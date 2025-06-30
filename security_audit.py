#!/usr/bin/env python3
import os
import re
import subprocess
import json
import sys
import hashlib
import datetime
import argparse
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, asdict
import logging
import os
import ast


# --- CONFIGURATION ---
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

BACKEND_DIR = os.path.join(PROJECT_ROOT, 'backend')
FRONTEND_DIR = os.path.join(PROJECT_ROOT, 'website')

excluded_dirs = [".venv", "__pycache__", "node_modules", ".git", "migrations"]

# Répertoires à analyser (chemins absolus).
SCAN_DIRECTORIES = [
    os.path.join(PROJECT_ROOT, 'backend'),
    os.path.join(PROJECT_ROOT, 'website')
]

# Chemins à exclure, convertis en chemins absolus pour une correspondance fiable.
EXCLUDED_PATHS = [
    os.path.abspath(os.path.join(PROJECT_ROOT, p)) for p in [
        'backend/migrations',
        'backend/tests',
        'backend/__pycache__',
        'website/node_modules',
        'website/dist'
    ]
]

# Décorateurs qui signalent qu'une route est protégée.
PERMISSION_DECORATORS = [
    '@jwt_required',
    '@roles_required',
    '@permissions_required',
    '@admin_required',
    '@staff_required',
    '@b2b_user_required',
    '@b2b_admin_required',
    '@login_required' # En supposant un décorateur personnalisé
]
# Routes qui sont publiquement accessibles par conception et qui doivent être ignorées.
PUBLIC_ROUTES = [
    r"@auth_bp\.route\('/login'",
    r"@auth_bp\.route\('/register'",
    r"@auth_bp\.route\('/refresh'",
    r"@csrf_bp\.route\('/get-csrf-token'",
    # Ajoutez ici d'autres routes publiques si nécessaire
]

# Security finding data structure
@dataclass
class SecurityFinding:
    severity: str  # HIGH, MEDIUM, LOW, INFO
    category: str  # e.g., "Authentication", "Input Validation", "Dependencies"
    title: str
    description: str
    file_path: str
    line_number: int
    code_snippet: str = ""
    recommendation: str = ""
    cwe_id: Optional[str] = None  # Common Weakness Enumeration ID
    
    def to_dict(self):
        return asdict(self)

# Audit configuration
@dataclass
class AuditConfig:
    include_low_severity: bool = False
    output_format: str = "console"  # console, json, html
    output_file: Optional[str] = None
    skip_dependency_check: bool = False
    skip_static_analysis: bool = False
    custom_rules_file: Optional[str] = None
    
# Global findings list
findings: List[SecurityFinding] = []

# ANSI color codes for better readability
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(title):
    """Prints a styled header."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}===== {title.upper()} ====={Colors.ENDC}")

def run_command(command, cwd='.'):
    """Runs a shell command and returns its output."""
    try:
        print(f"{Colors.BLUE}Running command: {' '.join(command)}{Colors.ENDC}")
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True,
            cwd=cwd
        )
        return result.stdout
    except FileNotFoundError:
        print(f"{Colors.RED}Error: Command '{command[0]}' not found.{Colors.ENDC}")
        if command[0] == 'npm':
            print(f"{Colors.YELLOW}Please ensure Node.js and npm are installed and in your system's PATH.{Colors.ENDC}")
        elif 'bandit' in command:
            print(f"{Colors.YELLOW}Please install bandit: pip install bandit{Colors.ENDC}")
        elif 'pip_audit' in command:
            print(f"{Colors.YELLOW}Please install pip-audit: pip install pip-audit{Colors.ENDC}")
        return None
    except subprocess.CalledProcessError as e:
        # Some audit tools return a non-zero exit code if vulnerabilities are found.
        # This is expected behavior, so we return the output for parsing.
        if (command[0] == 'npm' or 'pip_audit' in command) and e.stdout:
            return e.stdout
        print(f"{Colors.RED}Error executing command: {' '.join(command)}{Colors.ENDC}")
        print(e.stderr)
        return None

def run_bandit_scan():
    """Runs the Bandit static analysis scan on the backend."""
    print_header("Backend Security Scan (Bandit)")

    if not os.path.isdir(BACKEND_DIR):
        print(f"{Colors.YELLOW}Backend directory '{BACKEND_DIR}' not found. Skipping.{Colors.ENDC}")
        return 0

    # Create a default bandit.yaml if it doesn't exist to exclude test files
    if not os.path.exists('bandit.yaml'):
        with open('bandit.yaml', 'w') as f:
            f.write("skips: ['B101']\nexclude_dirs: ['/tests', '/venv']\n")

    bandit_cmd = [sys.executable, '-m', 'bandit', '-r', BACKEND_DIR, '-f', 'json', '-ll', '-c', 'bandit.yaml']
    output = run_command(bandit_cmd)
    if not output:
        return 0

    try:
        report = json.loads(output)
        issues = report.get('results', [])
        
        if not issues:
            print(f"{Colors.GREEN}✔ No high or medium severity issues found.{Colors.ENDC}")
            return 0
        
        print(f"{Colors.RED}Found {len(issues)} potential issues:{Colors.ENDC}")
        for issue in issues:
            print(f"\n  {Colors.YELLOW}File: {issue['filename']}:{issue['line_number']}{Colors.ENDC}")
            print(f"  Issue: {issue['issue_text']} (Severity: {issue['issue_severity']})")
            print(f"  Confidence: {issue['issue_confidence']}")
            print(f"  Code: {issue['code'].strip()}")
            print(f"  More Info: {issue['more_info']}")
        
        return len(issues)
    except json.JSONDecodeError:
        print(f"{Colors.RED}Error: Could not decode Bandit JSON output.{Colors.ENDC}")
        return 1

def run_npm_audit():
    """Runs npm audit to check for vulnerabilities in frontend dependencies."""
    print_header("Frontend Dependency Scan (npm audit)")
    
    if not os.path.isdir(FRONTEND_DIR):
        print(f"{Colors.YELLOW}Frontend directory '{FRONTEND_DIR}' not found. Skipping.{Colors.ENDC}")
        return 0

    npm_cmd = ['npm', 'audit', '--json']
    output = run_command(npm_cmd, cwd=FRONTEND_DIR)
    if not output:
        return 0

    try:
        report = json.loads(output)
        vulnerabilities = report.get('vulnerabilities', {})
        total_vulnerabilities = report.get('metadata', {}).get('vulnerabilities', {})
        
        if not vulnerabilities:
            print(f"{Colors.GREEN}✔ No vulnerabilities found in npm packages.{Colors.ENDC}")
            return 0
        
        summary = ", ".join([f"{count} {level}" for level, count in total_vulnerabilities.items() if count > 0])
        print(f"{Colors.RED}Found vulnerabilities: {summary}{Colors.ENDC}")
        
        for name, details in vulnerabilities.items():
            print(f"\n  {Colors.YELLOW}Package: {name}{Colors.ENDC} (Severity: {details['severity']})")
            print(f"  Affected versions: {details['range']}")
            via = [v['name'] for v in details.get('via', []) if isinstance(v, dict)]
            if via:
                print(f"  Dependency of: {', '.join(via)}")
            if details.get('fixAvailable'):
                 print(f"  {Colors.GREEN}Fix: Run 'npm audit fix' in the '{FRONTEND_DIR}' directory.{Colors.ENDC}")

        return sum(total_vulnerabilities.values())
        
    except json.JSONDecodeError:
        print(f"{Colors.RED}Error: Could not decode npm audit JSON output. Is npm installed and is '{FRONTEND_DIR}' a valid npm project?{Colors.ENDC}")
        return 1

def run_pip_audit():
    """Runs pip-audit to check for vulnerabilities in backend dependencies."""
    print_header("Backend Dependency Scan (pip-audit)")

    req_file = os.path.join(BACKEND_DIR, 'requirements.txt')
    if not os.path.exists(req_file):
        req_file = 'requirements.txt' # Check root as a fallback
        if not os.path.exists(req_file):
            print(f"{Colors.YELLOW}Could not find requirements.txt in '{BACKEND_DIR}' or root. Skipping pip-audit.{Colors.ENDC}")
            return 0

    command = [sys.executable, '-m', 'pip_audit', '--json', '-r', req_file]
    output = run_command(command)
    if not output:
        return 1

    try:
        report = json.loads(output)
        vulnerabilities = report.get('dependencies', [])
        vuln_count = 0
        found_vulnerabilities = [dep for dep in vulnerabilities if dep.get('vulns')]

        if not found_vulnerabilities:
            print(f"{Colors.GREEN}✔ No vulnerabilities found in Python packages.{Colors.ENDC}")
            return 0

        for dep in found_vulnerabilities:
            vuln_count += len(dep['vulns'])

        print(f"{Colors.RED}Found {vuln_count} vulnerabilities in Python packages:{Colors.ENDC}")
        for dep in found_vulnerabilities:
            print(f"\n  {Colors.YELLOW}Package: {dep['name']}=={dep['version']}{Colors.ENDC}")
            for vuln in dep['vulns']:
                fix_versions = ", ".join(vuln.get('fix_versions', []))
                print(f"  - ID: {vuln['id']} | Fix available in: {fix_versions or 'N/A'}")
                print(f"    Description: {vuln['description']}")
        return vuln_count
    except json.JSONDecodeError:
        print(f"{Colors.RED}Error: Could not decode pip-audit JSON output.{Colors.ENDC}")
        return 1

def add_finding(severity: str, category: str, title: str, description: str, 
                file_path: str, line_number: int, code_snippet: str = "", 
                recommendation: str = "", cwe_id: Optional[str] = None):
    """Add a security finding to the global findings list."""
    finding = SecurityFinding(
        severity=severity,
        category=category,
        title=title,
        description=description,
        file_path=file_path,
        line_number=line_number,
        code_snippet=code_snippet,
        recommendation=recommendation,
        cwe_id=cwe_id
    )
    findings.append(finding)

def print_finding(level: str, message: str, file_path: str, line_num: int):
    color = {
        "HIGH": Colors.RED, "MEDIUM": Colors.YELLOW, "LOW": Colors.BLUE
    }.get(level.upper(), Colors.ENDC)
    print(f"[{color}{level.upper()}{Colors.ENDC}] {message}\n    -> {file_path}:{line_num}")

def find_files(directory: str, extension: str) -> List[str]:
    """Finds all files with a given extension in a directory."""
    matches = []
    for root, _, filenames in os.walk(directory, topdown=True):
        for filename in filenames:
            if filename.endswith(extension):
                matches.append(os.path.join(root, filename))
    return matches

# --- Backend Checks ---

def check_missing_permissions(py_files: List[str]) -> int:
    """
    Scans Flask route files for endpoints missing authorization decorators.
    """
    print_header("Custom Check: Missing Endpoint Permissions")
    found_issues = 0
    permission_decorators = [
        '@permissions_required',
        '@roles_required',
        '@admin_required',
        '@staff_required',
        '@b2b_user_required',
        '@b2b_admin_required',
        '@jwt_required'
    ]

    for file_path in py_files:
        # Target files with 'routes' in their name, but exclude some common false positives
        if 'routes' not in file_path or 'node_modules' in file_path:
            continue

        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        for i, line in enumerate(lines):
            # Find a Flask route decorator
            if re.search(r'@\w+_bp\.route\(', line) or re.search(r'@\w+\.route\(', line):
                is_protected = False
                # Check the next few lines for a permission decorator
                for j in range(i, max(-1, i - 5), -1):
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
        print(f"{Colors.GREEN}✔ No unprotected endpoints found.{Colors.ENDC}")
    return found_issues

def check_unsanitized_input(py_files: List[str]) -> int:
    """
    Scans for direct usage of request data without apparent sanitization.
    This is a pattern-based check and may include false positives.
    """
    print_header("Custom Check: Potentially Unsanitized Input")
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
        print(f"{Colors.GREEN}✔ No obvious unsanitized input patterns found.{Colors.ENDC}")

def check_secure_cookies(config_file: str):
    """
    Checks Flask configuration for secure cookie settings.
    """
    print_header("Checking for Secure Cookie Configuration")
    if not os.path.exists(config_file):
        print(f"{Colors.YELLOW}Config file '{config_file}' not found. Skipping check.{Colors.ENDC}")
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
        print(f"{Colors.GREEN}✔ Cookie configurations appear secure.{Colors.ENDC}")

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
        print(f"{Colors.GREEN}✔ No unsanitized v-html uses found.{Colors.ENDC}")


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
            print(f"{Colors.GREEN}✔ No vulnerabilities found.{Colors.ENDC}")
        elif "vulnerabilities found" in result.stdout or "vulnerabilities found" in result.stderr:
             print(f"{Colors.RED}Vulnerabilities found! Run '{command}' in '{directory}' for details.{Colors.ENDC}")
             print(result.stdout)
        else:
            print(f"{Colors.YELLOW}Could not determine vulnerability status. Please run '{command}' manually.{Colors.ENDC}")

    except FileNotFoundError:
        print(f"{Colors.YELLOW}Command for '{command}' not found. Skipping dependency check.{Colors.ENDC}")
    except Exception as e:
        print(f"{Colors.RED}An error occurred while running dependency audit: {e}{Colors.ENDC}")

# --- Enhanced Security Checks ---

def check_hardcoded_secrets(files: List[str]) -> int:
    """Check for hardcoded secrets, API keys, passwords, etc."""
    print_header("Enhanced Check: Hardcoded Secrets Detection")
    found_issues = 0
    
    # Common patterns for secrets
    secret_patterns = [
        (r'password\s*=\s*["\'][^"\']{8,}["\']', "Hardcoded Password", "CWE-798"),
        (r'api[_-]?key\s*=\s*["\'][^"\']{16,}["\']', "Hardcoded API Key", "CWE-798"),
        (r'secret[_-]?key\s*=\s*["\'][^"\']{16,}["\']', "Hardcoded Secret Key", "CWE-798"),
        (r'token\s*=\s*["\'][^"\']{20,}["\']', "Hardcoded Token", "CWE-798"),
        (r'aws[_-]?access[_-]?key[_-]?id\s*=\s*["\'][^"\']+["\']', "AWS Access Key", "CWE-798"),
        (r'aws[_-]?secret[_-]?access[_-]?key\s*=\s*["\'][^"\']+["\']', "AWS Secret Key", "CWE-798"),
        (r'database[_-]?url\s*=\s*["\'].*://.*:.*@.*["\']', "Database URL with Credentials", "CWE-798"),
        (r'smtp[_-]?password\s*=\s*["\'][^"\']+["\']', "SMTP Password", "CWE-798"),
    ]
    
    for file_path in files:
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.splitlines()
            
            for pattern, title, cwe_id in secret_patterns:
                for match in re.finditer(pattern, content, re.IGNORECASE):
                    line_num = content.count('\n', 0, match.start()) + 1
                    line_content = lines[line_num - 1].strip() if line_num <= len(lines) else ""
                    
                    # Skip if it's a comment or example
                    if line_content.strip().startswith('#') or 'example' in line_content.lower():
                        continue
                    
                    add_finding(
                        severity="HIGH",
                        category="Secrets Management",
                        title=title,
                        description=f"Potential hardcoded secret detected: {match.group()}",
                        file_path=file_path,
                        line_number=line_num,
                        code_snippet=line_content,
                        recommendation="Use environment variables or secure secret management systems",
                        cwe_id=cwe_id
                    )
                    print_finding("HIGH", f"{title} detected", file_path, line_num)
                    found_issues += 1
                    
        except Exception as e:
            print(f"{Colors.YELLOW}Warning: Could not read file {file_path}: {e}{Colors.ENDC}")
    
    if found_issues == 0:
        print(f"{Colors.GREEN}✔ No hardcoded secrets detected.{Colors.ENDC}")
    return found_issues

def check_sql_injection_patterns(py_files: List[str]) -> int:
    """Check for potential SQL injection vulnerabilities."""
    print_header("Enhanced Check: SQL Injection Patterns")
    found_issues = 0
    
    # Patterns that might indicate SQL injection vulnerabilities
    sql_patterns = [
        (r'execute\s*\(\s*["\'].*%s.*["\'].*%', "String formatting in SQL execute"),
        (r'execute\s*\(\s*f["\'].*\{.*\}.*["\']', "f-string in SQL execute"),
        (r'query\s*\(\s*["\'].*%s.*["\'].*%', "String formatting in SQL query"),
        (r'query\s*\(\s*f["\'].*\{.*\}.*["\']', "f-string in SQL query"),
        (r'\.format\s*\(.*\).*execute', "String format with execute"),
        (r'SELECT.*\+.*FROM', "String concatenation in SELECT"),
        (r'INSERT.*\+.*VALUES', "String concatenation in INSERT"),
        (r'UPDATE.*\+.*SET', "String concatenation in UPDATE"),
        (r'DELETE.*\+.*FROM', "String concatenation in DELETE"),
    ]
    
    for file_path in py_files:
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.splitlines()
            
            for pattern, description in sql_patterns:
                for match in re.finditer(pattern, content, re.IGNORECASE):
                    line_num = content.count('\n', 0, match.start()) + 1
                    line_content = lines[line_num - 1].strip() if line_num <= len(lines) else ""
                    
                    add_finding(
                        severity="HIGH",
                        category="Input Validation",
                        title="Potential SQL Injection",
                        description=f"{description}: {match.group()}",
                        file_path=file_path,
                        line_number=line_num,
                        code_snippet=line_content,
                        recommendation="Use parameterized queries or ORM methods",
                        cwe_id="CWE-89"
                    )
                    print_finding("HIGH", f"Potential SQL injection: {description}", file_path, line_num)
                    found_issues += 1
                    
        except Exception as e:
            print(f"{Colors.YELLOW}Warning: Could not read file {file_path}: {e}{Colors.ENDC}")
    
    if found_issues == 0:
        print(f"{Colors.GREEN}✔ No obvious SQL injection patterns found.{Colors.ENDC}")
    return found_issues

def check_weak_crypto_patterns(files: List[str]) -> int:
    """Check for weak cryptographic practices."""
    print_header("Enhanced Check: Weak Cryptography")
    found_issues = 0
    
    weak_crypto_patterns = [
        (r'hashlib\.md5\(', "MD5 hash usage", "Use SHA-256 or stronger", "CWE-327"),
        (r'hashlib\.sha1\(', "SHA-1 hash usage", "Use SHA-256 or stronger", "CWE-327"),
        (r'random\.random\(\)', "Weak random number generation", "Use secrets module for cryptographic purposes", "CWE-338"),
        (r'DES\.new\(', "DES encryption", "Use AES or stronger encryption", "CWE-327"),
        (r'RC4\.new\(', "RC4 encryption", "Use AES or stronger encryption", "CWE-327"),
        (r'ssl\.PROTOCOL_TLS', "Deprecated SSL protocol", "Use TLS 1.2 or higher", "CWE-327"),
        (r'ssl_version\s*=\s*ssl\.PROTOCOL_SSLv', "SSL version usage", "Use TLS 1.2 or higher", "CWE-327"),
    ]
    
    for file_path in files:
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.splitlines()
            
            for pattern, title, recommendation, cwe_id in weak_crypto_patterns:
                for match in re.finditer(pattern, content):
                    line_num = content.count('\n', 0, match.start()) + 1
                    line_content = lines[line_num - 1].strip() if line_num <= len(lines) else ""
                    
                    add_finding(
                        severity="MEDIUM",
                        category="Cryptography",
                        title=title,
                        description=f"Weak cryptographic practice detected: {match.group()}",
                        file_path=file_path,
                        line_number=line_num,
                        code_snippet=line_content,
                        recommendation=recommendation,
                        cwe_id=cwe_id
                    )
                    print_finding("MEDIUM", title, file_path, line_num)
                    found_issues += 1
                    
        except Exception as e:
            print(f"{Colors.YELLOW}Warning: Could not read file {file_path}: {e}{Colors.ENDC}")
    
    if found_issues == 0:
        print(f"{Colors.GREEN}✔ No weak cryptography patterns found.{Colors.ENDC}")
    return found_issues

def check_file_permissions() -> int:
    """Check for insecure file permissions."""
    print_header("Enhanced Check: File Permissions")
    found_issues = 0
    
    sensitive_files = [
        '.env', '.env.local', '.env.production',
        'config.py', 'settings.py',
        'private_key.pem', 'id_rsa', 'id_dsa',
        'database.db', '*.key', '*.pem'
    ]
    
    for pattern in sensitive_files:
        for file_path in Path('.').rglob(pattern):
            if file_path.is_file():
                stat = file_path.stat()
                mode = oct(stat.st_mode)[-3:]  # Get last 3 digits of octal mode
                
                # Check if file is readable by others (world-readable)
                if int(mode[2]) & 4:  # Others have read permission
                    add_finding(
                        severity="HIGH",
                        category="File Permissions",
                        title="World-readable sensitive file",
                        description=f"Sensitive file {file_path} is readable by others (permissions: {mode})",
                        file_path=str(file_path),
                        line_number=1,
                        recommendation="Restrict file permissions to owner only (chmod 600)",
                        cwe_id="CWE-732"
                    )
                    print_finding("HIGH", f"World-readable sensitive file (permissions: {mode})", str(file_path), 1)
                    found_issues += 1
    
    if found_issues == 0:
        print(f"{Colors.GREEN}✔ No insecure file permissions found.{Colors.ENDC}")
    return found_issues

def check_debug_information(files: List[str]) -> int:
    """Check for debug information that might leak sensitive data."""
    print_header("Enhanced Check: Debug Information Leakage")
    found_issues = 0
    
    debug_patterns = [
        (r'DEBUG\s*=\s*True', "Debug mode enabled", "Disable debug mode in production"),
        (r'print\s*\(\s*.*password.*\)', "Password in print statement", "Remove debug prints with sensitive data"),
        (r'console\.log\s*\(\s*.*password.*\)', "Password in console.log", "Remove debug logs with sensitive data"),
        (r'logger\.debug\s*\(\s*.*password.*\)', "Password in debug log", "Remove sensitive data from logs"),
        (r'traceback\.print_exc\(\)', "Exception traceback printing", "Use proper error handling in production"),
    ]
    
    for file_path in files:
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.splitlines()
            
            for pattern, title, recommendation in debug_patterns:
                for match in re.finditer(pattern, content, re.IGNORECASE):
                    line_num = content.count('\n', 0, match.start()) + 1
                    line_content = lines[line_num - 1].strip() if line_num <= len(lines) else ""
                    
                    add_finding(
                        severity="MEDIUM",
                        category="Information Disclosure",
                        title=title,
                        description=f"Debug information detected: {match.group()}",
                        file_path=file_path,
                        line_number=line_num,
                        code_snippet=line_content,
                        recommendation=recommendation,
                        cwe_id="CWE-200"
                    )
                    print_finding("MEDIUM", title, file_path, line_num)
                    found_issues += 1
                    
        except Exception as e:
            print(f"{Colors.YELLOW}Warning: Could not read file {file_path}: {e}{Colors.ENDC}")
    
    if found_issues == 0:
        print(f"{Colors.GREEN}✔ No debug information leakage found.{Colors.ENDC}")
    return found_issues

def check_https_enforcement(files: List[str]) -> int:
    """Check for HTTPS enforcement and secure connections."""
    print_header("Enhanced Check: HTTPS/TLS Security")
    found_issues = 0
    
    for file_path in files:
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.splitlines()
            
            # Check for HTTP URLs (should be HTTPS)
            http_patterns = [
                (r'http://(?!localhost|127\.0\.0\.1|0\.0\.0\.0)', "HTTP URL found", "Use HTTPS instead of HTTP"),
                (r'["\']http://[^"\']*["\']', "Hardcoded HTTP URL", "Replace with HTTPS URL"),
                (r'url\s*=\s*["\']http://[^"\']*["\']', "HTTP URL in configuration", "Use HTTPS URLs"),
                (r'api[_-]?url\s*=\s*["\']http://[^"\']*["\']', "HTTP API URL", "Use HTTPS for API endpoints"),
            ]
            
            for pattern, title, recommendation in http_patterns:
                for match in re.finditer(pattern, content, re.IGNORECASE):
                    line_num = content.count('\n', 0, match.start()) + 1
                    line_content = lines[line_num - 1].strip() if line_num <= len(lines) else ""
                    
                    # Skip if it's a comment or example
                    if line_content.strip().startswith('#') or line_content.strip().startswith('//'):
                        continue
                    
                    add_finding(
                        severity="HIGH",
                        category="HTTPS/TLS",
                        title=title,
                        description=f"Insecure HTTP connection detected: {match.group()}",
                        file_path=file_path,
                        line_number=line_num,
                        code_snippet=line_content,
                        recommendation=recommendation,
                        cwe_id="CWE-319"
                    )
                    print_finding("HIGH", title, file_path, line_num)
                    found_issues += 1
            
            # Check for SSL/TLS configuration issues
            ssl_patterns = [
                (r'ssl_verify\s*=\s*False', "SSL verification disabled", "Enable SSL certificate verification"),
                (r'verify\s*=\s*False', "Certificate verification disabled", "Enable certificate verification"),
                (r'SSLOPT_NO_VERIFY', "SSL verification disabled", "Remove SSLOPT_NO_VERIFY flag"),
                (r'ssl\.CERT_NONE', "SSL certificate verification disabled", "Use ssl.CERT_REQUIRED"),
                (r'requests\.get\([^)]*verify\s*=\s*False', "Requests without SSL verification", "Remove verify=False parameter"),
                (r'urllib3\.disable_warnings', "SSL warnings disabled", "Fix SSL issues instead of disabling warnings"),
            ]
            
            for pattern, title, recommendation in ssl_patterns:
                for match in re.finditer(pattern, content, re.IGNORECASE):
                    line_num = content.count('\n', 0, match.start()) + 1
                    line_content = lines[line_num - 1].strip() if line_num <= len(lines) else ""
                    
                    add_finding(
                        severity="HIGH",
                        category="HTTPS/TLS",
                        title=title,
                        description=f"SSL/TLS security issue: {match.group()}",
                        file_path=file_path,
                        line_number=line_num,
                        code_snippet=line_content,
                        recommendation=recommendation,
                        cwe_id="CWE-295"
                    )
                    print_finding("HIGH", title, file_path, line_num)
                    found_issues += 1
            
            # Check for Flask HTTPS enforcement
            if file_path.endswith('.py') and ('flask' in content.lower() or 'app.run' in content):
                # Check for HTTPS redirect
                https_redirect_patterns = [
                    r'@app\.before_request.*force_https',
                    r'if.*request\.is_secure.*redirect',
                    r'FORCE_HTTPS\s*=\s*True',
                    r'SSL_REDIRECT\s*=\s*True',
                ]
                
                has_https_redirect = any(re.search(pattern, content, re.IGNORECASE) for pattern in https_redirect_patterns)
                
                # Check for secure cookie settings
                secure_cookie_patterns = [
                    r'SESSION_COOKIE_SECURE\s*=\s*True',
                    r'SESSION_COOKIE_HTTPONLY\s*=\s*True',
                    r'REMEMBER_COOKIE_SECURE\s*=\s*True',
                ]
                
                secure_cookies = sum(1 for pattern in secure_cookie_patterns if re.search(pattern, content))
                
                if not has_https_redirect and '@app.route' in content:
                    add_finding(
                        severity="MEDIUM",
                        category="HTTPS/TLS",
                        title="Missing HTTPS Enforcement",
                        description="Flask application without HTTPS redirect",
                        file_path=file_path,
                        line_number=1,
                        recommendation="Implement HTTPS redirect for all HTTP requests",
                        cwe_id="CWE-319"
                    )
                    print_finding("MEDIUM", "Missing HTTPS enforcement", file_path, 1)
                    found_issues += 1
                
                if secure_cookies < 2 and 'session' in content.lower():
                    add_finding(
                        severity="MEDIUM",
                        category="HTTPS/TLS",
                        title="Insecure Cookie Configuration",
                        description="Session cookies not configured for HTTPS",
                        file_path=file_path,
                        line_number=1,
                        recommendation="Set SESSION_COOKIE_SECURE=True and SESSION_COOKIE_HTTPONLY=True",
                        cwe_id="CWE-614"
                    )
                    print_finding("MEDIUM", "Insecure cookie configuration", file_path, 1)
                    found_issues += 1
            
            # Check for JavaScript/Frontend HTTPS issues
            if file_path.endswith(('.js', '.vue', '.ts')):
                # Check for mixed content issues
                mixed_content_patterns = [
                    (r'src\s*=\s*["\']http://[^"\']*["\']', "HTTP resource in HTTPS page"),
                    (r'href\s*=\s*["\']http://[^"\']*["\']', "HTTP link in HTTPS page"),
                    (r'fetch\s*\(\s*["\']http://[^"\']*["\']', "HTTP fetch request"),
                    (r'axios\.get\s*\(\s*["\']http://[^"\']*["\']', "HTTP axios request"),
                ]
                
                for pattern, title in mixed_content_patterns:
                    for match in re.finditer(pattern, content, re.IGNORECASE):
                        line_num = content.count('\n', 0, match.start()) + 1
                        line_content = lines[line_num - 1].strip() if line_num <= len(lines) else ""
                        
                        # Skip localhost and development URLs
                        if 'localhost' in match.group() or '127.0.0.1' in match.group():
                            continue
                        
                        add_finding(
                            severity="HIGH",
                            category="HTTPS/TLS",
                            title=title,
                            description=f"Mixed content issue: {match.group()}",
                            file_path=file_path,
                            line_number=line_num,
                            code_snippet=line_content,
                            recommendation="Use HTTPS URLs or protocol-relative URLs (//)",
                            cwe_id="CWE-319"
                        )
                        print_finding("HIGH", title, file_path, line_num)
                        found_issues += 1
                        
        except Exception as e:
            print(f"{Colors.YELLOW}Warning: Could not read file {file_path}: {e}{Colors.ENDC}")
    
    if found_issues == 0:
        print(f"{Colors.GREEN}✔ HTTPS/TLS configuration looks secure.{Colors.ENDC}")
    return found_issues

def check_network_security_headers(py_files: List[str]) -> int:
    """Check for security headers implementation."""
    print_header("Enhanced Check: Security Headers")
    found_issues = 0
    
    security_headers = [
        ('Strict-Transport-Security', 'HSTS header', 'Implement HSTS to enforce HTTPS'),
        ('Content-Security-Policy', 'CSP header', 'Implement Content Security Policy'),
        ('X-Frame-Options', 'Clickjacking protection', 'Add X-Frame-Options header'),
        ('X-Content-Type-Options', 'MIME sniffing protection', 'Add X-Content-Type-Options: nosniff'),
        ('Referrer-Policy', 'Referrer policy', 'Implement appropriate referrer policy'),
        ('Permissions-Policy', 'Feature policy', 'Consider implementing Permissions-Policy'),
    ]
    
    for file_path in py_files:
        if 'routes' not in file_path and 'app' not in file_path:
            continue
            
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Check if Flask security headers are implemented
            if 'flask' in content.lower():
                headers_found = []
                
                for header_name, description, recommendation in security_headers:
                    # Check for header implementation
                    header_patterns = [
                        rf'["\']?{header_name}["\']?\s*:\s*["\'][^"\']+["\']',
                        rf'response\.headers\[["\']?{header_name}["\']?\]',
                        rf'@app\.after_request.*{header_name}',
                    ]
                    
                    header_found = any(re.search(pattern, content, re.IGNORECASE) for pattern in header_patterns)
                    if header_found:
                        headers_found.append(header_name)
                
                # Check for missing critical headers
                critical_headers = ['Strict-Transport-Security', 'Content-Security-Policy', 'X-Frame-Options']
                missing_critical = [h for h in critical_headers if h not in headers_found]
                
                if missing_critical and '@app.route' in content:
                    for header in missing_critical:
                        header_info = next((h for h in security_headers if h[0] == header), None)
                        if header_info:
                            add_finding(
                                severity="MEDIUM",
                                category="Security Headers",
                                title=f"Missing {header_info[1]}",
                                description=f"Critical security header {header} not implemented",
                                file_path=file_path,
                                line_number=1,
                                recommendation=header_info[2],
                                cwe_id="CWE-693"
                            )
                            print_finding("MEDIUM", f"Missing {header} header", file_path, 1)
                            found_issues += 1
                            
        except Exception as e:
            print(f"{Colors.YELLOW}Warning: Could not read file {file_path}: {e}{Colors.ENDC}")
    
    if found_issues == 0:
        print(f"{Colors.GREEN}✔ Security headers configuration looks good.{Colors.ENDC}")
    return found_issues

def generate_report(config: AuditConfig):
    """Generate security audit report in specified format."""
    if config.output_format == "json":
        report = {
            "timestamp": datetime.datetime.now().isoformat(),
            "total_findings": len(findings),
            "severity_breakdown": {
                "HIGH": len([f for f in findings if f.severity == "HIGH"]),
                "MEDIUM": len([f for f in findings if f.severity == "MEDIUM"]),
                "LOW": len([f for f in findings if f.severity == "LOW"]),
                "INFO": len([f for f in findings if f.severity == "INFO"]),
            },
            "findings": [f.to_dict() for f in findings]
        }
        
        output_file = config.output_file or f"security_audit_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"{Colors.GREEN}Report saved to: {output_file}{Colors.ENDC}")
    
    elif config.output_format == "html":
        html_content = generate_html_report()
        output_file = config.output_file or f"security_audit_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        with open(output_file, 'w') as f:
            f.write(html_content)
        print(f"{Colors.GREEN}HTML report saved to: {output_file}{Colors.ENDC}")

def generate_html_report() -> str:
    """Generate HTML security audit report."""
    severity_colors = {
        "HIGH": "#dc3545",
        "MEDIUM": "#fd7e14", 
        "LOW": "#0dcaf0",
        "INFO": "#6c757d"
    }
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Security Audit Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            .header {{ background: #f8f9fa; padding: 20px; border-radius: 5px; }}
            .finding {{ margin: 15px 0; padding: 15px; border-left: 4px solid; }}
            .HIGH {{ border-color: {severity_colors['HIGH']}; background: #f8d7da; }}
            .MEDIUM {{ border-color: {severity_colors['MEDIUM']}; background: #fff3cd; }}
            .LOW {{ border-color: {severity_colors['LOW']}; background: #d1ecf1; }}
            .INFO {{ border-color: {severity_colors['INFO']}; background: #e2e3e5; }}
            .code {{ background: #f8f9fa; padding: 10px; font-family: monospace; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Security Audit Report</h1>
            <p>Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>Total Findings: {len(findings)}</p>
        </div>
    """
    
    for finding in findings:
        html += f"""
        <div class="finding {finding.severity}">
            <h3>{finding.title} ({finding.severity})</h3>
            <p><strong>Category:</strong> {finding.category}</p>
            <p><strong>File:</strong> {finding.file_path}:{finding.line_number}</p>
            <p><strong>Description:</strong> {finding.description}</p>
            {f'<div class="code">{finding.code_snippet}</div>' if finding.code_snippet else ''}
            {f'<p><strong>Recommendation:</strong> {finding.recommendation}</p>' if finding.recommendation else ''}
            {f'<p><strong>CWE ID:</strong> {finding.cwe_id}</p>' if finding.cwe_id else ''}
        </div>
        """
    
    html += "</body></html>"
    return html

def run_enhanced_audit(config: AuditConfig):
    """Run the enhanced security audit with all checks."""
    print(f"{Colors.BOLD}Starting Enhanced Security Audit...{Colors.ENDC}")
    
    all_files = []
    backend_py_files = []
    frontend_files = []
    
    # Collect files
    if os.path.isdir(BACKEND_DIR):
        backend_py_files = find_files(BACKEND_DIR, '.py')
        all_files.extend(backend_py_files)
        all_files.extend(find_files(BACKEND_DIR, '.env'))
        all_files.extend(find_files(BACKEND_DIR, '.yml'))
        all_files.extend(find_files(BACKEND_DIR, '.yaml'))
    
    if os.path.isdir(FRONTEND_DIR):
        frontend_files = find_files(FRONTEND_DIR, '.vue')
        frontend_files.extend(find_files(FRONTEND_DIR, '.js'))
        frontend_files.extend(find_files(FRONTEND_DIR, '.ts'))
        all_files.extend(frontend_files)
    
    # Add root level files
    all_files.extend([f for f in os.listdir('.') if f.endswith(('.py', '.env', '.yml', '.yaml'))])
    
    # Run enhanced security checks
    total_issues = 0
    
    # Core security checks
    total_issues += check_hardcoded_secrets(all_files)
    total_issues += check_sql_injection_patterns(backend_py_files)
    total_issues += check_weak_crypto_patterns(all_files)
    total_issues += check_file_permissions()
    total_issues += check_debug_information(all_files)
    total_issues += check_https_enforcement(all_files)
    total_issues += check_network_security_headers(backend_py_files)
    
    # Original checks
    if backend_py_files:
        total_issues += check_missing_permissions(backend_py_files)
        total_issues += check_unsanitized_input(backend_py_files)
        check_secure_cookies(os.path.join(BACKEND_DIR, 'config.py'))
    
    if frontend_files:
        vue_files = [f for f in frontend_files if f.endswith('.vue')]
        check_xss_vulnerabilities(vue_files)
    
    # Dependency checks (if not skipped)
    if not config.skip_dependency_check:
        if os.path.isdir(BACKEND_DIR):
            total_issues += run_pip_audit()
        if os.path.isdir(FRONTEND_DIR):
            total_issues += run_npm_audit()
    
    # Static analysis (if not skipped)
    if not config.skip_static_analysis:
        if os.path.isdir(BACKEND_DIR):
            total_issues += run_bandit_scan()
    
    # Generate report
    if config.output_format != "console":
        generate_report(config)
    
    # Summary
    print_header("Enhanced Audit Summary")
    severity_counts = {
        "HIGH": len([f for f in findings if f.severity == "HIGH"]),
        "MEDIUM": len([f for f in findings if f.severity == "MEDIUM"]),
        "LOW": len([f for f in findings if f.severity == "LOW"]),
        "INFO": len([f for f in findings if f.severity == "INFO"]),
    }
    
    print(f"Total findings: {len(findings)}")
    for severity, count in severity_counts.items():
        if count > 0:
            color = {"HIGH": Colors.RED, "MEDIUM": Colors.YELLOW, "LOW": Colors.BLUE, "INFO": Colors.ENDC}[severity]
            print(f"  {color}{severity}: {count}{Colors.ENDC}")
    
    if len(findings) == 0:
        print(f"{Colors.GREEN}{Colors.BOLD}✔ Congratulations! No security issues found.{Colors.ENDC}")
        return 0
    else:
        high_medium = severity_counts["HIGH"] + severity_counts["MEDIUM"]
        if high_medium > 0:
            print(f"{Colors.RED}{Colors.BOLD}✖ Security audit failed with {high_medium} high/medium severity issues.{Colors.ENDC}")
            return 1
        else:
            print(f"{Colors.YELLOW}⚠ Security audit completed with only low severity issues.{Colors.ENDC}")
            return 0


def find_python_files(directories):
    """
    Trouve tous les fichiers .py dans les répertoires spécifiés, en excluant les dossiers spécifiés.
    """
    python_files = []
    for directory in directories:
        if not os.path.isdir(directory):
            logging.warning(f"Le répertoire d'analyse '{directory}' n'existe pas, il sera ignoré.")
            continue
            
        for root, dirs, files in os.walk(directory):
            # Empêche os.walk de descendre dans les répertoires exclus.
            dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]
            
            for file in files:
                # Analyse uniquement les fichiers Python
                if file.endswith('.py'):
                    python_files.append(os.path.join(root, file))
    return python_files

def analyze_file_for_unprotected_routes(file_path):
    """
    Analyse un fichier pour trouver les routes Flask qui pourraient ne pas avoir
    de décorateurs de permission/authentification.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f.readlines()]
        
        unprotected_routes = []
        for i, line in enumerate(lines):
            # Cible les définitions de routes comme '@bp.route(...)'
            if '@' in line and '.route' in line:
                
                # Vérifie si la route est dans la liste blanche des routes publiques
                if any(re.search(pattern, line) for pattern in PUBLIC_ROUTES):
                    continue

                is_protected = False
                
                # Définit une "fenêtre de recherche" de lignes autour de la définition de la route.
                start_line = max(0, i - 8)
                end_line = min(len(lines), i + 4)
                search_window = lines[start_line:end_line]
                
                # Cherche un décorateur de permission n'importe où dans cette fenêtre.
                for window_line in search_window:
                    if any(dec in window_line for dec in PERMISSION_DECORATORS):
                        is_protected = True
                        break
                
                if not is_protected:
                    unprotected_routes.append((i + 1, line))
                    
        return unprotected_routes
    except Exception as e:
        logging.error(f"Impossible d'analyser le fichier {file_path}: {e}")
        return []
def find_scan_files(directories):
    """
    Trouve tous les fichiers pertinents (.py, .js, .vue) dans les répertoires spécifiés.
    Retourne une liste de chemins de fichiers absolus.
    """
    allowed_extensions = ('.py', '.js', '.vue')
    found_files = []
    
    for directory in directories:
        if not os.path.isdir(directory):
            logging.warning(f"Le répertoire d'analyse '{directory}' n'existe pas, il sera ignoré.")
            continue
            
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith(allowed_extensions):
                    # Convertit chaque chemin de fichier en chemin absolu.
                    found_files.append(os.path.abspath(os.path.join(root, file)))
    return found_files

def check_for_var_keyword(file_path):
    """Vérifie l'utilisation du mot-clé 'var' dans les fichiers JS et Vue."""
    if not file_path.endswith(('.js', '.vue')):
        return []

    findings = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f, 1):
                if re.search(r'\bvar\b', line):
                    findings.append({
                        "line": i,
                        "message": "L'utilisation de 'var' est obsolète. Préférez 'let' ou 'const'.",
                        "severity": "MEDIUM"
                    })
    except Exception as e:
        logging.error(f"Impossible de lire le fichier {file_path}: {e}")
    return findings

def run_all_checks_on_file(file_path):
    """Exécute toutes les vérifications définies sur un seul fichier."""
    all_findings = []
    all_findings.extend(check_for_var_keyword(file_path))
    return all_findings

def main():
    """Fonction principale pour exécuter l'audit des meilleures pratiques."""
    logging.info("Début de l'audit des meilleures pratiques...")
    
    all_files = find_scan_files(SCAN_DIRECTORIES)
    
    # Filtre les fichiers en comparant les chemins absolus, ce qui est plus fiable.
    files_to_scan = [
        f for f in all_files 
        if not any(f.startswith(excluded) for excluded in EXCLUDED_PATHS)
    ]
    
    logging.info(f"{len(files_to_scan)} fichier(s) à analyser après exclusion.")
    
    total_findings = 0
    
    for file_path in files_to_scan:
        # Affiche le chemin relatif pour une meilleure lisibilité.
        relative_path = os.path.relpath(file_path, PROJECT_ROOT)
        findings = run_all_checks_on_file(file_path)
        if findings:
            logging.warning(f"Problèmes trouvés dans : {relative_path}")
            for finding in findings:
                total_findings += 1
                logging.warning(f"  - Ligne {finding['line']}: [{finding['severity']}] {finding['message']}")

    if total_findings == 0:
        logging.info("Audit des meilleures pratiques terminé. Aucun problème trouvé.")
    else:
        logging.error(f"Audit des meilleures pratiques terminé. {total_findings} problème(s) potentiel(s) trouvé(s).")

if __name__ == '__main__':
    main()
