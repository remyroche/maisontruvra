import logging
import os
import sys
import json
import subprocess
import tempfile
import ast
import datetime
import re
from collections import defaultdict

# --- Configure logging to console and a file ---
# Define a dynamic log file path based on a timestamp
log_file_path = f"logs/security_audit_log_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

# Ensure the 'logs' directory exists
os.makedirs(os.path.dirname(log_file_path), exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(log_file_path)
    ]
)
logger = logging.getLogger(__name__) # Get a logger instance
logger.info(f"All Python logging output will also be written to: {log_file_path}")


class SecurityAuditor:
    def __init__(self, config, project_root, backend_dir, frontend_dir):
        self.config = config
        self.project_root = project_root
        self.backend_dir = backend_dir
        self.frontend_dir = frontend_dir
        self.findings = []
        self.permission_decorators = {
            'login_required', 'b2b_user_required', 'staff_required',
            'admin_required', 'roles_required', 'permissions_required',
            'b2b_admin_required', 'jwt_required'
        }
        self.severity_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3, 'UNKNOWN': 4, 'NOTE': 5, 'WARNING': 6} # Added for sorting

        # Configuration for external tools (can be passed via config object or env vars)
        self.codeql_sarif_output_file = "codeql_audit_results.sarif"
        self.codeql_database_dir = "codeql_db_for_flask"
        self.sonar_project_key = config.get('SONAR_PROJECT_KEY', 'YourProjectKey')
        self.sonar_organization = config.get('SONAR_ORGANIZATION', None)
        self.sonar_host_url = config.get('SONAR_HOST_URL', 'http://localhost:9000')
        self.sonar_token = os.getenv("SONAR_TOKEN") # Always get from env for security
        self.semgrep_python_output = "semgrep_python_results.json"
        self.semgrep_vuejs_output = "semgrep_vuejs_results.json"
        self.semgrep_python_config = config.get('SEMGREP_PYTHON_CONFIG', 'p/python')
        self.semgrep_vuejs_config = config.get('SEMGREP_VUEJS_CONFIG', 'p/vuejs')


    def _print_header(self, text):
        """Prints a styled header for audit steps."""
        logger.info(f"\n--- {text} ---")

    def add_finding(self, severity, category, title, description, file_path, line_number, recommendation=None, code_snippet=None, cwe_id=None):
        """Adds a new security finding to the auditor's list."""
        finding = {
            'severity': severity.upper(), # Ensure uppercase for consistency
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
        logger.info(f"NEW FINDING: {title} in {file_path}:{line_number} (Severity: {severity.upper()})")

    def _run_command(self, cmd_parts, cwd=None, env=None, stdout_target=subprocess.PIPE, stderr_target=subprocess.PIPE):
        """
        Helper to run a command, capturing stdout and stderr.
        It returns a tuple: (stdout_str, return_code).
        Warnings/errors printed to stderr by the command are logged separately.
        Does NOT raise CalledProcessError by default.
        """
        try:
            process = subprocess.run(
                cmd_parts,
                stdout=stdout_target,
                stderr=stderr_target,
                text=True,
                check=False,
                encoding='utf-8',
                cwd=cwd,
                env=env,
                timeout=300 # Increased timeout to 5 minutes for potentially long scans
            )
            
            if stderr_target == subprocess.PIPE and process.stderr:
                # Log stderr as warning, unless it's a known non-error output (e.g., progress messages)
                logger.warning(f"Command '{' '.join(cmd_parts)}' produced stderr:\n{process.stderr.strip()}")

            stdout_content = process.stdout if stdout_target == subprocess.PIPE else ""
            return stdout_content, process.returncode

        except subprocess.TimeoutExpired as e:
            logger.error(f"Command '{' '.join(cmd_parts)}' timed out after {e.timeout} seconds. This can happen due to network issues or if the tool is unresponsive.")
            if e.stdout:
                logger.error(f"Partial STDOUT from timed-out command:\n{e.stdout}")
            if e.stderr:
                logger.error(f"Partial STDERR from timed-out command:\n{e.stderr}")
            return None, 1
        except FileNotFoundError:
            logger.error(f"Command not found: '{cmd_parts[0]}'. Please ensure it's in your PATH.")
            return None, 1
        except Exception as e:
            logger.error(f"An unexpected error occurred while running command '{' '.join(cmd_parts)}': {e}")
            return None, 1

    def _find_files(self, directory, extensions, exclude_dirs=None):
        """Helper to find all files with given extensions in a directory, excluding specified subdirectories."""
        if exclude_dirs is None:
            exclude_dirs = []
        
        # Ensure paths are relative to project_root if they are passed as absolute from os.walk
        # Or, ensure exclude_dirs are relative paths from the directory being walked.
        # For simplicity, let's assume exclude_dirs are relative to the directory passed to os.walk
        # and convert them to absolute paths for comparison.
        
        # Convert exclude_dirs to absolute paths for robust comparison
        abs_exclude_paths = {os.path.abspath(os.path.join(directory, d)) for d in exclude_dirs}
        
        matches = []
        for root, dirs, filenames in os.walk(directory):
            # Filter out excluded directories from the current level
            dirs[:] = [d for d in dirs if os.path.abspath(os.path.join(root, d)) not in abs_exclude_paths]
            
            for filename in filenames:
                if any(filename.endswith(ext) for ext in extensions):
                    matches.append(os.path.join(root, filename))
        return matches
        
    def analyze_file(self, file_path):
        """Analyzes a single Python file for various security issues using AST."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content, filename=file_path)
            
            self.check_missing_permissions(file_path, tree)
            # Add other AST-based checks here as needed

        except FileNotFoundError:
            logger.error(f"File not found: {file_path}")
        except SyntaxError as e:
            logger.error(f"Syntax error in {file_path}: {e}")
        except Exception as e:
            logger.error(f"Error analyzing {file_path}: {e}")

    def run_codeql_scan(self):
        """
        Runs a CodeQL scan on the Python backend.
        """
        self._print_header("CodeQL Security Scan (Python Backend)")
        source_code_path = self.backend_dir
        output_sarif_path = self.codeql_sarif_output_file
        database_path = self.codeql_database_dir

        logger.info(f"Starting CodeQL scan for {source_code_path}...")

        # Clean up previous database if it exists
        if os.path.exists(database_path):
            logger.info(f"Removing existing CodeQL database at {database_path}...")
            _, return_code = self._run_command(['rm', '-rf', database_path])
            if return_code != 0:
                logger.error(f"Failed to remove existing CodeQL database (exit code {return_code}).")
                return False
            logger.info("Existing CodeQL database removed.")

        # 1. Create CodeQL database
        logger.info(f"Creating CodeQL database at {database_path} for language Python...")
        create_db_command = [
            "codeql", "database", "create", database_path,
            f"--source-root={source_code_path}",
            "--language=python"
        ]
        _, return_code = self._run_command(create_db_command)
        if return_code != 0:
            logger.error(f"Failed to create CodeQL database (exit code {return_code}).")
            return False
        logger.info("CodeQL database created successfully.")

        # 2. Run CodeQL analysis
        logger.info(f"Running CodeQL analysis on database {database_path}...")
        analyze_command = [
            "codeql", "database", "analyze", database_path,
            "python-security-and-quality.qls", # Standard Python security and quality queries
            "--format=sarif-latest",
            f"--output={output_sarif_path}"
        ]
        _, return_code = self._run_command(analyze_command)
        if return_code != 0:
            logger.error(f"Failed to run CodeQL analysis (exit code {return_code}).")
            return False
        logger.info(f"CodeQL analysis completed. Results saved to {output_sarif_path}")
        self.process_codeql_results(output_sarif_path) # Process results immediately
        return True
        
    def process_codeql_results(self, sarif_file_path):
        """
        Processes CodeQL SARIF results and adds findings to the auditor's list.
        """
        if not os.path.exists(sarif_file_path):
            logger.warning(f"CodeQL SARIF file not found: {sarif_file_path}")
            return

        logger.info(f"Processing CodeQL results from {sarif_file_path}...")
        try:
            with open(sarif_file_path, 'r', encoding='utf-8') as f:
                sarif_data = json.load(f)

            findings_count = 0
            if "runs" in sarif_data:
                for run in sarif_data["runs"]:
                    if "results" in run:
                        for result in run["results"]:
                            findings_count += 1
                            rule_id = result.get("ruleId", "N/A")
                            message = result["message"]["text"]
                            location = "N/A"
                            file_path = "N/A"
                            line_number = "N/A"

                            if "locations" in result and result["locations"]:
                                physical_location = result["locations"][0].get("physicalLocation")
                                if physical_location:
                                    artifact_location = physical_location.get("artifactLocation")
                                    region = physical_location.get("region")
                                    if artifact_location and "uri" in artifact_location:
                                        file_path = artifact_location["uri"].replace("file://", "")
                                    if region and "startLine" in region:
                                        line_number = region['startLine']

                            severity_map = {
                                'error': 'CRITICAL', 'warning': 'HIGH', 'note': 'MEDIUM' # Map CodeQL levels to your severity
                            }
                            severity = severity_map.get(result.get("level", "note"), 'UNKNOWN')
                            
                            self.add_finding(
                                severity=severity,
                                category="Static Analysis (CodeQL)",
                                title=f"CodeQL: {rule_id}",
                                description=message,
                                file_path=file_path,
                                line_number=line_number,
                                recommendation=f"Review CodeQL rule documentation for '{rule_id}'."
                            )
            if findings_count == 0:
                logger.info("No findings reported by CodeQL.")

        except json.JSONDecodeError:
            logger.error(f"Error decoding JSON from CodeQL SARIF file: {sarif_file_path}. Is it a valid SARIF file?")
        except Exception as e:
            logger.error(f"An unexpected error occurred while processing CodeQL results: {e}")

    def run_sonarqube_scan(self):
        """
        Runs a SonarQube scan on the specified project directory.
        """
        self._print_header("SonarQube Analysis")
        
        # Sonar Scanner command construction
        command = ["sonar-scanner"]

        # Add mandatory properties
        command.append(f"-Dsonar.projectKey={self.sonar_project_key}")
        command.append(f"-Dsonar.sources={self.project_root}") # Scan entire project
        command.append(f"-Dsonar.host.url={self.sonar_host_url}")

        # Add optional properties
        if self.sonar_organization:
            command.append(f"-Dsonar.organization={self.sonar_organization}")
        if self.sonar_token:
            command.append(f"-Dsonar.token={self.sonar_token}")
        else:
            logger.warning("SONAR_TOKEN environment variable not set. SonarQube scan might fail if authentication is required.")

        logger.info(f"Executing SonarQube command: {' '.join(command)}")

        # SonarQube scanner often prints to stderr for progress,
        # so we let it print directly to the console/log file for better visibility.
        # We only care about the return code for success/failure.
        _, return_code = self._run_command(command, stdout_target=sys.stdout, stderr_target=sys.stderr)
        
        if return_code == 0:
            logger.info("SonarQube scan completed successfully. Results are available on your SonarQube dashboard.")
            return True
        else:
            logger.error(f"SonarQube scan failed with exit code {return_code}. Please ensure SonarQube server is running, project key is correct, and 'sonar-scanner' is in your PATH.")
            self.add_finding(
                severity='CRITICAL',
                category='Tool Execution Failure',
                title='SonarQube Scan Failed',
                description=f"SonarQube scan failed with exit code {return_code}. Check the detailed logs for reasons (e.g., server connectivity, invalid token, scanner not found).",
                file_path="N/A",
                line_number=0,
                recommendation="Investigate SonarQube server status, network connectivity, and scanner configuration."
            )
            return False

    def run_semgrep_scan(self, target_path, output_json_path, config_path):
        """
        Runs a Semgrep scan on the specified path with a given configuration.
        """
        self._print_header(f"Semgrep Security Scan for {os.path.basename(target_path)}")
        
        command = [
            "semgrep",
            f"--config={config_path}",
            f"--output={output_json_path}",
            "--json",
            target_path
        ]

        output_str, return_code = self._run_command(command)
        
        if output_str is None:
            logger.error(f"Semgrep scan for {target_path} could not be run or produced no output.")
            self.add_finding(
                severity='CRITICAL',
                category='Tool Execution Failure',
                title=f'Semgrep Scan Failed for {os.path.basename(target_path)}',
                description=f"Semgrep command failed to execute or timed out. Check if Semgrep CLI is installed and in PATH.",
                file_path="N/A",
                line_number=0,
                recommendation="Ensure Semgrep CLI is installed and accessible."
            )
            return False

        if return_code != 0:
            logger.error(f"Semgrep scan for {target_path} failed with exit code {return_code}.")
            self.add_finding(
                severity='CRITICAL',
                category='Tool Execution Failure',
                title=f'Semgrep Scan Failed for {os.path.basename(target_path)}',
                description=f"Semgrep exited with non-zero code {return_code}. This might indicate a configuration issue or a critical error during scan.",
                file_path="N/A",
                line_number=0,
                recommendation="Review Semgrep configuration and logs for errors."
            )
            return False
        
        logger.info(f"Semgrep scan completed. Results saved to {output_json_path}")
        self.process_semgrep_results(output_json_path)
        return True
        
    def process_semgrep_results(self, json_file_path):
        """
        Processes Semgrep JSON results and adds findings to the auditor's list.
        """
        if not os.path.exists(json_file_path):
            logger.warning(f"Semgrep JSON file not found: {json_file_path}")
            return

        logger.info(f"Processing Semgrep results from {json_file_path}...")
        try:
            with open(json_file_path, 'r', encoding='utf-8') as f:
                semgrep_data = json.load(f)

            findings_count = 0
            if "results" in semgrep_data:
                for result in semgrep_data["results"]:
                    findings_count += 1
                    check_id = result.get("check_id", "N/A")
                    message = result.get("extra", {}).get("message", "No message provided.")
                    path = result.get("path", "N/A")
                    start_line = result.get("start", {}).get("line", "N/A")
                    severity_raw = result.get("extra", {}).get("severity", "UNKNOWN").upper()
                    
                    # Map Semgrep severity to your own severity levels
                    severity_map = {
                        'ERROR': 'CRITICAL',
                        'WARNING': 'HIGH',
                        'INFO': 'MEDIUM',
                        'UNKNOWN': 'UNKNOWN'
                    }
                    severity = severity_map.get(severity_raw, 'UNKNOWN')

                    self.add_finding(
                        severity=severity,
                        category="Static Analysis (Semgrep)",
                        title=f"Semgrep: {check_id}",
                        description=message,
                        file_path=path,
                        line_number=start_line,
                        recommendation=f"Review Semgrep rule documentation for '{check_id}'."
                    )
            if findings_count == 0:
                logger.info("No findings reported by Semgrep.")

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

    def run_code_integrity_scan(self):
        """Runs syntax checks and detects circular imports."""
        self._print_header("Backend Code Integrity (Syntax & Circular Imports)")

        backend_files = self._find_files(self.backend_dir, ['.py'], exclude_dirs=['website/node_modules'])
        if not backend_files:
            logger.warning("No Python files found in backend to scan for integrity.")
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
            logger.info("Syntax check passed for all backend files.")

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
            logger.info("No circular imports detected.")

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
                    # Filter for internal dependencies within the backend directory
                    # This assumes backend_dir is like 'backend' and module names start with 'backend.'
                    backend_base_module = os.path.basename(self.backend_dir)
                    internal_deps = {dep for dep in visitor.dependencies if dep.startswith(backend_base_module)}
                    if internal_deps:
                        dependency_graph[module_name].update(internal_deps)
            except Exception as e:
                logger.error(f"Could not analyze dependencies for {file_path}: {e}")
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
                        sorted_cycle = tuple(sorted(cycle[:-1])) # Use sorted tuple to avoid duplicate cycles
                        if sorted_cycle not in [tuple(sorted(c[:-1])) for c in cycles]:
                            cycles.append(cycle)
                    except ValueError:
                        # Should not happen if neighbour in path, but as a fallback
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
            # Convert absolute path to relative path from project root, then to module name
            relative_path = os.path.relpath(path, start=os.getcwd()) # Get path relative to current working directory
            path_parts = os.path.splitext(relative_path)[0].split(os.path.sep)
            return '.'.join(path_parts)
            
        def visit_Import(self, node):
            for alias in node.names:
                self.dependencies.add(alias.name)
            self.generic_visit(node)

        def visit_ImportFrom(self, node):
            module_name = node.module
            if node.level > 0:
                # Handle relative imports correctly
                parts = self.current_module_name.split('.')
                base_path_parts = parts[:-(node.level)]
                if module_name:
                    module_name = '.'.join(base_path_parts + [module_name])
                else:
                    module_name = '.'.join(base_path_parts)
            if module_name:
                self.dependencies.add(module_name)
            self.generic_visit(node)

    def run_safety_scan(self):
        """Runs Safety to check for backend dependency vulnerabilities."""
        self._print_header("Backend Dependency Scan (Safety)")
        if self.config.get('skip_dependency_check', False):
            logger.info("Skipping Safety scan as per configuration.")
            return

        logger.info("This scan may take a moment as it might need to fetch the latest vulnerability database...")
        req_file = os.path.join(self.backend_dir, 'requirements.txt')
        if not os.path.exists(req_file):
            logger.warning(f"Could not find requirements.txt at '{self.backend_dir}'. Skipping Safety scan.")
            return

        command = [sys.executable, '-m', 'safety', 'scan', f'--file={req_file}', '--json']
        output, return_code = self._run_command(command)
        
        if output is None: # Command execution failed or timed out
            self.add_finding(
                severity="CRITICAL",
                category="Tool Execution Failure",
                title="Safety Scan Failed",
                description="Safety command could not be run or produced no output. Check if 'safety' is installed.",
                file_path="N/A",
                line_number=0,
                recommendation="Ensure 'safety' is installed (`pip install safety`) and in your PATH."
            )
            return

        try:
            report = json.loads(output)
            vulnerabilities_found = 0
            # Safety's JSON output format can vary; handle both list and dict of vulnerabilities
            if isinstance(report, dict) and 'vulnerabilities' in report:
                for vuln_id, vuln_data in report.get('vulnerabilities', {}).items():
                    vulnerabilities_found += 1
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
            elif isinstance(report, list): # Older Safety versions or specific output
                for vuln_data in report:
                    vulnerabilities_found += 1
                    self.add_finding(
                        severity="HIGH",
                        category="Dependency Vulnerability (Safety)",
                        title=f"Vulnerable package: {vuln_data.get('package_name')} ({vuln_data.get('found_version')})",
                        description=f"Advisory: {vuln_data.get('advisory')}",
                        file_path=req_file,
                        line_number=1,
                        recommendation=f"Upgrade to a fixed version. Fixed in: {', '.join(vuln_data.get('fixed_versions', ['N/A']))}",
                        cwe_id=vuln_data.get('vulnerability_id', 'N/A')
                    )

            if vulnerabilities_found > 0:
                logger.info(f"Safety scan found {vulnerabilities_found} vulnerabilities.")
            else:
                logger.info("Safety scan completed with no vulnerabilities found.")
        except json.JSONDecodeError as e:
            logger.error(f"Could not decode Safety JSON output: {e}. Raw output (first 500 chars):\n{output[:500]}...")
            self.add_finding(
                severity="CRITICAL",
                category="Tool Output Parsing Error",
                title="Safety Output Parsing Failed",
                description=f"Safety scan ran, but its output was not valid JSON: {e}",
                file_path="N/A",
                line_number=0,
                recommendation="Check Safety CLI version and output format."
            )

    def run_pip_audit(self):
        """Runs pip-audit to check for backend dependency vulnerabilities using a temporary file for the report."""
        if self.config.get('skip_dependency_check', False):
            logger.info("Skipping pip-audit as per configuration.")
            return
            
        self._print_header("Backend Dependency Scan (pip-audit)")
        req_file = os.path.join(self.backend_dir, 'requirements.txt')
        if not os.path.exists(req_file):
            req_file = os.path.join(self.project_root, 'requirements.txt')
            if not os.path.exists(req_file):
                logger.warning(f"Could not find requirements.txt at '{self.backend_dir}' or '{self.project_root}'. Skipping pip-audit.")
                return
        
        with tempfile.NamedTemporaryFile(mode='w+', delete=False, encoding='utf-8', suffix=".json") as tmp_file:
            report_filename = tmp_file.name
        
        try:
            command = [
                sys.executable, '-m', 'pip_audit',
                '-r', req_file,
                '-f', 'json',
                '-o', report_filename
            ]
            
            _, return_code = self._run_command(command) # Capture return code
            
            if not os.path.exists(report_filename) or os.path.getsize(report_filename) == 0:
                logger.error(f"pip-audit did not generate an output file at {report_filename} or it was empty.")
                self.add_finding(
                    severity="CRITICAL",
                    category="Tool Execution Failure",
                    title="pip-audit Scan Failed",
                    description="pip-audit command failed to produce a valid report. Check if 'pip-audit' is installed.",
                    file_path="N/A",
                    line_number=0,
                    recommendation="Ensure 'pip-audit' is installed (`pip install pip-audit`) and in your PATH."
                )
                return

            with open(report_filename, 'r', encoding='utf-8') as f:
                try:
                    report = json.load(f)
                except json.JSONDecodeError:
                    logger.error(f"pip-audit ran, but its output at {report_filename} was not valid JSON. Please inspect the file.")
                    self.add_finding(
                        severity="CRITICAL",
                        category="Tool Output Parsing Error",
                        title="pip-audit Output Parsing Failed",
                        description=f"pip-audit scan ran, but its output was not valid JSON: {e}",
                        file_path="N/A",
                        line_number=0,
                        recommendation="Check pip-audit CLI version and output format."
                    )
                    return
        
            if 'vulnerabilities' in report and report['vulnerabilities']:
                logger.info(f"pip-audit found {len(report['vulnerabilities'])} vulnerabilities.")
                with open(req_file, 'r', encoding='utf-8') as f_req:
                    req_lines = f_req.readlines()
        
                for vuln_data in report['vulnerabilities']:
                    package_name = vuln_data.get('name', 'N/A')
                    package_version = vuln_data.get('version', 'N/A')
                    vuln_id = vuln_data.get('id', 'N/A')
                    description = vuln_data.get('details', 'No description provided.')
                    fixed_versions = ', '.join(vuln_data.get('fix_versions', ['N/A']))
        
                    line_number = "N/A"
                    for i, line in enumerate(req_lines):
                        if package_name.lower() in line.lower():
                            line_number = i + 1
                            break
        
                    self.add_finding(
                        severity="HIGH",
                        category="Dependency Vulnerability (pip-audit)",
                        title=f"Vulnerable package: {package_name}=={package_version}",
                        description=f"Vulnerability ID: {vuln_id}. Details: {description}",
                        file_path=req_file,
                        line_number=line_number,
                        recommendation=f"Upgrade to a fixed version, e.g.,: {fixed_versions}",
                    )
            else:
                logger.info("pip-audit completed with no vulnerabilities found.")
        
        finally:
            if os.path.exists(report_filename):
                os.remove(report_filename)
                
    def run_npm_audit(self):
        """Runs npm audit to check for frontend dependency vulnerabilities."""
        if self.config.get('skip_dependency_check', False):
            logger.info("Skipping npm audit as per configuration.")
            return

        self._print_header("Frontend Dependency Scan (npm audit)")
        
        if not os.path.isdir(self.frontend_dir):
            logger.warning(f"Frontend directory '{self.frontend_dir}' not found. Skipping npm audit.")
            return

        npm_cmd = ['npm', 'audit', '--json']

        output_str, return_code = self._run_command(npm_cmd, cwd=self.frontend_dir)
        
        if output_str is None:
            self.add_finding(
                severity="CRITICAL",
                category="Tool Execution Failure",
                title="npm audit Scan Failed",
                description="npm audit command could not be run or produced no output. Check if 'npm' is installed.",
                file_path="N/A",
                line_number=0,
                recommendation="Ensure 'npm' is installed and accessible in your PATH."
            )
            return

        try:
            report = json.loads(output_str)

            vulnerabilities_found = 0
            # npm audit output format can vary, handle both 'advisories' and 'vulnerabilities' top-level keys
            if 'advisories' in report: # Newer npm audit output
                for advisory_id, advisory_data in report['advisories'].items():
                    vulnerabilities_found += 1
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
            elif 'vulnerabilities' in report and report['vulnerabilities']: # Older npm audit output
                for pkg_name, pkg_data in report['vulnerabilities'].items():
                    for vuln_info in pkg_data.get('via', []):
                        if isinstance(vuln_info, dict):
                            vulnerabilities_found += 1
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

            if vulnerabilities_found > 0:
                logger.info(f"npm audit found {vulnerabilities_found} vulnerabilities.")
            else:
                logger.info("npm audit completed with no vulnerabilities found.")

            if return_code != 0 and vulnerabilities_found == 0:
                logger.warning(f"npm audit exited with non-zero code ({return_code}) but reported no vulnerabilities in its JSON output or parsing failed. Check stderr logs for details.")

        except json.JSONDecodeError as e:
            logger.error(f"Could not decode npm audit JSON output. Error: {e}")
            logger.error(f"Raw npm audit output that failed to decode (first 500 chars):\n{output_str[:500]}...")
            self.add_finding(
                severity="CRITICAL",
                category="Tool Output Parsing Error",
                title="npm audit Output Parsing Failed",
                description=f"npm audit scan ran, but its output was not valid JSON: {e}",
                file_path="N/A",
                line_number=0,
                recommendation="Check npm audit CLI version and output format."
            )
        except KeyError as e:
            logger.error(f"Missing expected key in npm audit JSON output: {e}. Ensure npm audit JSON format matches expectations.")
            logger.error(f"Problematic JSON (full output, if short enough): {output_str}")
            self.add_finding(
                severity="CRITICAL",
                category="Tool Output Parsing Error",
                title="npm audit Output Structure Error",
                description=f"npm audit output structure was unexpected: Missing key '{e}'.",
                file_path="N/A",
                line_number=0,
                recommendation="Check npm audit CLI version and output format."
            )

    def run_bandit_scan(self):
        """Runs Bandit static analysis on the backend directory, writing the report to a file for stable parsing."""
        if self.config.get('skip_static_analysis', False):
            logger.info("Skipping Bandit scan as per configuration.")
            return
        
        self._print_header("Backend Security Scan (Bandit)")
        if not os.path.isdir(self.backend_dir):
            logger.warning(f"Backend directory '{self.backend_dir}' not found. Skipping Bandit scan.")
            return
        
        with tempfile.NamedTemporaryFile(mode='w+', delete=False, encoding='utf-8', suffix=".json") as tmp_file:
            report_filename = tmp_file.name
        
        try:
            bandit_cmd = [
                sys.executable, '-m', 'bandit',
                '-r', self.backend_dir,
                '-f', 'json',
                '-o', report_filename,
                '-x', 'tests'
            ]
            
            _, return_code = self._run_command(bandit_cmd)
            
            if not os.path.exists(report_filename) or os.path.getsize(report_filename) == 0:
                logger.error(f"Bandit did not generate an output file at {report_filename} or it was empty.")
                self.add_finding(
                    severity="CRITICAL",
                    category="Tool Execution Failure",
                    title="Bandit Scan Failed",
                    description="Bandit command failed to produce a valid report. Check if 'bandit' is installed.",
                    file_path="N/A",
                    line_number=0,
                    recommendation="Ensure 'bandit' is installed (`pip install bandit`) and in your PATH."
                )
                return

            with open(report_filename, 'r', encoding='utf-8') as f:
                try:
                    report = json.load(f)
                except json.JSONDecodeError:
                    logger.error(f"Bandit ran, but its output at {report_filename} was not valid JSON. Please inspect the file.")
                    self.add_finding(
                        severity="CRITICAL",
                        category="Tool Output Parsing Error",
                        title="Bandit Output Parsing Failed",
                        description=f"Bandit scan ran, but its output was not valid JSON: {e}",
                        file_path="N/A",
                        line_number=0,
                        recommendation="Check Bandit CLI version and output format."
                    )
                    return
        
            if 'results' in report and report['results']:
                logger.info(f"Bandit scan found {len(report['results'])} issues.")
                for issue in report['results']:
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
                logger.info("Bandit scan completed with no security issues found.")
        
        finally:
            if os.path.exists(report_filename):
                os.remove(report_filename)
                
    def run_pylint_scan(self):
        """Runs Pylint static analysis on the backend directory and parses the JSON output."""
        if self.config.get('skip_static_analysis', False):
            logger.info("Skipping Pylint scan as per configuration.")
            return

        self._print_header("Backend Code Linting (Pylint)")
        if not os.path.isdir(self.backend_dir):
            logger.warning(f"Backend directory '{self.backend_dir}' not found. Skipping Pylint scan.")
            return

        with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix=".json", encoding='utf-8') as tmp_file:
            pylint_output_file = tmp_file.name

        pylint_cmd = [
            sys.executable, '-m', 'pylint',
            self.backend_dir,
            '--output-format=json'
        ]

        _, return_code = self._run_command(pylint_cmd, stdout_target=open(pylint_output_file, 'w'), stderr_target=subprocess.PIPE)

        if not os.path.exists(pylint_output_file) or os.path.getsize(pylint_output_file) == 0:
            logger.error(f"Pylint did not generate an output file at {pylint_output_file} or it was empty. Pylint might have crashed. Check stderr logs.")
            self.add_finding(
                severity="CRITICAL",
                category="Tool Execution Failure",
                title="Pylint Scan Failed",
                description="Pylint command failed to produce a valid report. Check if 'pylint' is installed.",
                file_path="N/A",
                line_number=0,
                recommendation="Ensure 'pylint' is installed (`pip install pylint`) and in your PATH."
            )
            if os.path.exists(pylint_output_file): # Clean up even if empty
                os.remove(pylint_output_file)
            return

        try:
            with open(pylint_output_file, 'r', encoding='utf-8') as f:
                report = json.load(f)

            if not report:
                logger.info("Pylint scan completed with no issues found.")
                return

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
            logger.info(f"Pylint scan found {len(report)} issues.")
        except (json.JSONDecodeError, Exception) as e:
            logger.error(f"An unexpected error occurred while parsing Pylint report from {pylint_output_file}: {e}")
            self.add_finding(
                severity="CRITICAL",
                category="Tool Output Parsing Error",
                title="Pylint Output Parsing Failed",
                description=f"Pylint scan ran, but its output was not valid JSON or unexpected: {e}",
                file_path="N/A",
                line_number=0,
                recommendation="Check Pylint CLI version and output format."
            )
        finally:
            if os.path.exists(pylint_output_file):
                os.remove(pylint_output_file)

    def run_mypy_scan(self):
        """Runs Mypy for static type checking and parses the output."""
        if self.config.get('skip_static_analysis', False):
            logger.info("Skipping Mypy scan as per configuration.")
            return

        self._print_header("Backend Static Type Checking (Mypy)")
        if not os.path.isdir(self.backend_dir):
            logger.warning(f"Backend directory '{self.backend_dir}' not found. Skipping Mypy scan.")
            return

        mypy_cmd = [
            sys.executable, '-m', 'mypy',
            self.backend_dir,
            '--ignore-missing-imports'
        ]

        output, return_code = self._run_command(mypy_cmd)

        if return_code == 0 or not output: # Mypy returns 0 on success, even with notes/warnings
            logger.info("Mypy scan completed with no type errors found.")
            return

        mypy_pattern = re.compile(r"([^:]+):(\d+): (error|note): (.+)")
        
        issues_found = 0
        for line in output.strip().split('\n'):
            match = mypy_pattern.match(line)
            if match:
                issues_found += 1
                file_path, line_number, severity_type, description = match.groups()
                
                # Map Mypy severity to your own severity levels
                severity_map = {
                    'error': 'HIGH',
                    'note': 'LOW' # Mypy notes are usually informational
                }
                severity = severity_map.get(severity_type, 'UNKNOWN')

                self.add_finding(
                    severity=severity,
                    category="Static Type Checking (Mypy)",
                    title=f"Mypy: {severity_type.capitalize()} Detected",
                    description=description.strip(),
                    file_path=file_path.strip(),
                    line_number=int(line_number),
                    recommendation="Fix the type hint or the code that violates it to ensure type safety."
                )
        
        if issues_found > 0:
            logger.info(f"Mypy scan found {issues_found} type errors.")
        else:
            logger.warning("Mypy exited with a non-zero status but no issues could be parsed from its output. Check raw stderr for details.")
            self.add_finding(
                severity="CRITICAL",
                category="Tool Output Parsing Error",
                title="Mypy Output Parsing Failed",
                description="Mypy scan ran, but its output could not be parsed. Check raw output for errors.",
                file_path="N/A",
                line_number=0,
                recommendation="Check Mypy CLI version and output format."
            )


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
                # Improved regex to reduce false positives for common variable names like 'secret_key'
                # This pattern looks for assignments where the right-hand side is a string literal
                # and the left-hand side contains a secret keyword.
                # It's still heuristic but better than simple substring.
                hardcoded_secret_pattern = re.compile(r'\b(?:' + '|'.join(secret_keywords) + r')\s*=\s*[\'"].+?[\'"]', re.IGNORECASE)

                for i, line in enumerate(content.splitlines(), 1):
                    if hardcoded_secret_pattern.search(line):
                        # Further filter out common non-secret variable names if necessary
                        if not (re.search(r'\b(secret_key|secret_message)\b', line, re.IGNORECASE) and 'config' in file_path.lower()):
                            self.add_finding(
                                severity='HIGH', category='Security', title='Potential Hardcoded Secret',
                                description=f"Line contains a keyword that might indicate a hardcoded secret. Review manually.",
                                file_path=file_path, line_number=i, code_snippet=line.strip(),
                                recommendation="Store secrets in environment variables or a secure vault, not in code. Use a dedicated secrets scanning tool for more robust detection."
                            )

                # Check for insecure HTTP URLs
                http_patterns = [r'http://(?!localhost|127\.0\.0\.1|0\.0\.0\.0|schemas\.openxmlformats\.org|www\.w3\.org|purl\.org)'] # Exclude common XML/schema URLs
                for pattern in http_patterns:
                    for match in re.finditer(pattern, content, re.IGNORECASE):
                        line_num = content.count('\n', 0, match.start()) + 1
                        self.add_finding(
                            severity="HIGH", category="HTTPS", title="Insecure HTTP URL",
                            description=f"Insecure HTTP URL found: {match.group()}",
                            file_path=file_path, line_number=line_num,
                            recommendation="Use HTTPS for all external connections. If this is an internal/local connection, ensure it's truly isolated."
                        )

                # Check for bare except clauses (Python specific)
                if file_path.endswith('.py'):
                    bare_except_pattern = r'except\s*:'
                    for match in re.finditer(bare_except_pattern, content):
                        line_num = content.count('\n', 0, match.start()) + 1
                        self.add_finding(
                            severity="MEDIUM", category="Error Handling", title="Bare Except Clause",
                            description="Bare except clause catches all exceptions, which can hide bugs and make debugging difficult.",
                            file_path=file_path, line_number=line_num,
                            recommendation="Catch specific exceptions instead of using a bare except, or re-raise if not handled."
                        )

            except Exception as e:
                logger.warning(f"Could not process file {file_path} for best practices audit: {e}")

        logger.info("Best practices audit checks completed.")


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
        
        # Run CodeQL Scan (for Python backend)
        self.run_codeql_scan()

        # Run SonarQube Scan (for entire project)
        # Note: SonarQube results are viewed on the SonarQube dashboard, not directly added to self.findings
        self.run_sonarqube_scan()

        # Run Semgrep Scan (for Python Backend)
        self.run_semgrep_scan(
            target_path=self.backend_dir,
            output_json_path=self.semgrep_python_output,
            config_path=self.semgrep_python_config
        )

        # Run Semgrep Scan (for Vue.js Frontend)
        self.run_semgrep_scan(
            target_path=self.frontend_dir,
            output_json_path=self.semgrep_vuejs_output,
            config_path=self.semgrep_vuejs_config
        )
        
        # checks for type errors (Static Type Checking)
        self.run_mypy_scan()
        
        # Run Pylint scan for code quality and potential bugs
        self.run_pylint_scan()

        # Run code integrity checks (syntax, circular imports)
        self.run_code_integrity_scan()

        # Run best practices audit
        self.run_best_practices_audit()

        self._print_header("AUDIT SUMMARY")
        if self.findings:
            self.findings.sort(key=lambda f: self.severity_order.get(f.get('severity', 'UNKNOWN'), 99))
            
            logger.info(f"Found {len(self.findings)} potential issues:")
            for i, finding in enumerate(self.findings):
                logger.info(f"  {i+1}. [{finding.get('severity', 'UNKNOWN')}] {finding.get('title', 'No Title')}")
                logger.info(f"      Category: {finding.get('category', 'N/A')}")
                logger.info(f"      File: {finding.get('file_path', 'N/A')}:{finding.get('line_number', 'N/A')}")
                logger.info(f"      Description: {finding.get('description', 'N/A')}")
                if finding.get('recommendation'):
                    logger.info(f"      Recommendation: {finding['recommendation']}")
                if finding.get('code_snippet'):
                    logger.info(f"      Code Snippet:\n{finding['code_snippet']}")
                logger.info("-" * 20)
        else:
            logger.info("No issues found during the audit.")

        return len(self.findings)

if __name__ == "__main__":
    # This block allows the script to be run directly from the command line,
    # which is how it's called from `run_audits.sh`.

    # Define a simple default configuration for direct execution.
    # In a real application, this might come from command-line arguments or a config file.
    # Using a dictionary for config allows for easier passing of specific tool configurations.
    default_config = {
        'skip_dependency_check': False,
        'skip_static_analysis': False,
        'SONAR_PROJECT_KEY': "maison-truvra-project", # <<< IMPORTANT: CHANGE THIS
        'SONAR_ORGANIZATION': None, # <<< IMPORTANT: CHANGE THIS if using SonarCloud
        'SONAR_HOST_URL': "http://localhost:9000", # <<< IMPORTANT: CHANGE THIS if your SonarQube is elsewhere
        'SEMGREP_PYTHON_CONFIG': "p/python",
        'SEMGREP_VUEJS_CONFIG': "p/vuejs" # You might also use 'p/javascript', 'p/html', or custom rules
    }

    # Determine project paths based on this script's location
    project_root = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.join(project_root, 'backend')
    frontend_dir = os.path.join(project_root, 'website')

    logger.info("Security audit script is being run directly.")

    # Instantiate and run the auditor
    auditor = SecurityAuditor(default_config, project_root, backend_dir, frontend_dir)
    num_findings = auditor.run_audit()

    # Exit with a non-zero status code if findings are present
    if num_findings > 0:
        sys.exit(1)
