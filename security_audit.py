import logging
import os
import sys
import json
import subprocess
import tempfile
import ast # Required for analyze_file and check_missing_permissions
import datetime # Required for dynamic log file naming
import re
from collections import defaultdict

# --- Configure logging to console and a file ---
# Define a dynamic log file path based on a timestamp
log_file_path = f"security_audit_log_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s', # Include timestamp in log format
    handlers=[
        logging.StreamHandler(sys.stdout), # Keep console output
        logging.FileHandler(log_file_path) # Add file output
    ]
)
logging.info(f"All Python logging output will also be written to: {log_file_path}")


class SecurityAuditor:
    def __init__(self, config, project_root, backend_dir, frontend_dir):
        self.config = config
        self.project_root = project_root
        self.backend_dir = backend_dir
        self.frontend_dir = frontend_dir
        self.findings = [] # This list will store your audit findings
        # Define permission decorators relevant to your Flask application
        self.permission_decorators = {
            'login_required', 'b2b_user_required', 'staff_required',
            'admin_required', 'roles_required', 'permissions_required',
            'b2b_admin_required', 'jwt_required'
        }

    def _print_header(self, text):
        """Prints a styled header for audit steps."""
        logging.info(f"\n--- {text} ---")

    def add_finding(self, severity, category, title, description, file_path, line_number, recommendation=None, code_snippet=None, cwe_id=None):
        """Adds a new security finding to the auditor's list."""
        finding = {
            'severity': severity,
            'category': category,
            'title': title,
            'description': description,
            'file_path': file_path,
            'line_number': line_number,
            'recommendation': recommendation,
            'code_snippet': code_snippet,
            'cwe_id': cwe_id
        }
        self.findings.append(finding)
        logging.info(f"NEW FINDING: {title} in {file_path}:{line_number} (Severity: {severity})")

    def _run_command(self, cmd_parts, cwd=None, env=None, stdout_target=subprocess.PIPE, stderr_target=subprocess.PIPE):
        """
        Helper to run a command, capturing stdout and stderr.
        It returns a tuple: (stdout_str, return_code).
        Warnings/errors printed to stderr by the command are logged separately.
        Does NOT raise CalledProcessError by default.
        """
        try:
            # Add a timeout to prevent the script from hanging indefinitely.
            # 3 minutes should be more than enough for these tools.
            process = subprocess.run(
                cmd_parts,
                stdout=stdout_target,
                stderr=stderr_target,
                text=True,
                check=False,
                encoding='utf-8',
                cwd=cwd,
                env=env,
                timeout=180
            )
            
            if stderr_target == subprocess.PIPE and process.stderr:
                logging.warning(f"Command '{' '.join(cmd_parts)}' produced stderr:\n{process.stderr.strip()}")

            stdout_content = process.stdout if stdout_target == subprocess.PIPE else ""
            return stdout_content, process.returncode

        except subprocess.TimeoutExpired as e:
            logging.error(f"Command '{' '.join(cmd_parts)}' timed out after 180 seconds. This can happen due to network issues or if the tool is unresponsive.")
            # Log any partial output that was captured
            if e.stdout:
                logging.error(f"Partial STDOUT from timed-out command:\n{e.stdout}")
            if e.stderr:
                logging.error(f"Partial STDERR from timed-out command:\n{e.stderr}")
            return None, 1
        except FileNotFoundError:
            logging.error(f"Command not found: '{cmd_parts[0]}'. Please ensure it's in your PATH.")
            return None, 1
        except Exception as e:
            logging.error(f"An unexpected error occurred while running command '{' '.join(cmd_parts)}': {e}")
            return None, 1

    def _find_files(self, directory, extensions, exclude_dirs=None):
        """Helper to find all files with given extensions in a directory, excluding specified subdirectories."""
        if exclude_dirs is None:
            exclude_dirs = []
    
        all_exclude_dirs = exclude_dirs + ['website/node_modules']
        exclude_paths = {os.path.join(self.project_root, d) for d in all_exclude_dirs}
        
        matches = []
        for root, dirs, filenames in os.walk(directory):
            # Modify dirs in-place to skip the excluded directories.
            # This now checks against the pre-built set for better performance.
            dirs[:] = [d for d in dirs if os.path.join(root, d) not in exclude_paths]
            
            for filename in filenames:
                if any(filename.endswith(ext) for ext in extensions):
                    matches.append(os.path.join(root, filename))
        return matches
        
    def analyze_file(self, file_path):
        """Analyzes a single Python file for various security issues using AST."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse the file content into an AST
            tree = ast.parse(content, filename=file_path)
            
            # Call various check methods, passing the AST and other relevant data
            self.check_missing_permissions(file_path, tree)
            # Add other AST-based checks here as needed

        except FileNotFoundError:
            logging.error(f"File not found: {file_path}")
        except SyntaxError as e:
            logging.error(f"Syntax error in {file_path}: {e}")
        except Exception as e:
            logging.error(f"Error analyzing {file_path}: {e}")

    def run_codeql_scan(source_code_path, output_sarif_path, database_path):
        """
        Runs a CodeQL scan on the specified source code path.
    
        Args:
            source_code_path (str): The path to the source code to be scanned (e.g., './backend').
            output_sarif_path (str): The path to save the SARIF results (e.g., 'codeql_audit_results.sarif').
            database_path (str): The path to store the CodeQL database (e.g., 'codeql_db_python').
    
        Returns:
            bool: True if the CodeQL scan completes successfully, False otherwise.
        """
        logger.info(f"Starting CodeQL scan for {source_code_path}...")
    
        # Clean up previous database if it exists
        if os.path.exists(database_path):
            logger.info(f"Removing existing CodeQL database at {database_path}...")
            try:
                # Use shutil.rmtree for directory removal if available, or subprocess 'rm -rf'
                subprocess.run(['rm', '-rf', database_path], check=True, capture_output=True, text=True)
                logger.info("Existing CodeQL database removed.")
            except subprocess.CalledProcessError as e:
                logger.error(f"Failed to remove existing CodeQL database: {e.stderr}")
                return False
    
        # 1. Create CodeQL database
        logger.info(f"Creating CodeQL database at {database_path} for language Python...")
        create_db_command = [
            "codeql", "database", "create", database_path,
            f"--source-root={source_code_path}",
            "--language=python"
        ]
        try:
            # Using shell=True for simpler command execution, but be mindful of security implications
            # if input comes from untrusted sources. For a local audit script, it's generally acceptable.
            process = subprocess.run(create_db_command, check=True, capture_output=True, text=True, shell=False)
            logger.info(f"CodeQL database creation stdout:\n{process.stdout}")
            logger.info("CodeQL database created successfully.")
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to create CodeQL database. Stderr:\n{e.stderr}")
            return False
        except FileNotFoundError:
            logger.error("CodeQL CLI not found. Please ensure 'codeql' is in your system's PATH.")
            return False
    
        # 2. Run CodeQL analysis
        logger.info(f"Running CodeQL analysis on database {database_path}...")
        # Use standard Python security queries. You can customize this or add more QLS files.
        analyze_command = [
            "codeql", "database", "analyze", database_path,
            "python-security-and-quality.qls", # Standard Python security and quality queries
            "--format=sarif-latest",
            f"--output={output_sarif_path}"
        ]
        try:
            process = subprocess.run(analyze_command, check=True, capture_output=True, text=True, shell=False)
            logger.info(f"CodeQL analysis stdout:\n{process.stdout}")
            logger.info(f"CodeQL analysis completed. Results saved to {output_sarif_path}")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to run CodeQL analysis. Stderr:\n{e.stderr}")
            return False
    
    def process_codeql_results(sarif_file_path):
        """
        Processes CodeQL SARIF results and logs relevant findings.
    
        Args:
            sarif_file_path (str): The path to the SARIF results file.
        """
        if not os.path.exists(sarif_file_path):
            logger.warning(f"CodeQL SARIF file not found: {sarif_file_path}")
            return
    
        logger.info(f"Processing CodeQL results from {sarif_file_path}...")
        try:
            with open(sarif_file_path, 'r') as f:
                sarif_data = json.load(f)
    
            if "runs" in sarif_data:
                for run in sarif_data["runs"]:
                    if "results" in run:
                        if not run["results"]:
                            logger.info("No findings reported by CodeQL for this run.")
                        for result in run["results"]:
                            rule_id = result.get("ruleId", "N/A")
                            message = result["message"]["text"]
                            location = "N/A"
                            if "locations" in result and result["locations"]:
                                physical_location = result["locations"][0].get("physicalLocation")
                                if physical_location:
                                    artifact_location = physical_location.get("artifactLocation")
                                    region = physical_location.get("region")
                                    if artifact_location and "uri" in artifact_location:
                                        # Convert file URI to a more readable path if necessary
                                        location = artifact_location["uri"].replace("file://", "")
                                    if region and "startLine" in region:
                                        location += f":{region['startLine']}"
                                    if "startColumn" in region:
                                        location += f":{region['startColumn']}"
    
                            severity = result.get("level", "note") # 'error', 'warning', 'note'
                            logger.info(f"CodeQL Finding ({severity.upper()}): Rule={rule_id}, Message='{message}', Location={location}")
                    else:
                        logger.info("No results array found in CodeQL SARIF run.")
            else:
                logger.info("No 'runs' array found in CodeQL SARIF data.")
    
        except json.JSONDecodeError:
            logger.error(f"Error decoding JSON from CodeQL SARIF file: {sarif_file_path}. Is it a valid SARIF file?")
        except Exception as e:
            logger.error(f"An unexpected error occurred while processing CodeQL results: {e}")
    



def run_sonarqube_scan(project_base_dir, project_key, organization=None, sonar_url="http://localhost:9000", token=None):
    """
    Runs a SonarQube scan on the specified project directory.

    Args:
        project_base_dir (str): The base directory of the project to scan.
        project_key (str): The SonarQube project key.
        organization (str, optional): The SonarQube organization key (if using SonarCloud).
        sonar_url (str): The URL of your SonarQube server.
        token (str, optional): Your SonarQube authentication token.

    Returns:
        bool: True if the scan completes successfully, False otherwise.
    """
    logger.info(f"Starting SonarQube scan for project {project_key} in {project_base_dir}...")

    # Sonar Scanner command construction
    command = ["sonar-scanner"]

    # Add mandatory properties
    command.append(f"-Dsonar.projectKey={project_key}")
    command.append(f"-Dsonar.sources={project_base_dir}")
    command.append(f"-Dsonar.host.url={sonar_url}")

    # Add optional properties
    if organization:
        command.append(f"-Dsonar.organization={organization}")
    if token:
        command.append(f"-Dsonar.token={token}")

    logger.info(f"Executing SonarQube command: {' '.join(command)}")

    try:
        # SonarQube scanner often prints to stderr for progress, so capture_output might hide useful info
        # It's better to let it print to console and just check the return code.
        process = subprocess.run(command, check=True, text=True, shell=False)
        logger.info("SonarQube scan completed successfully.")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"SonarQube scan failed. Error:\n{e.stderr}\nOutput:\n{e.stdout}")
        logger.error("Please ensure SonarQube server is running and 'sonar-scanner' is in your PATH.")
        return False
    except FileNotFoundError:
        logger.error("SonarQube Scanner CLI ('sonar-scanner') not found. Please ensure it is installed and in your system's PATH.")
        return False


    def run_semgrep_scan(target_path, output_json_path, config_path="auto"):
        """
        Runs a Semgrep scan on the specified path with a given configuration.
    
        Args:
            target_path (str): The file or directory to scan.
            output_json_path (str): The path to save the JSON results.
            config_path (str): The Semgrep configuration (e.g., 'p/python', 'p/vuejs', or a local path to rules).
    
        Returns:
            bool: True if the scan completes successfully, False otherwise.
        """
        logger.info(f"Starting Semgrep scan for {target_path} with config '{config_path}'...")
    
        command = [
            "semgrep",
            f"--config={config_path}",
            f"--output={output_json_path}",
            "--json",
            target_path
        ]
    
        try:
            # Semgrep exits with 0 even if findings are present, only non-zero on error.
            process = subprocess.run(command, check=False, capture_output=True, text=True, shell=False)
    
            if process.returncode != 0:
                logger.error(f"Semgrep scan failed with exit code {process.returncode}. Stderr:\n{process.stderr}")
                return False
    
            logger.info(f"Semgrep scan completed. Results saved to {output_json_path}")
            # Log stdout/stderr for debugging even on success, as warnings might be there
            if process.stdout:
                logger.debug(f"Semgrep stdout:\n{process.stdout}")
            if process.stderr:
                logger.debug(f"Semgrep stderr:\n{process.stderr}")
    
            return True
        except FileNotFoundError:
            logger.error("Semgrep CLI not found. Please ensure 'semgrep' is installed and in your system's PATH.")
            return False
        except Exception as e:
            logger.error(f"An unexpected error occurred during Semgrep scan: {e}")
            return False
    
    def process_semgrep_results(json_file_path):
        """
        Processes Semgrep JSON results and logs relevant findings.
    
        Args:
            json_file_path (str): The path to the Semgrep JSON results file.
        """
        if not os.path.exists(json_file_path):
            logger.warning(f"Semgrep JSON file not found: {json_file_path}")
            return
    
        logger.info(f"Processing Semgrep results from {json_file_path}...")
        try:
            with open(json_file_path, 'r') as f:
                semgrep_data = json.load(f)
    
            if "results" in semgrep_data:
                if not semgrep_data["results"]:
                    logger.info("No findings reported by Semgrep for this run.")
                for result in semgrep_data["results"]:
                    check_id = result.get("check_id", "N/A")
                    message = result.get("extra", {}).get("message", "No message provided.")
                    path = result.get("path", "N/A")
                    start_line = result.get("start", {}).get("line", "N/A")
                    severity = result.get("extra", {}).get("severity", "UNKNOWN")
    
                    location = f"{path}:{start_line}"
    
                    logger.info(f"Semgrep Finding ({severity}): ID={check_id}, Message='{message}', Location={location}")
            else:
                logger.info("No 'results' array found in Semgrep JSON data.")
    
        except json.JSONDecodeError:
            logger.error(f"Error decoding JSON from Semgrep file: {json_file_path}. Is it a valid JSON file?")
        except Exception as e:
            logger.error(f"An unexpected error occurred while processing Semgrep results: {e}")


    
    def check_missing_permissions(self, file_path, tree):
        """
        Vérifie les routes Flask pour les permissions manquantes en utilisant l'AST.
        C'est une méthode beaucoup plus fiable que l'analyse textuelle.
        """
        for node in ast.walk(tree):
            if not isinstance(node, ast.FunctionDef):
                continue

            # Vérifie si la fonction est une route Flask
            is_route = any(
                isinstance(d, ast.Call) and isinstance(d.func, ast.Attribute) and d.func.attr == 'route'
                for d in node.decorator_list
            )

            if not is_route:
                continue

            # Vérifie si un décorateur de permission est présent
            has_auth = False
            for decorator in node.decorator_list:
                decorator_name = ''
                if isinstance(decorator, ast.Name):
                    decorator_name = decorator.id
                elif isinstance(decorator, ast.Call) and isinstance(decorator.func, ast.Name):
                    decorator_name = decorator.func.id
                
                if decorator_name in self.permission_decorators:
                    has_auth = True
                    break
            
            if not has_auth:
                self.add_finding(
                    severity='HIGH',
                    category='Endpoint Missing Permissions',
                    title=f"L'endpoint '{node.name}' semble ne pas avoir de décorateur d'autorisation.",
                    description="This Flask endpoint does not appear to have any authorization decorator, which could lead to unauthorized access.",
                    file_path=file_path,
                    line_number=node.lineno,
                    recommendation="Ensure all Flask endpoints have appropriate authorization decorators (e.g., @login_required, @role_required)."
                    # code_snippet can be added here if 'content' is passed to this method
                )

    # --- Start of merged code from backend_code_scanner.py ---

    def run_code_integrity_scan(self):
        """Runs syntax checks and detects circular imports."""
        self._print_header("Backend Code Integrity (Syntax & Circular Imports)")

        backend_files = self._find_files(self.backend_dir, ['.py'], exclude_dirs=['website/node_modules'])
        if not backend_files:
            logging.warning("No Python files found in backend to scan for integrity.")
            return

        # 1. Syntax Check
        syntax_errors_found = False
        for file_path in backend_files:
            is_valid, error_msg = self._check_syntax(file_path)
            if not is_valid:
                syntax_errors_found = True
                self.add_finding(
                    severity='CRITICAL',
                    category='Code Integrity',
                    title='Syntax Error',
                    description=error_msg,
                    file_path=file_path,
                    line_number=0, # The error message contains the line number
                    recommendation="Fix the syntax error to allow the application to run."
                )
        if not syntax_errors_found:
            logging.info("Syntax check passed for all backend files.")

        # 2. Circular Import Check
        dependency_graph = self._build_dependency_graph(backend_files)
        circular_imports = self._find_circular_imports(dependency_graph)

        if circular_imports:
            for i, cycle in enumerate(circular_imports):
                cycle_path = ' ->\n    '.join(cycle)
                self.add_finding(
                    severity='HIGH',
                    category='Code Integrity',
                    title=f'Circular Import Detected (Cycle {i+1})',
                    description=f"A circular import dependency was found. This can lead to runtime errors and difficult-to-maintain code.",
                    file_path=cycle[0].replace('.', '/') + '.py', # Best guess for file path
                    line_number=1,
                    code_snippet=cycle_path,
                    recommendation="Refactor the code to break the import cycle. This often involves moving models, creating service locators, or using local imports within functions."
                )
        else:
            logging.info("No circular imports detected.")

    def _check_syntax(self, file_path):
        """Vérifie la syntaxe d'un fichier Python en utilisant AST."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source_code = f.read()
                ast.parse(source_code, filename=file_path)
            return True, None
        except SyntaxError as e:
            return False, f"Syntax error in {file_path} at line {e.lineno}: {e.msg}"
        except Exception as e:
            return False, f"Unexpected error while parsing {file_path}: {e}"

    def _build_dependency_graph(self, python_files):
        """Builds a dependency graph from a list of Python files."""
        dependency_graph = defaultdict(set)
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    source = f.read()
                    tree = ast.parse(source, filename=file_path)
                    visitor = self._DependencyVisitor(file_path)
                    visitor.visit(tree)
                    
                    module_name = visitor.current_module_name
                    internal_deps = {dep for dep in visitor.dependencies if dep.startswith(os.path.basename(self.backend_dir))}
                    if internal_deps:
                        dependency_graph[module_name].update(internal_deps)
            except Exception as e:
                logging.error(f"Could not analyze dependencies for {file_path}: {e}")
        return dependency_graph

    def _find_circular_imports(self, dependency_graph):
        """Finds circular imports in a dependency graph using DFS."""
        cycles = []
        path = set()
        visited = set()

        def visit(node):
            if node in visited:
                return
            path.add(node)
            visited.add(node)
            for neighbour in dependency_graph.get(node, []):
                if neighbour in path:
                    try:
                        cycle_start_index = list(path).index(neighbour)
                        cycle = list(path)[cycle_start_index:] + [neighbour]
                        sorted_cycle = tuple(sorted(cycle[:-1]))
                        if sorted_cycle not in [tuple(sorted(c[:-1])) for c in cycles]:
                            cycles.append(cycle)
                    except ValueError:
                        cycles.append(list(path) + [neighbour])
                visit(neighbour)
            path.remove(node)

        for node in list(dependency_graph.keys()):
            visit(node)
        return cycles

    class _DependencyVisitor(ast.NodeVisitor):
        """AST visitor to find all import statements."""
        def __init__(self, current_module_path):
            self.dependencies = set()
            self.current_module_path = current_module_path
            self.current_module_name = self._path_to_module(current_module_path)

        def _path_to_module(self, path):
            path = os.path.splitext(path)[0]
            return path.replace(os.path.sep, '.')
            
        def visit_Import(self, node):
            for alias in node.names:
                self.dependencies.add(alias.name)
            self.generic_visit(node)

        def visit_ImportFrom(self, node):
            module_name = node.module
            if node.level > 0:
                parts = self.current_module_name.split('.')
                base_path = '.'.join(parts[:-(node.level)])
                if module_name:
                    module_name = f"{base_path}.{module_name}"
                else:
                    module_name = base_path
            if module_name:
                self.dependencies.add(module_name)
            self.generic_visit(node)
    # --- End of merged code from backend_code_scanner.py ---

    def run_safety_scan(self):
        """Runs Safety to check for backend dependency vulnerabilities."""
        self._print_header("Backend Dependency Scan (Safety)")
        logging.info("This scan may take a moment as it might need to fetch the latest vulnerability database...")
        req_file = os.path.join(self.backend_dir, 'requirements.txt')
        if not os.path.exists(req_file):
            logging.warning(f"Could not find requirements.txt at '{self.backend_dir}'. Skipping Safety scan.")
            return

        command = [sys.executable, '-m', 'safety', 'scan', f'--file={req_file}', '--json']
        output, _ = self._run_command(command)
        if not output:
            logging.error("Safety command could not be run or produced no output.")
            return

        try:
            report = json.loads(output)
            for vuln_id, vuln_data in report.get('vulnerabilities', {}).items():
                self.add_finding(
                    severity="HIGH",
                    category="Dependency Vulnerability (Safety)",
                    title=f"Vulnerable package: {vuln_data.get('package_name')} ({vuln_data.get('analyzed_version')})",
                    description=f"ID: {vuln_id}. {vuln_data.get('advisory')}",
                    file_path=req_file,
                    line_number=1,
                    recommendation=f"Upgrade to a version > {vuln_data.get('vulnerable_version')}. Fixed in: {vuln_data.get('fixed_versions')}",
                    cwe_id=vuln_id
                )
            logging.info(f"Safety scan found {len(report.get('vulnerabilities', {}))} vulnerabilities.")
        except json.JSONDecodeError as e:
            logging.error(f"Could not decode Safety JSON output: {e}")

    def run_pip_audit(self):
        """Runs pip-audit to check for backend dependency vulnerabilities using a temporary file for the report."""
        if self.config.skip_dependency_check:
            logging.info("Skipping pip-audit as per configuration.")
            return
            
        self._print_header("Backend Dependency Scan (pip-audit)")
        req_file = os.path.join(self.backend_dir, 'requirements.txt')
        if not os.path.exists(req_file):
            req_file = os.path.join(self.project_root, 'requirements.txt')
            if not os.path.exists(req_file):
                logging.warning(f"Could not find requirements.txt at '{self.backend_dir}' or '{self.project_root}'. Skipping pip-audit.")
                return
    
        # --- CHANGE START ---
        # Use a temporary file for reliable JSON output.
        with tempfile.NamedTemporaryFile(mode='w+', delete=False, encoding='utf-8', suffix=".json") as tmp_file:
            report_filename = tmp_file.name
    
        try:
            # Command to write the JSON report directly to a file.
            command = [
                sys.executable, '-m', 'pip_audit',
                '-r', req_file,
                '-f', 'json',
                '-o', report_filename
            ]
            
            self._run_command(command)
            
            # Read the report from the temporary file.
            with open(report_filename, 'r', encoding='utf-8') as f:
                try:
                    report = json.load(f)
                except json.JSONDecodeError:
                    logging.error(f"pip-audit ran, but its output at {report_filename} was not valid JSON. Please inspect the file.")
                    return
    
            if 'vulnerabilities' in report and report['vulnerabilities']:
                logging.info(f"pip-audit found {len(report['vulnerabilities'])} vulnerabilities.")
                # Read requirements file to find line numbers.
                with open(req_file, 'r', encoding='utf-8') as f_req:
                    req_lines = f_req.readlines()
    
                for vuln_data in report['vulnerabilities']:
                    package_name = vuln_data.get('name', 'N/A')
                    package_version = vuln_data.get('version', 'N/A')
                    vuln_id = vuln_data.get('id', 'N/A')
                    description = vuln_data.get('details', 'No description provided.')
                    fixed_versions = ', '.join(vuln_data.get('fix_versions', ['N/A']))
    
                    # Find the line number for the vulnerable package.
                    line_number = "N/A"
                    for i, line in enumerate(req_lines):
                        if package_name.lower() in line.lower():
                            line_number = i + 1
                            break
    
                    self.add_finding(
                        severity="HIGH", # All dependency issues are treated as high priority.
                        category="Dependency Vulnerability (pip-audit)",
                        title=f"Vulnerable package: {package_name}=={package_version}",
                        description=f"Vulnerability ID: {vuln_id}. Details: {description}",
                        file_path=req_file,
                        line_number=line_number,
                        recommendation=f"Upgrade to a fixed version, e.g.,: {fixed_versions}",
                    )
            else:
                logging.info("pip-audit completed with no vulnerabilities found.")
    
        finally:
            # Clean up the temporary file.
            if os.path.exists(report_filename):
                os.remove(report_filename)
                
    def run_npm_audit(self):
        """Runs npm audit to check for frontend dependency vulnerabilities."""
        if self.config.skip_dependency_check:
            logging.info("Skipping npm audit as per configuration.")
            return

        self._print_header("Frontend Dependency Scan (npm audit)")
        
        if not os.path.isdir(self.frontend_dir):
            logging.warning(f"Frontend directory '{self.frontend_dir}' not found. Skipping npm audit.")
            return

        npm_cmd = ['npm', 'audit', '--json']

        output_str, return_code = self._run_command(npm_cmd, cwd=self.frontend_dir)
        
        if output_str is None:
            logging.error("npm audit command could not be run or produced no output.")
            return

        try:
            report = json.loads(output_str)

            vulnerabilities_found = 0
            if 'advisories' in report:
                for advisory_id, advisory_data in report['advisories'].items():
                    self.add_finding(
                        severity=advisory_data.get('severity', 'UNKNOWN').upper(),
                        category="Dependency Vulnerability (npm)",
                        title=advisory_data.get('title', 'N/A'),
                        description=advisory_data.get('overview', 'No overview provided.') + f"\nMore info: {advisory_data.get('url', 'N/A')}",
                        file_path=os.path.join(self.frontend_dir, 'package.json'),
                        line_number=1,
                        recommendation=f"Upgrade: {advisory_data.get('fixString', 'Manual fix needed.')}",
                        cwe_id=advisory_id
                    )
                    vulnerabilities_found += 1
            elif 'vulnerabilities' in report and report['vulnerabilities']:
                for pkg_name, pkg_data in report['vulnerabilities'].items():
                    for vuln_info in pkg_data.get('via', []):
                        if isinstance(vuln_info, dict):
                            self.add_finding(
                                severity=vuln_info.get('severity', 'UNKNOWN').upper(),
                                category="Dependency Vulnerability (npm)",
                                title=f"Vulnerable package: {pkg_name}",
                                description=f"{vuln_info.get('title', 'N/A')}. {vuln_info.get('url', 'N/A')}",
                                file_path=os.path.join(self.frontend_dir, 'package.json'),
                                line_number=1,
                                recommendation=f"Affected versions: {vuln_info.get('range', 'N/A')}. Fix: npm audit fix",
                                cwe_id=vuln_info.get('id', 'N/A')
                            )
                            vulnerabilities_found += 1

            if vulnerabilities_found > 0:
                logging.info(f"npm audit found {vulnerabilities_found} vulnerabilities.")
            else:
                logging.info("npm audit completed with no vulnerabilities found.")

            if return_code != 0 and vulnerabilities_found == 0:
                logging.warning(f"npm audit exited with non-zero code ({return_code}) but reported no vulnerabilities in its JSON output or parsing failed. Check stderr logs for details.")

        except json.JSONDecodeError as e:
            logging.error(f"Could not decode npm audit JSON output. Error: {e}")
            logging.error(f"Raw npm audit output that failed to decode (first 500 chars):\n{output_str[:500]}...")
        except KeyError as e:
            logging.error(f"Missing expected key in npm audit JSON output: {e}. Ensure npm audit JSON format matches expectations.")
            logging.error(f"Problematic JSON (full output, if short enough): {output_str}")

    def run_bandit_scan(self):
        """Runs Bandit static analysis on the backend directory, writing the report to a file for stable parsing."""
        if self.config.skip_static_analysis:
            logging.info("Skipping Bandit scan as per configuration.")
            return
    
        self._print_header("Backend Security Scan (Bandit)")
        if not os.path.isdir(self.backend_dir):
            logging.warning(f"Backend directory '{self.backend_dir}' not found. Skipping Bandit scan.")
            return
    
        # --- CHANGE START ---
        # Use a temporary file for reliable JSON output and exclude the 'tests' directory.
        with tempfile.NamedTemporaryFile(mode='w+', delete=False, encoding='utf-8', suffix=".json") as tmp_file:
            report_filename = tmp_file.name
    
        try:
            # Define the Bandit command with the output file and exclusions.
            bandit_cmd = [
                sys.executable, '-m', 'bandit',
                '-r', self.backend_dir,
                '-f', 'json',
                '-o', report_filename, # Write JSON output directly to a file.
                '-x', 'tests'  # Exclude the tests directory.
            ]
    
            # Run the command. We don't need to capture stdout/stderr as output goes to the file.
            self._run_command(bandit_cmd)
    
            # Read the JSON report from the file.
            with open(report_filename, 'r', encoding='utf-8') as f:
                try:
                    report = json.load(f)
                except json.JSONDecodeError:
                    logging.error(f"Bandit ran, but its output at {report_filename} was not valid JSON. Please inspect the file.")
                    return # Can't proceed without a valid report
    
            # Process the results from the report.
            if 'results' in report and report['results']:
                logging.info(f"Bandit scan found {len(report['results'])} issues.")
                for issue in report['results']:
                    # Format the finding details from the issue.
                    test_name = issue.get('test_name', 'N/A')
                    confidence = issue.get('issue_confidence', 'UNKNOWN').upper()
                    more_info_url = issue.get('more_info', 'N/A')
                    line_number = issue.get('line_number', 'N/A')
    
                    description = (
                        f"Bandit Test: {test_name} ({issue.get('test_id', 'N/A')})\n"
                        f"Confidence: {confidence}\n"
                        f"This was flagged by Bandit, a static analysis tool for finding common security issues."
                    )
                    recommendation = f"Review the issue and guidance at: {more_info_url}"
    
                    # Format the code snippet with line numbers.
                    code_lines = issue.get('code', '').split('\n')
                    start_line = issue.get('line_range', [line_number])[0]
                    formatted_code = "\n".join(
                        f"{start_line + i: >4}: {line}" for i, line in enumerate(code_lines)
                    )
    
                    self.add_finding(
                        severity=issue.get('issue_severity', 'UNKNOWN').upper(),
                        category="Static Analysis (Bandit)",
                        title=issue.get('issue_text', 'No issue description provided'),
                        description=description,
                        file_path=issue.get('filename', 'N/A'),
                        line_number=line_number,
                        code_snippet=formatted_code,
                        recommendation=recommendation
                    )
            else:
                logging.info("Bandit scan completed with no security issues found.")
    
        finally:
            # Clean up the temporary file.
            if os.path.exists(report_filename):
                os.remove(report_filename)
                
    def run_pylint_scan(self):
        """Runs Pylint static analysis on the backend directory and parses the JSON output."""
        self._print_header("Backend Code Linting (Pylint)")
        if not os.path.isdir(self.backend_dir):
            logging.warning(f"Backend directory '{self.backend_dir}' not found. Skipping Pylint scan.")
            return

        # Using a temporary file for JSON output is more robust
        with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix=".json", encoding='utf-8') as tmp_file:
            pylint_output_file = tmp_file.name

        pylint_cmd = [
            sys.executable, '-m', 'pylint',
            self.backend_dir,
            '--output-format=json'
        ]

        # Run Pylint and direct its JSON output to the temp file
        # We capture stderr to see any Pylint configuration errors
        _, return_code = self._run_command(pylint_cmd, stdout_target=open(pylint_output_file, 'w'), stderr_target=subprocess.PIPE)

        if not os.path.exists(pylint_output_file) or os.path.getsize(pylint_output_file) == 0:
            logging.error(f"Pylint did not generate an output file at {pylint_output_file}. Pylint might have crashed. Check stderr logs.")
            os.remove(pylint_output_file)
            return

        try:
            with open(pylint_output_file, 'r', encoding='utf-8') as f:
                report = json.load(f)

            if not report:
                logging.info("Pylint scan completed with no issues found.")
                return

            # Map Pylint message types to our severity levels
            severity_map = {
                'fatal': 'CRITICAL', 'error': 'HIGH', 'warning': 'MEDIUM',
                'convention': 'LOW', 'refactor': 'LOW',
            }

            for issue in report:
                self.add_finding(
                    severity=severity_map.get(issue.get('type', 'convention'), 'LOW'),
                    category="Code Quality (Pylint)",
                    title=f"{issue.get('symbol')} ({issue.get('message-id')})",
                    description=issue.get('message', 'No message provided.'),
                    file_path=issue.get('path', 'N/A'),
                    line_number=issue.get('line', 0),
                    code_snippet=f"Module: {issue.get('module')}, Object: {issue.get('obj')}",
                    recommendation=f"Review Pylint rule {issue.get('message-id')} for best practices."
                )
            logging.info(f"Pylint scan found {len(report)} issues.")
        except (json.JSONDecodeError, Exception) as e:
            logging.error(f"An unexpected error occurred while parsing Pylint report from {pylint_output_file}: {e}")
        finally:
            os.remove(pylint_output_file)

    def run_mypy_scan(self):
        """Runs Mypy for static type checking and parses the output."""
        self._print_header("Backend Static Type Checking (Mypy)")
        if not os.path.isdir(self.backend_dir):
            logging.warning(f"Backend directory '{self.backend_dir}' not found. Skipping Mypy scan.")
            return

        # Mypy command. --ignore-missing-imports is useful to avoid errors from libs without type stubs.
        mypy_cmd = [
            sys.executable, '-m', 'mypy',
            self.backend_dir,
            '--ignore-missing-imports'
        ]

        output, return_code = self._run_command(mypy_cmd)

        if return_code == 0 or not output:
            logging.info("Mypy scan completed with no type errors found.")
            return

        # Regex to parse Mypy's default output format.
        # e.g., "path/to/file.py:123: error: Your error message here  [error-code]"
        mypy_pattern = re.compile(r"([^:]+):(\d+): (error|note): (.+)")
        
        issues_found = 0
        for line in output.strip().split('\n'):
            match = mypy_pattern.match(line)
            if match:
                issues_found += 1
                file_path, line_number, severity, description = match.groups()
                self.add_finding(
                    severity='HIGH',  # All Mypy errors are considered high severity for code correctness.
                    category="Static Type Checking (Mypy)",
                    title="Type Error",
                    description=description.strip(),
                    file_path=file_path.strip(),
                    line_number=int(line_number),
                    recommendation="Fix the type hint or the code that violates it to ensure type safety."
                )
        
        if issues_found > 0:
            logging.info(f"Mypy scan found {issues_found} type errors.")
        else:
            # This can happen if mypy exits with an error code but parsing fails.
            logging.warning("Mypy exited with a non-zero status but no issues could be parsed from its output.")


    def run_best_practices_audit(self):
        """Runs various best practice checks from the best_practices_audit.py script."""
        self._print_header("Best Practices Audit")
        all_files = self._find_files(self.project_root, ['.py', '.js', '.vue', '.css', '.scss'], exclude_dirs=['website/node_modules'])
        
        for file_path in all_files:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # Check for hardcoded secrets
                secret_keywords = ['password', 'secret', 'api_key', 'token']
                if any(keyword in content.lower() for keyword in secret_keywords):
                    for i, line in enumerate(content.splitlines(), 1):
                        if any(keyword in line.lower() for keyword in secret_keywords) and ('=' in line):
                            if not (line.strip().startswith('#') or 'secret_key' in line):
                                self.add_finding(
                                    severity='HIGH', category='Security', title='Potential Hardcoded Secret',
                                    description=f"Line contains a keyword that might indicate a hardcoded secret.",
                                    file_path=file_path, line_number=i, code_snippet=line.strip(),
                                    recommendation="Store secrets in environment variables or a secure vault, not in code."
                                )

                # Check for insecure HTTP URLs
                http_patterns = [r'http://(?!localhost|127\.0\.0\.1|0\.0\.0\.0)']
                for pattern in http_patterns:
                    for match in re.finditer(pattern, content, re.IGNORECASE):
                        line_num = content.count('\n', 0, match.start()) + 1
                        self.add_finding(
                            severity="HIGH", category="HTTPS", title="Insecure HTTP URL",
                            description=f"Insecure HTTP URL found: {match.group()}",
                            file_path=file_path, line_number=line_num,
                            recommendation="Use HTTPS for all external connections."
                        )

                # Check for bare except clauses
                bare_except_pattern = r'except\s*:'
                for match in re.finditer(bare_except_pattern, content):
                    line_num = content.count('\n', 0, match.start()) + 1
                    self.add_finding(
                        severity="MEDIUM", category="Error Handling", title="Bare Except Clause",
                        description="Bare except clause catches all exceptions, which can hide bugs.",
                        file_path=file_path, line_number=line_num,
                        recommendation="Catch specific exceptions instead of using a bare except."
                    )

            except Exception as e:
                logging.warning(f"Could not process file {file_path} for best practices audit: {e}")

        logging.info("Best practices audit checks completed.")


    def run_audit(self):
        """Orchestrates the full suite of security and best practices audits."""
        self._print_header("STARTING COMPREHENSIVE SECURITY AUDIT")

        # Run backend dependency scan (pip-audit)
        self.run_pip_audit()

        # Run frontend dependency scan (npm audit)
        self.run_npm_audit()
        
        # Run another backend dependency scan (safety)
        self.run_safety_scan()

        # Run static security analysis (Bandit)
        self.run_bandit_scan()
    
        # checks for type errors (Static Type Checking)
        self.run_mypy_scan()
        
        # Run Pylint scan for code quality and potential bugs
        self.run_pylint_scan()

        # Run code integrity checks (syntax, circular imports)
        self.run_code_integrity_scan()

        # Run best practices audit
        self.run_best_practices_audit()

        # Add other audit steps here as needed
        # Example: self.run_code_linting()
        # Example: self.run_code_formatting_checks()

        self._print_header("AUDIT SUMMARY")
        if self.findings:
            # Sort findings by severity (assuming severity_order is defined elsewhere or in __init__)
            severity_order = {'HIGH': 1, 'MEDIUM': 2, 'LOW': 3, 'UNKNOWN': 4, 'UNDEFINED': 5}
            # Ensure 'severity' key exists in finding dictionary before sorting
            self.findings.sort(key=lambda f: severity_order.get(f.get('severity', 'UNKNOWN'), 99))
            
            logging.info(f"Found {len(self.findings)} potential issues:")
            for i, finding in enumerate(self.findings):
                logging.info(f"  {i+1}. [{finding.get('severity', 'UNKNOWN')}] {finding.get('title', 'No Title')}")
                logging.info(f"      Category: {finding.get('category', 'N/A')}")
                logging.info(f"      File: {finding.get('file_path', 'N/A')}:{finding.get('line_number', 'N/A')}")
                logging.info(f"      Description: {finding.get('description', 'N/A')}")
                if finding.get('recommendation'):
                    logging.info(f"      Recommendation: {finding['recommendation']}")
                if finding.get('code_snippet'):
                    logging.info(f"      Code Snippet:\n{finding['code_snippet']}")
                logging.info("-" * 20)
        else:
            logging.info("No issues found during the audit.")

        return len(self.findings)

if __name__ == "__main__":
    # This block allows the script to be run directly from the command line,
    # which is how it's called from `run_audits.sh`.

    # Define a simple default configuration for direct execution.
    # In a real application, this might come from command-line arguments.
    class SimpleConfig:
        skip_dependency_check = False
        skip_static_analysis = False

    config = SimpleConfig()

    project_root_backend = "./backend"
    project_root_frontend = "./website" # Assuming Vue.js frontend is in a 'website' directory

    # --- CodeQL Configuration ---
    codeql_sarif_output_file = "codeql_audit_results.sarif"
    codeql_database_dir = "codeql_db_for_flask"

    # --- SonarQube Configuration ---
    # IMPORTANT: Replace with your actual SonarQube/SonarCloud details
    # SonarQube requires a running SonarQube server or SonarCloud account.
    SONAR_PROJECT_KEY = "YourProjectKey" # e.g., "maison-truvra-backend"
    SONAR_ORGANIZATION = None # e.g., "your-sonarcloud-org" if using SonarCloud
    SONAR_HOST_URL = "http://localhost:9000" # Your SonarQube server URL
    SONAR_TOKEN = os.getenv("SONAR_TOKEN") # It's recommended to use environment variables for tokens

    # --- Semgrep Configuration ---
    semgrep_python_output = "semgrep_python_results.json"
    semgrep_vuejs_output = "semgrep_vuejs_results.json"
    # You can specify default rulesets ('auto', 'p/python', 'p/vuejs', 'p/ci', etc.)
    # or paths to local Semgrep rule files.
    SEMGREP_PYTHON_CONFIG = "p/python"
    SEMGREP_VUEJS_CONFIG = "p/vuejs" # Or more specific configs like 'p/javascript', 'p/html'

    logger.info("Starting all security audits...")

    # --- Run CodeQL Scan (for Python backend) ---
    logger.info("\n--- Initiating CodeQL Security Scan (Python Backend) ---")
    codeql_scan_successful = run_codeql_scan(
        source_code_path=project_root_backend,
        output_sarif_path=codeql_sarif_output_file,
        database_path=codeql_database_dir
    )
    if codeql_scan_successful:
        process_codeql_results(codeql_sarif_output_file)
    else:
        logger.error("CodeQL scan did not complete successfully. Check logs for details.")

    # --- Run SonarQube Scan (for entire project) ---
    logger.info("\n--- Initiating SonarQube Analysis ---")
    # You typically run SonarQube Scanner from the root of your entire project
    # for a full-stack analysis. Adjust project_base_dir as needed.
    sonarqube_scan_successful = run_sonarqube_scan(
        project_base_dir=".", # Scan the entire project directory
        project_key=SONAR_PROJECT_KEY,
        organization=SONAR_ORGANIZATION,
        sonar_url=SONAR_HOST_URL,
        token=SONAR_TOKEN
    )
    if sonarqube_scan_successful:
        logger.info("SonarQube scan results are available on your SonarQube dashboard.")
    else:
        logger.error("SonarQube scan did not complete successfully. Check logs for details and server status.")


    # --- Run Semgrep Scan (for Python Backend) ---
    logger.info("\n--- Initiating Semgrep Security Scan (Python Backend) ---")
    semgrep_python_successful = run_semgrep_scan(
        target_path=project_root_backend,
        output_json_path=semgrep_python_output,
        config_path=SEMGREP_PYTHON_CONFIG
    )
    if semgrep_python_successful:
        process_semgrep_results(semgrep_python_output)
    else:
        logger.error("Semgrep scan for Python backend did not complete successfully.")

    # --- Run Semgrep Scan (for Vue.js Frontend) ---
    logger.info("\n--- Initiating Semgrep Security Scan (Vue.js Frontend) ---")
    semgrep_vuejs_successful = run_semgrep_scan(
        target_path=project_root_frontend,
        output_json_path=semgrep_vuejs_output,
        config_path=SEMGREP_VUEJS_CONFIG # Use appropriate config for Vue.js/JS/TS
    )
    if semgrep_vuejs_successful:
        process_semgrep_results(semgrep_vuejs_output)
    else:
        logger.error("Semgrep scan for Vue.js frontend did not complete successfully.")

    
    # Determine project paths based on this script's location
    project_root = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.join(project_root, 'backend')
    frontend_dir = os.path.join(project_root, 'website')

    logging.info("Security audit script is being run directly.")

    # Instantiate and run the auditor
    auditor = SecurityAuditor(config, project_root, backend_dir, frontend_dir)
    num_findings = auditor.run_audit()

    # Exit with a non-zero status code if findings are present
    if num_findings > 0:
        sys.exit(1)
