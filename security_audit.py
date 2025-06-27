#!/usr/bin/env python3
import os
import re
import subprocess
import json
from typing import List, Tuple, Dict

# --- Configuration ---
# Directories to scan
BACKEND_DIR = 'backend'
FRONTEND_DIR = 'website'
# Bandit configuration: -r for recursive, -f json for format, -ll for medium/high severity
BANDIT_CMD = [
    sys.executable, '-m', 'bandit', '-r', BACKEND_DIR, 
    '-f', 'json', '-ll', '-c', 'bandit.yaml'
]
# npm audit configuration
NPM_CMD = ['npm', 'audit', '--json']

# ANSI color codes for better readability
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(title):
    """Prints a styled header."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}===== {title} ====={Colors.ENDC}")

def run_command(command, cwd='.'):
    """Runs a shell command and returns its output."""
    try:
        print(f"{Colors.OKBLUE}Running command: {' '.join(command)}{Colors.ENDC}")
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True,
            cwd=cwd
        )
        return result.stdout
    except FileNotFoundError:
        print(f"{Colors.FAIL}Error: Command '{command[0]}' not found.{Colors.ENDC}")
        if command[0] == 'npm':
            print(f"{Colors.WARNING}Please ensure Node.js and npm are installed and in your system's PATH.{Colors.ENDC}")
        elif 'bandit' in command:
            print(f"{Colors.WARNING}Please install bandit: pip install bandit{Colors.ENDC}")
        return None
    except subprocess.CalledProcessError as e:
        # npm audit returns a non-zero exit code if vulnerabilities are found.
        # This is expected behavior, so we return the output for parsing.
        if command[0] == 'npm' and e.stdout:
            return e.stdout
        print(f"{Colors.FAIL}Error executing command: {' '.join(command)}{Colors.ENDC}")
        print(e.stderr)
        return None

def run_bandit_scan():
    """Runs the Bandit static analysis scan on the backend."""
    print_header("Backend Security Scan (Bandit)")
    
    # Create a default bandit.yaml if it doesn't exist to exclude test files
    if not os.path.exists('bandit.yaml'):
        with open('bandit.yaml', 'w') as f:
            f.write("skips: ['B101']\n")
            f.write("tests: ['B101']\n")
            f.write("exclude_dirs: ['/tests', '/venv']\n")

    output = run_command(BANDIT_CMD)
    if not output:
        return 0

    try:
        report = json.loads(output)
        issues = report.get('results', [])
        
        if not issues:
            print(f"{Colors.OKGREEN}✔ No high or medium severity issues found.{Colors.ENDC}")
            return 0
        
        print(f"{Colors.FAIL}Found {len(issues)} potential issues:{Colors.ENDC}")
        for issue in issues:
            print(f"\n  {Colors.WARNING}File: {issue['filename']}:{issue['line_number']}{Colors.ENDC}")
            print(f"  Issue: {issue['issue_text']} (Severity: {issue['issue_severity']})")
            print(f"  Confidence: {issue['issue_confidence']}")
            print(f"  Code: {issue['code'].strip()}")
            print(f"  More Info: {issue['more_info']}")
        
        return len(issues)
    except json.JSONDecodeError:
        print(f"{Colors.FAIL}Error: Could not decode Bandit JSON output.{Colors.ENDC}")
        return 0

def run_npm_audit():
    """Runs npm audit to check for vulnerabilities in frontend dependencies."""
    print_header("Frontend Dependency Scan (npm audit)")
    
    if not os.path.isdir(FRONTEND_DIR):
        print(f"{Colors.FAIL}Frontend directory '{FRONTEND_DIR}' not found.{Colors.ENDC}")
        return 0

    output = run_command(NPM_CMD, cwd=FRONTEND_DIR)
    if not output:
        return 0

    try:
        report = json.loads(output)
        vulnerabilities = report.get('vulnerabilities', {})
        total_vulnerabilities = report.get('metadata', {}).get('vulnerabilities', {})
        
        if not vulnerabilities:
            print(f"{Colors.OKGREEN}✔ No vulnerabilities found in npm packages.{Colors.ENDC}")
            return 0
        
        summary = ", ".join([f"{count} {level}" for level, count in total_vulnerabilities.items() if count > 0])
        print(f"{Colors.FAIL}Found vulnerabilities: {summary}{Colors.ENDC}")
        
        for name, details in vulnerabilities.items():
            print(f"\n  {Colors.WARNING}Package: {name}{Colors.ENDC} (Severity: {details['severity']})")
            print(f"  Affected versions: {details['range']}")
            via = [v['name'] for v in details.get('via', []) if isinstance(v, dict)]
            if via:
                print(f"  Dependency of: {', '.join(via)}")
            if details.get('fixAvailable'):
                 print(f"  {Colors.OKGREEN}Fix: Run 'npm audit fix' in the '{FRONTEND_DIR}' directory.{Colors.ENDC}")

        return sum(total_vulnerabilities.values())
        
    except json.JSONDecodeError:
        print(f"{Colors.FAIL}Error: Could not decode npm audit JSON output. Is npm installed and is '{FRONTEND_DIR}' a valid npm project?{Colors.ENDC}")
        return 0


def print_header(title: str):
    print(f"\n{Colors.BLUE}{Colors.BOLD}===== {title.upper()} ====={Colors.RESET}")

def print_finding(level: str, message: str, file_path: str, line_num: int):
    color = {
        "HIGH": Colors.RED,
        "MEDIUM": Colors.YELLOW,
        "LOW": Colors.BLUE
    }.get(level, Colors.RESET)
    print(f"[{color}{level.upper()}{Colors.RESET}] {message}\n    -> {file_path}:{line_num}")

def find_files(directory: str, extension: str) -> List[str]:
    """Finds all files with a given extension in a directory."""
    matches = []
    for root, _, filenames in os.walk(directory):
        for filename in filenames:
            if filename.endswith(extension):
                matches.append(os.path.join(root, filename))
    return matches

# --- Backend Checks ---

def check_missing_permissions(py_files: List[str]):
    """
    Scans Flask route files for endpoints missing authorization decorators.
    """
    print_header("Checking for Missing Endpoint Permissions")
    found_issues = 0
    permission_decorators = [
        '@permissions_required',
        '@admin_required',
        '@staff_required',
        '@b2b_user_required',
        '@jwt_required'
    ]

    for file_path in py_files:
        if 'routes' not in file_path:
            continue

        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        for i, line in enumerate(lines):
            # Find a Flask route decorator
            if re.search(r'@\w+_bp\.route\(', line) or re.search(r'@\w+\.route\(', line):
                is_protected = False
                # Check the next few lines for a permission decorator
                for j in range(i - 1, max(-1, i - 5), -1):
                    # Check if any of the decorators are in the line preceeding the route
                    if any(dec in lines[j] for dec in permission_decorators):
                        is_protected = True
                        break
                
                if not is_protected:
                    # Check the line itself (for optional JWT)
                    if '@jwt_required(optional=True)' in line:
                       continue
                    print_finding("HIGH", "Endpoint defined without a permission decorator.", file_path, i + 1)
                    found_issues += 1
    
    if found_issues == 0:
        print(f"{Colors.GREEN}✔ No unprotected endpoints found.{Colors.RESET}")

def check_unsanitized_input(py_files: List[str]):
    """
    Scans for direct usage of request data without apparent sanitization.
    This is a pattern-based check and may include false positives.
    """
    print_header("Checking for Potentially Unsanitized Input")
    found_issues = 0
    # Patterns for detecting usage of Flask's request objects
    input_patterns = re.compile(r"request\.(get_json|args|form|values|data)")
    
    for file_path in py_files:
        if 'routes' not in file_path:
            continue
            
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        for match in input_patterns.finditer(content):
            line_num = content.count('\n', 0, match.start()) + 1
            line_content = content.splitlines()[line_num - 1]
            
            # Check if 'sanitize_input' is used on the same line. A simple but effective check.
            if 'sanitize_input' not in line_content:
                # Exclude known safe files or lines if necessary
                if 'password' in line_content.lower(): # Passwords shouldn't be sanitized this way
                    continue
                print_finding("MEDIUM", "Direct use of request object detected. Ensure data is sanitized.", file_path, line_num)
                found_issues += 1

    if found_issues == 0:
        print(f"{Colors.GREEN}✔ No obvious unsanitized input patterns found.{Colors.RESET}")

def check_secure_cookies(config_file: str):
    """
    Checks Flask configuration for secure cookie settings.
    """
    print_header("Checking for Secure Cookie Configuration")
    if not os.path.exists(config_file):
        print(f"{Colors.YELLOW}Config file '{config_file}' not found. Skipping check.{Colors.RESET}")
        return

    with open(config_file, 'r', encoding='utf-8') as f:
        content = f.read()

    secure_settings = {
        "SESSION_COOKIE_SECURE": True,
        "SESSION_COOKIE_HTTPONLY": True,
        "SESSION_COOKIE_SAMESITE": "'Strict'", # Or 'Lax'
        "REMEMBER_COOKIE_SECURE": True,
        "REMEMBER_COOKIE_HTTPONLY": True,
    }
    
    found_issues = 0
    for key, expected_value in secure_settings.items():
        pattern = re.compile(rf"{key}\s*=\s*(.*)")
        match = pattern.search(content)
        if not match:
            print_finding("MEDIUM", f"Cookie setting '{key}' is not defined.", config_file, 1)
            found_issues += 1
        elif str(expected_value) not in match.group(1):
            line_num = content.count('\n', 0, match.start()) + 1
            print_finding("HIGH", f"Insecure cookie setting for '{key}'. Expected {expected_value}.", config_file, line_num)
            found_issues += 1

    if found_issues == 0:
        print(f"{Colors.GREEN}✔ Cookie configurations appear secure.{Colors.RESET}")

# --- Frontend Checks ---

def check_xss_vulnerabilities(vue_files: List[str]):
    """
    Scans Vue files for use of `v-html` without sanitization.
    """
    print_header("Checking for Potential XSS Vulnerabilities in Vue Files")
    found_issues = 0
    for file_path in vue_files:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Simple regex to find v-html usages
        for match in re.finditer(r'v-html="([^"]+)"', content):
            line_num = content.count('\n', 0, match.start()) + 1
            variable_name = match.group(1)
            
            # Check if the variable is being sanitized in the script section
            script_content_match = re.search(r'<script.*?>([\s\S]*?)<\/script>', content)
            is_sanitized = False
            if script_content_match:
                script_content = script_content_match.group(1)
                # This is a heuristic check. It looks for 'sanitizeHTML(variable)'
                if re.search(rf'sanitizeHTML\(\s*{re.escape(variable_name)}\s*\)', script_content, re.IGNORECASE):
                    is_sanitized = True
                elif re.search(rf'{re.escape(variable_name)}\s*=\s*sanitizeHTML\(', script_content, re.IGNORECASE):
                    is_sanitized = True
            
            if not is_sanitized:
                print_finding("HIGH", f"v-html used with unsanitized variable '{variable_name}'.", file_path, line_num)
                found_issues += 1
    
    if found_issues == 0:
        print(f"{Colors.GREEN}✔ No unsanitized v-html uses found.{Colors.RESET}")


def check_dependency_vulnerabilities(directory: str, command: str):
    """
    Runs a dependency vulnerability scanner (like npm audit or pip-audit).
    """
    print_header(f"Checking for Dependency Vulnerabilities in '{directory}'")
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            cwd=directory
        )
        
        if "found 0 vulnerabilities" in result.stdout or "found 0 vulnerabilities" in result.stderr:
            print(f"{Colors.GREEN}✔ No vulnerabilities found.{Colors.RESET}")
        elif "vulnerabilities found" in result.stdout or "vulnerabilities found" in result.stderr:
             print(f"{Colors.RED}Vulnerabilities found! Run '{command}' in '{directory}' for details.{Colors.RESET}")
             print(result.stdout)
        else:
            print(f"{Colors.YELLOW}Could not determine vulnerability status. Please run '{command}' manually.{Colors.RESET}")

    except FileNotFoundError:
        print(f"{Colors.YELLOW}Command for '{command}' not found. Skipping dependency check.{Colors.RESET}")
    except Exception as e:
        print(f"{Colors.RED}An error occurred while running dependency audit: {e}{Colors.RESET}")


if __name__ == '__main__':
    print(f"{Colors.BOLD}Starting security audit...{Colors.RESET}")

    # --- Backend Audit ---
    if os.path.isdir(BACKEND_DIR):
        print_header("BACKEND AUDIT")
        backend_py_files = find_files(BACKEND_DIR, '.py')
        check_missing_permissions(backend_py_files)
        check_unsanitized_input(backend_py_files)
        check_secure_cookies(os.path.join(BACKEND_DIR, 'config.py'))
        check_dependency_vulnerabilities(BACKEND_DIR, "pip-audit")
    else:
        print(f"{Colors.YELLOW}Backend directory '{BACKEND_DIR}' not found. Skipping backend checks.{Colors.RESET}")

    # --- Frontend Audit ---
    if os.path.isdir(FRONTEND_DIR):
        print_header("FRONTEND AUDIT")
        vue_files = find_files(FRONTEND_DIR, '.vue')
        check_xss_vulnerabilities(vue_files)
        check_dependency_vulnerabilities(FRONTEND_DIR, "npm audit")
    else:
        print(f"{Colors.YELLOW}Frontend directory '{FRONTEND_DIR}' not found. Skipping frontend checks.{Colors.RESET}")

    print(f"\n{Colors.BOLD}Audit complete.{Colors.RESET}")



def main():
    """Main function to run all security audits."""
    print(f"{Colors.BOLD}Starting Comprehensive Security Audit...{Colors.ENDC}")
    
    bandit_issues = run_bandit_scan()
    npm_issues = run_npm_audit()
    
    total_issues = bandit_issues + npm_issues
    
    print_header("Audit Summary")
    if total_issues == 0:
        print(f"{Colors.OKGREEN}{Colors.BOLD}✔ Congratulations! The security audit passed with no high/medium severity issues found.{Colors.ENDC}")
        sys.exit(0)
    else:
        print(f"{Colors.FAIL}{Colors.BOLD}✖ Security audit failed with a total of {total_issues} issues found.{Colors.ENDC}")
        print(f"  - Backend (Bandit): {bandit_issues} issues")
        print(f"  - Frontend (npm): {npm_issues} vulnerabilities")
        print(f"{Colors.WARNING}Please review the findings above and address them accordingly.{Colors.ENDC}")
        sys.exit(1)


if __name__ == "__main__":
    main()
