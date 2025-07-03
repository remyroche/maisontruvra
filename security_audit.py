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

    def _find_files(self, directory, extensions):
        """Helper to find all files with given extensions in a directory."""
        matches = []
        for root, _, filenames in os.walk(directory):
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

        backend_files = self._find_files(self.backend_dir, ['.py'])
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
        """Runs pip-audit to check for backend dependency vulnerabilities."""
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

        command = [sys.executable, '-m', 'pip_audit', '-f', 'json', '-r', req_file]
        
        output, return_code = self._run_command(command)
        
        if output is None:
            logging.error("pip-audit command could not be run or produced no parsable output.")
            return

        try:
            report = json.loads(output)
            
            if 'vulnerabilities' in report and report['vulnerabilities']:
                for vuln_data in report['vulnerabilities']:
                    package_name = vuln_data.get('affected_package', {}).get('name', 'N/A')
                    package_version = vuln_data.get('affected_package', {}).get('version', 'N/A')
                    
                    vuln_id = vuln_data.get('id', 'N/A')
                    description = vuln_data.get('details', 'No description provided.')
                    fixed_versions = ', '.join(vuln_data.get('fixed_versions', ['N/A']))
                    
                    self.add_finding(
                        severity="HIGH",
                        category="Dependency Vulnerability (pip-audit)",
                        title=f"Vulnerable package: {package_name}=={package_version}",
                        description=f"Vulnerability ID: {vuln_id}. Details: {description}",
                        file_path=req_file,
                        line_number=1,
                        recommendation=f"Upgrade to a fixed version: {fixed_versions}",
                        cwe_id=vuln_id
                    )
                logging.info(f"pip-audit found {len(report['vulnerabilities'])} vulnerabilities.")
            else:
                logging.info("pip-audit completed with no vulnerabilities found.")

            if return_code != 0 and (not report.get('vulnerabilities')):
                logging.warning(f"pip-audit exited with non-zero code ({return_code}) but reported no vulnerabilities in its JSON output. Check stderr logs for details.")

        except json.JSONDecodeError as e:
            logging.error(f"Could not decode pip-audit JSON output. Error: {e}")
            logging.error(f"Raw pip-audit output that failed to decode (first 500 chars):\n{output[:500]}...")
        except KeyError as e:
            logging.error(f"Missing expected key in pip-audit JSON output: {e}. Ensure pip-audit JSON format matches expectations.")
            logging.error(f"Problematic JSON (full output, if short enough): {output}")

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
        """Runs Bandit static analysis on the backend directory."""
        if self.config.skip_static_analysis:
            logging.info("Skipping Bandit scan as per configuration.")
            return

        self._print_header("Backend Security Scan (Bandit)")
        if not os.path.isdir(self.backend_dir):
            logging.warning(f"Backend directory '{self.backend_dir}' not found. Skipping Bandit scan.")
            return

        # Command is now more exhaustive by removing the severity filter '-ll'.
        # It will now report issues of ALL severities (LOW, MEDIUM, HIGH).
        # Confidence level defaults to MEDIUM and HIGH, which is a good balance.
        # To include LOW confidence, add: '--confidence-level', 'low'
        bandit_cmd = [sys.executable, '-m', 'bandit', '-r', self.backend_dir, '-f', 'json']

        output_str, return_code = self._run_command(
            bandit_cmd,
            stdout_target=subprocess.PIPE,
            stderr_target=subprocess.DEVNULL
        )

        logging.info("\n--- Raw Bandit Output (captured by Python) ---")
        logging.info(f"Length of raw output: {len(output_str)}")
        logging.info(f"First 200 chars of raw output:\n{output_str[:200]}")
        logging.info(f"Last 200 chars of raw output:\n{output_str[-200:]}")
        logging.info("--- End Raw Bandit Output ---")

        clean_json_str = ""
        try:
            json_start_index = -1
            for i, char in enumerate(output_str):
                if char == '{' or char == '[':
                    json_start_index = i
                    break

            json_end_index = -1
            for i in range(len(output_str) - 1, -1, -1):
                char = output_str[i]
                if char == '}' or char == ']':
                    json_end_index = i
                    break

            if json_start_index != -1 and json_end_index != -1 and json_end_index > json_start_index:
                clean_json_str = output_str[json_start_index : json_end_index + 1]
                logging.info(f"Extracted potential JSON substring from Bandit output (length: {len(clean_json_str)}).")
                
                clean_json_str = ''.join(c for c in clean_json_str if c.isprintable() or c.isspace())
                clean_json_str = clean_json_str.strip()
            else:
                logging.warning("No complete JSON structure ({...} or [...]) found in Bandit output after initial capture.")
                clean_json_str = ""

        except Exception as e:
            logging.error(f"Error trying to extract JSON substring from Bandit output: {e}")
            clean_json_str = ""

        logging.info("\n--- Cleaned JSON String (before json.loads) ---")
        logging.info(f"Length of cleaned JSON: {len(clean_json_str)}")
        logging.info(f"First 200 chars of cleaned JSON:\n{clean_json_str[:200]}")
        logging.info(f"Last 200 chars of cleaned JSON:\n{clean_json_str[-200:]}")
        logging.info("--- End Cleaned JSON String ---")


        if not clean_json_str.strip():
            logging.info("Bandit scan completed with no issues found (empty or non-parsable JSON after cleaning).")
            if return_code != 0:
                 logging.warning(f"Bandit exited with non-zero code ({return_code}) but produced no parsable JSON output.")
            return

        try:
            report = json.loads(clean_json_str)

            if 'results' in report and report['results']:
                for issue in report['results']:
                    # --- Enhanced and more specific finding details ---
                    test_name = issue.get('test_name', 'N/A')
                    confidence = issue.get('issue_confidence', 'UNKNOWN').upper()
                    more_info_url = issue.get('more_info', 'N/A')

                    # Create a more detailed description
                    description = (
                        f"Bandit Test: {test_name} ({issue.get('test_id', 'N/A')})\n"
                        f"Confidence: {confidence}\n"
                        f"This issue was flagged by Bandit, a static analysis tool for finding common security issues in Python code."
                    )

                    # Create a more helpful recommendation
                    recommendation = f"Review the issue and the guidance available at: {more_info_url}"

                    # Format the code snippet with line numbers for better context
                    code_lines = issue.get('code', '').split('\n')
                    line_range = issue.get('line_range', [issue.get('line_number', 0)])
                    start_line = line_range[0]
                    formatted_code = "\n".join(
                        f"{start_line + i: >4}: {line}" for i, line in enumerate(code_lines)
                    )

                    self.add_finding(
                        severity=issue.get('issue_severity', 'UNKNOWN').upper(),
                        category="Static Analysis (Bandit)",
                        title=issue.get('issue_text', 'No issue description'),
                        description=description,
                        file_path=issue.get('filename', 'N/A'),
                        line_number=issue.get('line_number', 'N/A'),
                        code_snippet=formatted_code,
                        recommendation=recommendation,
                        cwe_id=issue.get('test_id', 'N/A')
                    )
                logging.info(f"Bandit scan found {len(report['results'])} issues.")
            else:
                logging.info("Bandit scan completed with no security issues found in 'results' section.")

            if 'metrics' in report and report['metrics']:
                for file_path_metric, metrics_data in report['metrics'].items():
                    for severity_key in ['SEVERITY.HIGH', 'SEVERITY.MEDIUM', 'SEVERITY.LOW', 'SEVERITY.UNDEFINED']:
                        if metrics_data.get(severity_key, 0) > 0:
                            self.add_finding(
                                severity=severity_key.replace('SEVERITY.', ''),
                                category="Static Analysis (Bandit Metrics)",
                                title=f"Bandit detected {metrics_data[severity_key]} {severity_key} issues in {file_path_metric}",
                                description=f"Summary metrics for {file_path_metric} show {metrics_data[severity_key]} issues with {severity_key.replace('SEVERITY.', '')} severity. Review the detailed 'results' section if available.",
                                file_path=file_path_metric,
                                line_number=0,
                                recommendation="Review the file for potential security vulnerabilities identified by Bandit."
                            )
                            break
            else:
                logging.info("No 'metrics' section found in Bandit report or it's empty.")


            if return_code != 0 and not (report.get('results') or report.get('metrics')):
                logging.warning(f"Bandit exited with non-zero code ({return_code}) but reported no vulnerabilities in its JSON output (after parsing). This might indicate a configuration error or other non-finding issue. Please check Bandit's configuration and execution context.")

        except json.JSONDecodeError as e:
            logging.error(f"Could not decode Bandit JSON output. Error: {e}")
            logging.error(f"Problematic JSON (first 500 chars):\n{clean_json_str[:500]}...")
            with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as tmp_file:
                tmp_file.write(clean_json_str)
                logging.error(f"Problematic Bandit JSON saved to: {tmp_file.name} for manual inspection.")
            raise
        except KeyError as e:
            logging.error(f"Missing expected key in Bandit JSON output: {e}. Ensure Bandit JSON format matches expectations.")
            logging.error(f"Problematic JSON (full output, if short enough): {clean_json_str}")
            raise

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

    def run_best_practices_audit(self):
        """Runs various best practice checks from the best_practices_audit.py script."""
        self._print_header("Best Practices Audit")
        all_files = self._find_files(self.project_root, ['.py', '.js', '.vue', '.css', '.scss'])
        
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
                logging.info(f"     Category: {finding.get('category', 'N/A')}")
                logging.info(f"     File: {finding.get('file_path', 'N/A')}:{finding.get('line_number', 'N/A')}")
                logging.info(f"     Description: {finding.get('description', 'N/A')}")
                if finding.get('recommendation'):
                    logging.info(f"     Recommendation: {finding['recommendation']}")
                if finding.get('code_snippet'):
                    logging.info(f"     Code Snippet:\n{finding['code_snippet']}")
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
