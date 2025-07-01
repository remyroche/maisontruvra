#!/usr/bin/env python3
import os
import re
import subprocess
import json
import sys
import datetime
import argparse
import ast
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass, asdict
import logging

# --- DATA STRUCTURES ---

@dataclass
class SecurityFinding:
    """A dataclass to hold the details of a single security finding."""
    severity: str  # e.g., HIGH, MEDIUM, LOW
    category: str  # e.g., "Authentication", "Input Validation"
    title: str
    description: str
    file_path: str
    line_number: int
    code_snippet: str = ""
    recommendation: str = ""
    cwe_id: Optional[str] = None  # Common Weakness Enumeration ID

    def to_dict(self):
        return asdict(self)

# --- UTILITIES ---

class Colors:
    """ANSI color codes for console output."""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

# --- MAIN AUDITOR CLASS ---

class SecurityAuditor:
    """
    A comprehensive security auditor that scans for vulnerabilities in
    a Python (Flask) and JavaScript (Vue) project.
    """

    def __init__(self, config: argparse.Namespace):
        """
        Initializes the SecurityAuditor with given configuration.

        Args:
            config: An argparse Namespace object with configuration options.
        """
        self.config = config
        self.findings: List[SecurityFinding] = []
        self.project_root = os.path.abspath(os.path.dirname(__file__))

        # --- PATHS CONFIGURATION ---
        self.backend_dir = os.path.join(self.project_root, 'backend')
        self.frontend_dir = os.path.join(self.project_root, 'website')

        self.scan_directories = [self.backend_dir, self.frontend_dir]
        self.excluded_paths = [
            os.path.abspath(os.path.join(self.project_root, p)) for p in [
                'backend/migrations',
                'backend/tests',
                'backend/__pycache__',
                'website/node_modules',
                'website/dist',
                '.venv',
                '.git',
            ]
        ]

        # --- RULES CONFIGURATION ---
        self.permission_decorators = [
            '@jwt_required', '@roles_required', '@permissions_required',
            '@admin_required', '@staff_required', '@b2b_user_required',
            '@b2b_admin_required', '@login_required'
        ]
        self.public_routes = [
            r"@auth_bp\.route\('/login'", r"@auth_bp\.route\('/register'",
            r"@auth_bp\.route\('/refresh'", r"@csrf_bp\.route\('/get-csrf-token'"
        ]

    def _print_header(self, title: str):
        """Prints a styled header to the console."""
        print(f"\n{Colors.HEADER}{Colors.BOLD}===== {title.upper()} ====={Colors.ENDC}")

    def _run_command(self, command: List[str], cwd: str = '.') -> Optional[str]:
        """
        Runs a shell command and returns its standard output.

        Args:
            command: The command to run as a list of strings.
            cwd: The working directory for the command.

        Returns:
            The stdout from the command, or None if an error occurred.
        """
        try:
            logging.info(f"Running command: {' '.join(command)} in {cwd}")
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=True,
                cwd=cwd
            )
            return result.stdout
        except FileNotFoundError:
            logging.error(f"Command '{command[0]}' not found.")
            if command[0] == 'npm':
                logging.warning("Please ensure Node.js and npm are installed and in your system's PATH.")
            elif 'bandit' in command[0]:
                logging.warning("Please install bandit: pip install bandit")
            elif 'pip_audit' in command[0]:
                logging.warning("Please install pip-audit: pip install pip-audit")
            return None
        except subprocess.CalledProcessError as e:
            # Tools like npm audit and pip-audit return non-zero exit codes on finding vulnerabilities.
            # This is expected, so we return the output for parsing.
            if e.stdout:
                return e.stdout
            logging.error(f"Error executing command: {' '.join(command)}")
            logging.error(e.stderr)
            return None

    def add_finding(self, **kwargs: Any):
        """Adds a security finding to the internal list."""
        finding = SecurityFinding(**kwargs)
        self.findings.append(finding)
        color = {
            "HIGH": Colors.RED, "MEDIUM": Colors.YELLOW, "LOW": Colors.BLUE
        }.get(finding.severity.upper(), Colors.ENDC)
        print(f"[{color}{finding.severity.upper()}{Colors.ENDC}] {finding.title}\n  -> {finding.file_path}:{finding.line_number}")

    # --- EXTERNAL TOOL SCANNERS ---

    def run_bandit_scan(self):
        """Runs Bandit static analysis on the backend directory."""
        if self.config.skip_static_analysis:
            logging.info("Skipping Bandit scan as per configuration.")
            return

        self._print_header("Backend Security Scan (Bandit)")
        if not os.path.isdir(self.backend_dir):
            logging.warning(f"Backend directory '{self.backend_dir}' not found. Skipping Bandit scan.")
            return

        bandit_cmd = [sys.executable, '-m', 'bandit', '-r', self.backend_dir, '-f', 'json', '-ll']
        output = self._run_command(bandit_cmd)
        if not output:
            return

        try:
            report = json.loads(output)
            for issue in report.get('results', []):
                self.add_finding(
                    severity=issue['issue_severity'],
                    category="Static Analysis (Bandit)",
                    title=issue['issue_text'],
                    description=f"Confidence: {issue['issue_confidence']}. More Info: {issue['more_info']}",
                    file_path=issue['filename'],
                    line_number=issue['line_number'],
                    code_snippet=issue['code'].strip(),
                    cwe_id=issue['test_id'] # Bandit IDs are CWE compatible
                )
        except json.JSONDecodeError:
            logging.error("Could not decode Bandit JSON output.")

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
        output = self._run_command(npm_cmd, cwd=self.frontend_dir)
        if not output:
            return

        try:
            report = json.loads(output)
            vulnerabilities = report.get('vulnerabilities', {})
            for name, details in vulnerabilities.items():
                via = [v['name'] for v in details.get('via', []) if isinstance(v, dict)]
                self.add_finding(
                    severity=details['severity'].upper(),
                    category="Dependency Vulnerability (npm)",
                    title=f"Vulnerable package: {name}",
                    description=f"Affected versions: {details['range']}. Dependency of: {', '.join(via)}.",
                    file_path=os.path.join(self.frontend_dir, 'package.json'),
                    line_number=1,
                    recommendation=f"Run 'npm audit fix' or update '{name}' manually."
                )
        except json.JSONDecodeError:
            logging.error("Could not decode npm audit JSON output. Is npm installed?")

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
                logging.warning("Could not find requirements.txt. Skipping pip-audit.")
                return

        command = [sys.executable, '-m', 'pip_audit', '--json', '-r', req_file]
        output = self._run_command(command)
        if not output:
            return

        try:
            report = json.loads(output)
            for dep in report.get('dependencies', []):
                if dep.get('vulns'):
                    for vuln in dep['vulns']:
                        self.add_finding(
                            severity="HIGH", # pip-audit doesn't provide severity, default to high
                            category="Dependency Vulnerability (pip)",
                            title=f"Vulnerable package: {dep['name']}=={dep['version']}",
                            description=f"{vuln['id']}: {vuln['description']}",
                            file_path=req_file,
                            line_number=1,
                            recommendation=f"Upgrade to a fixed version: {', '.join(vuln.get('fix_versions', ['N/A']))}"
                        )
        except json.JSONDecodeError:
            logging.error("Could not decode pip-audit JSON output.")


    # --- CUSTOM STATIC ANALYSIS CHECKS ---

    def find_files_to_scan(self) -> List[str]:
        """Finds all relevant files, excluding specified paths."""
        allowed_extensions = ('.py', '.js', '.vue', '.html')
        found_files = []
        for directory in self.scan_directories:
            if not os.path.isdir(directory):
                logging.warning(f"Scan directory '{directory}' does not exist, skipping.")
                continue
            for root, _, files in os.walk(directory):
                current_path_abs = os.path.abspath(root)
                if any(current_path_abs.startswith(excluded) for excluded in self.excluded_paths):
                    continue

                for file in files:
                    if file.endswith(allowed_extensions):
                        found_files.append(os.path.join(root, file))
        return found_files

    def analyze_file(self, file_path: str):
        """Runs all applicable checks on a single file."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.splitlines()
        except Exception as e:
            logging.error(f"Could not read file {file_path}: {e}")
            return

        # Python-specific checks
        if file_path.endswith('.py'):
            self.check_hardcoded_secrets(file_path, content, lines)
            self.check_sql_injection_patterns(file_path, content, lines)
            self.check_weak_crypto(file_path, content, lines)
            self.check_debug_info(file_path, content, lines)
            self.check_missing_permissions(file_path, content, lines)
            self.check_secure_cookies(file_path, content, lines)

        # Frontend-specific checks
        if file_path.endswith(('.vue', '.html')):
            self.check_xss_vulnerabilities(file_path, content, lines)
        if file_path.endswith(('.js', '.vue')):
            self.check_for_var_keyword(file_path, lines)

        # General checks
        self.check_https_enforcement(file_path, content, lines)


    def check_hardcoded_secrets(self, file_path: str, content: str, lines: List[str]):
        secret_patterns = [
            (r'password\s*=\s*["\'][^"\']{8,}["\']', "Hardcoded Password", "CWE-798"),
            (r'api[_-]?key\s*=\s*["\'][^"\']{16,}["\']', "Hardcoded API Key", "CWE-798"),
            (r'secret[_-]?key\s*=\s*["\'][^"\']{16,}["\']', "Hardcoded Secret Key", "CWE-798"),
        ]
        for pattern, title, cwe_id in secret_patterns:
            for match in re.finditer(pattern, content, re.IGNORECASE):
                line_num = content.count('\n', 0, match.start()) + 1
                self.add_finding(
                    severity="HIGH", category="Secrets Management", title=title,
                    description=f"Potential hardcoded secret found: {match.group()}",
                    file_path=file_path, line_number=line_num,
                    code_snippet=lines[line_num - 1].strip(),
                    recommendation="Use environment variables or a secret management system.",
                    cwe_id=cwe_id
                )

    def check_sql_injection_patterns(self, file_path: str, content: str, lines: List[str]):
        sql_patterns = [
            (r'execute\s*\(\s*f["\']', "f-string in SQL execute"),
            (r'SELECT.*FROM.*\+.*', "String concatenation in SELECT query"),
        ]
        for pattern, description in sql_patterns:
            for match in re.finditer(pattern, content, re.IGNORECASE):
                line_num = content.count('\n', 0, match.start()) + 1
                self.add_finding(
                    severity="HIGH", category="Input Validation", title="Potential SQL Injection",
                    description=f"{description}: {lines[line_num - 1].strip()}",
                    file_path=file_path, line_number=line_num,
                    code_snippet=lines[line_num - 1].strip(),
                    recommendation="Use parameterized queries or an ORM.", cwe_id="CWE-89"
                )

    def check_weak_crypto(self, file_path: str, content: str, lines: List[str]):
        weak_patterns = [
            (r'hashlib\.md5\(', "MD5 hash usage", "CWE-327"),
            (r'hashlib\.sha1\(', "SHA-1 hash usage", "CWE-327"),
            (r'random\.random\(\)', "Insecure random number generation", "CWE-338"),
        ]
        for pattern, title, cwe in weak_patterns:
            for match in re.finditer(pattern, content):
                line_num = content.count('\n', 0, match.start()) + 1
                self.add_finding(
                    severity="MEDIUM", category="Cryptography", title=title,
                    description="Usage of a weak or insecure cryptographic algorithm.",
                    file_path=file_path, line_number=line_num,
                    code_snippet=lines[line_num-1].strip(),
                    recommendation="Use stronger, modern alternatives (e.g., SHA-256, secrets module).", cwe_id=cwe
                )

    def check_debug_info(self, file_path: str, content: str, lines: List[str]):
        if 'config.py' in file_path and 'DEBUG = True' in content:
            line_num = content.find('DEBUG = True')
            line_num = content.count('\n', 0, line_num) + 1
            self.add_finding(
                severity="HIGH", category="Configuration", title="Debug Mode Enabled",
                description="The application may be running in debug mode, which can expose sensitive information.",
                file_path=file_path, line_number=line_num,
                code_snippet="DEBUG = True",
                recommendation="Ensure DEBUG is set to False in production environments.", cwe_id="CWE-215"
            )


    def check_missing_permissions(self, tree, file_path):
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
                self._add_issue(
                    file_path,
                    node.lineno,
                    'Endpoint Missing Permissions',
                    f"L'endpoint '{node.name}' semble ne pas avoir de décorateur d'autorisation.",
                    'HIGH'
                )
                

    def check_secure_cookies(self, file_path: str, content: str, lines: List[str]):
        if 'config.py' not in file_path:
            return
        
        secure_settings = {
            "SESSION_COOKIE_SECURE": 'True',
            "SESSION_COOKIE_HTTPONLY": 'True',
            "SESSION_COOKIE_SAMESITE": "'Strict'",
        }
        for key, expected in secure_settings.items():
            if key not in content:
                self.add_finding(
                    severity="MEDIUM", category="Configuration", title=f"Missing Secure Cookie Setting: {key}",
                    description=f"The setting {key} is not defined, which can lead to session vulnerabilities.",
                    file_path=file_path, line_number=1, recommendation=f"Set {key} = {expected} in your Flask config.", cwe_id="CWE-614"
                )

    def check_xss_vulnerabilities(self, file_path: str, content: str, lines: List[str]):
        # Simple check for v-html, a common source of XSS in Vue
        for match in re.finditer(r'v-html=', content):
            line_num = content.count('\n', 0, match.start()) + 1
            line = lines[line_num - 1]
            # A more advanced check would trace the variable, but for now, we flag all uses.
            self.add_finding(
                severity="HIGH", category="XSS", title="Potential XSS with v-html",
                description="The 'v-html' directive can expose your application to XSS if the content is user-provided.",
                file_path=file_path, line_number=line_num,
                code_snippet=line.strip(),
                recommendation="Avoid v-html. If necessary, use a library like DOMPurify to sanitize the HTML.",
                cwe_id="CWE-79"
            )

    def check_https_enforcement(self, file_path: str, content: str, lines: List[str]):
        # Finds hardcoded http:// links
        for match in re.finditer(r'["\']http://(?!localhost|127\.0\.0\.1)', content):
             line_num = content.count('\n', 0, match.start()) + 1
             self.add_finding(
                severity="MEDIUM", category="Transport Security", title="Insecure HTTP URL",
                description="A hardcoded HTTP URL was found. All external resources should be loaded over HTTPS.",
                file_path=file_path, line_number=line_num,
                code_snippet=lines[line_num-1].strip(),
                recommendation="Replace 'http://' with 'https://'.", cwe_id="CWE-319"
             )
    
    def check_for_var_keyword(self, file_path: str, lines: List[str]):
        for i, line in enumerate(lines):
            # A simple regex to find 'var' but not as part of another word like 'variable'.
            if re.search(r'\bvar\b', line):
                self.add_finding(
                    severity="LOW", category="Code Quality", title="Outdated 'var' keyword",
                    description="The 'var' keyword is outdated and has function-scoping issues.",
                    file_path=file_path, line_number=i + 1,
                    code_snippet=line.strip(),
                    recommendation="Use 'let' for variables that will be reassigned, or 'const' for constant variables."
                )

    # --- MAIN EXECUTION METHOD ---

    def run_audit(self):
        """Runs the complete security audit."""
        self._print_header("Starting Comprehensive Security Audit")

        # 1. Dependency and Tool Scans
        self.run_pip_audit()
        self.run_npm_audit()
        self.run_bandit_scan()
        
        # 2. Custom Static Code Analysis
        self._print_header("Running Custom Static Code Analysis")
        files_to_scan = self.find_files_to_scan()
        logging.info(f"Found {len(files_to_scan)} files to analyze.")
        
        for file_path in files_to_scan:
            logging.debug(f"Scanning: {file_path}")
            self.analyze_file(file_path)
            
        # 3. Final Report
        self._print_header("Audit Summary")
        if not self.findings:
            print(f"{Colors.GREEN}✔ No security issues found.{Colors.ENDC}")
        else:
            print(f"{Colors.RED}Found {len(self.findings)} potential issues.{Colors.ENDC}")
            
            # Sort findings by severity
            severity_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
            self.findings.sort(key=lambda f: severity_order.get(f.severity, 99))
            
            # Optionally, write to a file
            if self.config.output_file:
                output_data = [f.to_dict() for f in self.findings]
                try:
                    with open(self.config.output_file, 'w') as f:
                        json.dump(output_data, f, indent=4)
                    print(f"Report saved to {self.config.output_file}")
                except Exception as e:
                    logging.error(f"Failed to write report to file: {e}")

        print(f"\n{Colors.HEADER}{Colors.BOLD}===== Audit Finished ====={Colors.ENDC}")
        return len(self.findings)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Comprehensive Security Audit Tool.")
    parser.add_argument(
        '-o', '--output-file',
        help="Path to save the JSON report file."
    )
    parser.add_argument(
        '--skip-dependency-check',
        action='store_true',
        help="Skip pip-audit and npm-audit scans."
    )
    parser.add_argument(
        '--skip-static-analysis',
        action='store_true',
        help="Skip the Bandit scan."
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help="Enable verbose logging."
    )
    
    args = parser.parse_args()

    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=log_level, format='[%(levelname)s] %(message)s')

    auditor = SecurityAuditor(config=args)
    num_issues = auditor.run_audit()

    # Exit with a non-zero status code if issues were found
    if num_issues > 0:
        sys.exit(1)
    else:
        sys.exit(0)
