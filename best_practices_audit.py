#!/usr/bin/env python3
"""
Best Practices Audit Tool
Checks for coding best practices, CORS configuration, logging, error handling, and more.
"""

import os
import re
import json
import sys
import datetime
import argparse
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Set
from dataclasses import dataclass, asdict
import logging

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# --- CONFIGURATION ---
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

# Détermine la racine du projet en se basant sur l'emplacement de ce script.
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

# Répertoires à analyser (chemins absolus).
SCAN_DIRECTORIES = [
    os.path.join(PROJECT_ROOT, 'backend'),
    os.path.join(PROJECT_ROOT, 'website')
]

BACKEND_DIR = 'backend'
FRONTEND_DIR = 'website'


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
# Best practice finding data structure
@dataclass
class BestPracticeFinding:
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW, INFO
    category: str  # e.g., "CORS", "Logging", "Error Handling", "Code Quality"
    title: str
    description: str
    file_path: str
    line_number: int
    code_snippet: str = ""
    recommendation: str = ""
    best_practice_id: Optional[str] = None
    
    def to_dict(self):
        return asdict(self)

# Audit configuration
@dataclass
class BestPracticesConfig:
    include_low_severity: bool = False
    output_format: str = "console"  # console, json, html
    output_file: Optional[str] = None
    skip_frontend_checks: bool = False
    skip_backend_checks: bool = False
    custom_rules_file: Optional[str] = None
    
# Global findings list
findings: List[BestPracticeFinding] = []

# ANSI color codes
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(title):
    """Prints a styled header."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}===== {title.upper()} ====={Colors.ENDC}")

def add_finding(severity: str, category: str, title: str, description: str, 
                file_path: str, line_number: int, code_snippet: str = "", 
                recommendation: str = "", best_practice_id: Optional[str] = None):
    """Add a best practice finding to the global findings list."""
    finding = BestPracticeFinding(
        severity=severity,
        category=category,
        title=title,
        description=description,
        file_path=file_path,
        line_number=line_number,
        code_snippet=code_snippet,
        recommendation=recommendation,
        best_practice_id=best_practice_id
    )
    findings.append(finding)

def print_finding(level: str, message: str, file_path: str, line_num: int):
    color = {
        "CRITICAL": Colors.RED, "HIGH": Colors.RED, "MEDIUM": Colors.YELLOW, 
        "LOW": Colors.BLUE, "INFO": Colors.CYAN
    }.get(level.upper(), Colors.ENDC)
    print(f"[{color}{level.upper()}{Colors.ENDC}] {message}\n    -> {file_path}:{line_num}")

def find_files(directory: str, extensions: List[str]) -> List[str]:
    """Finds all files with given extensions in a directory."""
    matches = []
    for root, _, filenames in os.walk(directory, topdown=True):
        for filename in filenames:
            if any(filename.endswith(ext) for ext in extensions):
                matches.append(os.path.join(root, filename))
        return matches

    # --- Running flake8 ---
    print(f"\n{YELLOW}Running flake8...{NC}")
    try:
        flake8_process = subprocess.run(
            ['flake8', backend_path],
            capture_output=True,
            text=True,
            check=False # Do not throw exception on non-zero exit code
        )
        if flake8_process.stdout:
            print(f"{RED}Flake8 found issues:{NC}")
            print(flake8_process.stdout)
        else:
            print(f"{GREEN}flake8: No issues found.{NC}")
    except FileNotFoundError:
        print(f"{RED}Error: 'flake8' command not found. Please install it with 'pip install flake8'.{RESET}")

    
    # --- Running pylint ---
    print(f"\n{YELLOW}Running pylint...{NC}")
    try:
        # Note: pylint can be noisy. It's best to configure it with a .pylintrc file.
        pylint_process = subprocess.run(
            ['pylint', backend_path],
            capture_output=True,
            text=True,
            check=False # Do not throw exception on non-zero exit code
        )
        if pylint_process.stdout and "Your code has been rated at" in pylint_process.stdout:
             # A basic check to see if pylint ran successfully
            print(f"{YELLOW}Pylint analysis complete. See details below:{RESET}")
            print(pylint_process.stdout)
        elif pylint_process.returncode != 0:
            print(f"{RED}Pylint found issues:{RESET}")
            print(pylint_process.stdout)
            if pylint_process.stderr:
                print(pylint_process.stderr)
        else:
            print(f"{GREEN}pylint: No issues found.{RESET}")

    except FileNotFoundError:
        print(f"{RED}Error: 'pylint' command not found. Please install it with 'pip install pylint'.{RESET}")



def audit_hardcoded_secrets():
    """Scans for potentially hardcoded secrets."""
    print(f"\n{YELLOW}--- Auditing for hardcoded secrets (basic check) ---{NC}")
    # This is a very basic check. For real projects, use tools like git-secrets or trivy.
    backend_path = os.path.join(os.path.dirname(__file__), 'backend')
    found_secrets = False
    secret_keywords = ['password', 'secret', 'api_key', 'token']
    for root, _, files in os.walk(backend_path):
        for file in files:
            if file.endswith('.py') and file != 'config.py':
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        for i, line in enumerate(f, 1):
                            if any(keyword in line.lower() for keyword in secret_keywords) and ('=' in line):
                                 if not (line.lstrip().startswith('#') or 'secret_key' in line): # Ignore comments and specific safe keys
                                    print(f"Potential hardcoded secret in {filepath}:{i} -> {line.strip()}")
                                    found_secrets = True
                except Exception as e:
                    print(f"{RED}Error reading {filepath}: {e}{NC}")
    
    if not found_secrets:
        print(f"{GREEN}No obvious hardcoded secrets found.{NC}")

# --- Backend Best Practices Checks ---

def check_cors_configuration(py_files: List[str]) -> int:
    """Check for proper CORS configuration in Flask applications."""
    print_header("Backend Check: CORS Configuration")
    found_issues = 0
    
    cors_patterns = [
        (r'CORS\s*\(\s*app\s*\)', "Basic CORS setup found"),
        (r'@cross_origin\s*\(\s*\)', "Cross-origin decorator without parameters"),
        (r'Access-Control-Allow-Origin.*\*', "Wildcard CORS origin"),
        (r'flask_cors', "Flask-CORS import detected"),
    ]
    
    has_cors_config = False
    has_wildcard_cors = False
    
    for file_path in py_files:
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.splitlines()
            
            # Check for CORS imports
            if 'flask_cors' in content or 'CORS' in content:
                has_cors_config = True
            
            for pattern, description in cors_patterns:
                for match in re.finditer(pattern, content, re.IGNORECASE):
                    line_num = content.count('\n', 0, match.start()) + 1
                    line_content = lines[line_num - 1].strip() if line_num <= len(lines) else ""
                    
                    if "Access-Control-Allow-Origin.*\\*" in pattern:
                        has_wildcard_cors = True
                        add_finding(
                            severity="HIGH",
                            category="CORS",
                            title="Wildcard CORS Origin",
                            description="CORS configured to allow all origins (*)",
                            file_path=file_path,
                            line_number=line_num,
                            code_snippet=line_content,
                            recommendation="Specify explicit allowed origins instead of using wildcard",
                            best_practice_id="BP-CORS-001"
                        )
                        print_finding("HIGH", "Wildcard CORS origin detected", file_path, line_num)
                        found_issues += 1
                    
                    elif "@cross_origin\\s*\\(\\s*\\)" in pattern:
                        add_finding(
                            severity="MEDIUM",
                            category="CORS",
                            title="Unconfigured Cross-Origin Decorator",
                            description="@cross_origin decorator used without specific configuration",
                            file_path=file_path,
                            line_number=line_num,
                            code_snippet=line_content,
                            recommendation="Configure specific origins, methods, and headers",
                            best_practice_id="BP-CORS-002"
                        )
                        print_finding("MEDIUM", "Cross-origin decorator without configuration", file_path, line_num)
                        found_issues += 1
                        
        except Exception as e:
            print(f"{Colors.YELLOW}Warning: Could not read file {file_path}: {e}{Colors.ENDC}")
    
    # Check if CORS is configured at all
    if not has_cors_config:
        add_finding(
            severity="MEDIUM",
            category="CORS",
            title="No CORS Configuration Found",
            description="No CORS configuration detected in Flask application",
            file_path="N/A",
            line_number=0,
            recommendation="Implement proper CORS configuration using Flask-CORS",
            best_practice_id="BP-CORS-003"
        )
        print_finding("MEDIUM", "No CORS configuration found", "Flask App", 0)
        found_issues += 1
    
    if found_issues == 0:
        print(f"{Colors.GREEN}✔ CORS configuration appears properly configured.{Colors.ENDC}")
    return found_issues

def check_logging_practices(py_files: List[str]) -> int:
    """Check for proper logging implementation."""
    print_header("Backend Check: Logging Best Practices")
    found_issues = 0
    
    has_logging_config = False
    has_print_statements = False
    
    for file_path in py_files:
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.splitlines()
            
            # Check for logging imports and configuration
            if 'import logging' in content or 'from logging' in content:
                has_logging_config = True
            
            # Check for print statements (should use logging instead)
            print_pattern = r'print\s*\([^)]*\)'
            for match in re.finditer(print_pattern, content):
                line_num = content.count('\n', 0, match.start()) + 1
                line_content = lines[line_num - 1].strip() if line_num <= len(lines) else ""
                
                # Skip if it's in a comment or test file
                if line_content.strip().startswith('#') or 'test' in file_path.lower():
                    continue
                
                has_print_statements = True
                add_finding(
                    severity="LOW",
                    category="Logging",
                    title="Print Statement Instead of Logging",
                    description=f"Print statement found: {match.group()}",
                    file_path=file_path,
                    line_number=line_num,
                    code_snippet=line_content,
                    recommendation="Use logging.info(), logging.debug(), etc. instead of print()",
                    best_practice_id="BP-LOG-001"
                )
                print_finding("LOW", "Print statement found", file_path, line_num)
                found_issues += 1
            
            # Check for proper log levels
            log_level_patterns = [
                (r'logging\.debug\s*\(', "DEBUG"),
                (r'logging\.info\s*\(', "INFO"),
                (r'logging\.warning\s*\(', "WARNING"),
                (r'logging\.error\s*\(', "ERROR"),
                (r'logging\.critical\s*\(', "CRITICAL"),
            ]
            
            log_levels_used = set()
            for pattern, level in log_level_patterns:
                if re.search(pattern, content):
                    log_levels_used.add(level)
            
            # Check if only one log level is used (might indicate poor logging practices)
            if len(log_levels_used) == 1 and 'INFO' in log_levels_used:
                add_finding(
                    severity="INFO",
                    category="Logging",
                    title="Limited Log Level Usage",
                    description="Only INFO level logging detected",
                    file_path=file_path,
                    line_number=1,
                    recommendation="Use appropriate log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
                    best_practice_id="BP-LOG-002"
                )
                
        except Exception as e:
            print(f"{Colors.YELLOW}Warning: Could not read file {file_path}: {e}{Colors.ENDC}")
    
    # Check if logging is configured at all
    if not has_logging_config:
        add_finding(
            severity="MEDIUM",
            category="Logging",
            title="No Logging Configuration",
            description="No logging configuration detected",
            file_path="N/A",
            line_number=0,
            recommendation="Implement proper logging with appropriate levels and formatters",
            best_practice_id="BP-LOG-003"
        )
        print_finding("MEDIUM", "No logging configuration found", "Application", 0)
        found_issues += 1
    
    if found_issues == 0:
        print(f"{Colors.GREEN}✔ Logging practices look good.{Colors.ENDC}")
    return found_issues

def check_error_handling(py_files: List[str]) -> int:
    """Check for proper error handling practices."""
    print_header("Backend Check: Error Handling")
    found_issues = 0
    
    for file_path in py_files:
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.splitlines()
            
            # Check for bare except clauses
            bare_except_pattern = r'except\s*:'
            for match in re.finditer(bare_except_pattern, content):
                line_num = content.count('\n', 0, match.start()) + 1
                line_content = lines[line_num - 1].strip() if line_num <= len(lines) else ""
                
                add_finding(
                    severity="MEDIUM",
                    category="Error Handling",
                    title="Bare Except Clause",
                    description="Bare except clause catches all exceptions",
                    file_path=file_path,
                    line_number=line_num,
                    code_snippet=line_content,
                    recommendation="Catch specific exceptions instead of using bare except",
                    best_practice_id="BP-ERR-001"
                )
                print_finding("MEDIUM", "Bare except clause found", file_path, line_num)
                found_issues += 1
            
            # Check for pass in except blocks
            except_pass_pattern = r'except[^:]*:\s*\n\s*pass'
            for match in re.finditer(except_pass_pattern, content, re.MULTILINE):
                line_num = content.count('\n', 0, match.start()) + 1
                
                add_finding(
                    severity="HIGH",
                    category="Error Handling",
                    title="Silent Exception Handling",
                    description="Exception caught and silently ignored with pass",
                    file_path=file_path,
                    line_number=line_num,
                    code_snippet=match.group().strip(),
                    recommendation="Log the exception or handle it appropriately",
                    best_practice_id="BP-ERR-002"
                )
                print_finding("HIGH", "Silent exception handling", file_path, line_num)
                found_issues += 1
            
            # Check for proper Flask error handlers
            if 'flask' in content.lower():
                error_handler_patterns = [
                    r'@app\.errorhandler\s*\(\s*404\s*\)',
                    r'@app\.errorhandler\s*\(\s*500\s*\)',
                    r'@.*\.errorhandler\s*\(\s*\d+\s*\)',
                ]
                
                has_error_handlers = any(re.search(pattern, content) for pattern in error_handler_patterns)
                if not has_error_handlers and '@app.route' in content:
                    add_finding(
                        severity="MEDIUM",
                        category="Error Handling",
                        title="Missing Flask Error Handlers",
                        description="Flask routes found but no error handlers defined",
                        file_path=file_path,
                        line_number=1,
                        recommendation="Implement error handlers for common HTTP errors (404, 500, etc.)",
                        best_practice_id="BP-ERR-003"
                    )
                    print_finding("MEDIUM", "Missing Flask error handlers", file_path, 1)
                    found_issues += 1
                        
        except Exception as e:
            print(f"{Colors.YELLOW}Warning: Could not read file {file_path}: {e}{Colors.ENDC}")
    
    if found_issues == 0:
        print(f"{Colors.GREEN}✔ Error handling practices look good.{Colors.ENDC}")
    return found_issues

def check_database_practices(py_files: List[str]) -> int:
    """Check for database best practices."""
    print_header("Backend Check: Database Best Practices")
    found_issues = 0
    
    for file_path in py_files:
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.splitlines()
            
            # Check for database connection management
            db_patterns = [
                (r'\.commit\s*\(\s*\)', "Database commit found"),
                (r'\.rollback\s*\(\s*\)', "Database rollback found"),
                (r'with\s+.*\.begin\s*\(\s*\)', "Transaction context manager"),
                (r'db\.session\.', "SQLAlchemy session usage"),
            ]
            
            has_commits = False
            has_rollbacks = False
            has_context_manager = False
            
            for pattern, description in db_patterns:
                matches = list(re.finditer(pattern, content))
                if matches:
                    if "commit" in pattern:
                        has_commits = True
                    elif "rollback" in pattern:
                        has_rollbacks = True
                    elif "with.*begin" in pattern:
                        has_context_manager = True
            
            # Check for commits without rollbacks
            if has_commits and not has_rollbacks and not has_context_manager:
                add_finding(
                    severity="MEDIUM",
                    category="Database",
                    title="Missing Transaction Rollback",
                    description="Database commits found but no rollback handling",
                    file_path=file_path,
                    line_number=1,
                    recommendation="Implement proper transaction rollback handling or use context managers",
                    best_practice_id="BP-DB-001"
                )
                print_finding("MEDIUM", "Missing transaction rollback handling", file_path, 1)
                found_issues += 1
            
            # Check for connection leaks
            connection_patterns = [
                r'\.connect\s*\(\s*\)',
                r'create_engine\s*\(',
                r'sqlite3\.connect\s*\(',
            ]
            
            for pattern in connection_patterns:
                for match in re.finditer(pattern, content):
                    line_num = content.count('\n', 0, match.start()) + 1
                    line_content = lines[line_num - 1].strip() if line_num <= len(lines) else ""
                    
                    # Check if connection is properly closed
                    # Look for .close() in the same function/block
                    function_start = content.rfind('def ', 0, match.start())
                    next_function = content.find('\ndef ', match.end())
                    if next_function == -1:
                        next_function = len(content)
                    
                    function_content = content[function_start:next_function]
                    if '.close()' not in function_content and 'with ' not in line_content:
                        add_finding(
                            severity="MEDIUM",
                            category="Database",
                            title="Potential Connection Leak",
                            description="Database connection opened without explicit close",
                            file_path=file_path,
                            line_number=line_num,
                            code_snippet=line_content,
                            recommendation="Use context managers or ensure connections are properly closed",
                            best_practice_id="BP-DB-002"
                        )
                        print_finding("MEDIUM", "Potential database connection leak", file_path, line_num)
                        found_issues += 1
                        
        except Exception as e:
            print(f"{Colors.YELLOW}Warning: Could not read file {file_path}: {e}{Colors.ENDC}")
    
    if found_issues == 0:
        print(f"{Colors.GREEN}✔ Database practices look good.{Colors.ENDC}")
    return found_issues

def check_api_best_practices(py_files: List[str]) -> int:
    """Check for API design best practices."""
    print_header("Backend Check: API Best Practices")
    found_issues = 0
    
    for file_path in py_files:
        if 'routes' not in file_path and 'api' not in file_path:
            continue
            
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.splitlines()
            
            # Check for proper HTTP methods
            route_pattern = r'@\w*\.route\s*\(\s*["\']([^"\']+)["\'](?:,\s*methods\s*=\s*\[([^\]]+)\])?'
            
            for match in re.finditer(route_pattern, content):
                line_num = content.count('\n', 0, match.start()) + 1
                line_content = lines[line_num - 1].strip() if line_num <= len(lines) else ""
                
                route_path = match.group(1)
                methods = match.group(2) if match.group(2) else "GET"
                
                # Check for RESTful naming conventions
                if not re.match(r'^/api/v\d+/', route_path) and '/api/' in route_path:
                    add_finding(
                        severity="LOW",
                        category="API Design",
                        title="Missing API Versioning",
                        description=f"API route without version: {route_path}",
                        file_path=file_path,
                        line_number=line_num,
                        code_snippet=line_content,
                        recommendation="Include version in API routes (e.g., /api/v1/)",
                        best_practice_id="BP-API-001"
                    )
                    print_finding("LOW", "API route without versioning", file_path, line_num)
                    found_issues += 1
                
                # Check for proper HTTP methods usage
                if 'POST' in methods and 'GET' in methods:
                    add_finding(
                        severity="MEDIUM",
                        category="API Design",
                        title="Mixed HTTP Methods",
                        description=f"Route accepts both GET and POST: {route_path}",
                        file_path=file_path,
                        line_number=line_num,
                        code_snippet=line_content,
                        recommendation="Use separate endpoints for different HTTP methods",
                        best_practice_id="BP-API-002"
                    )
                    print_finding("MEDIUM", "Mixed HTTP methods in single route", file_path, line_num)
                    found_issues += 1
            
            # Check for proper status code usage
            status_code_patterns = [
                (r'return.*,\s*200', "Explicit 200 status"),
                (r'return.*,\s*201', "201 Created status"),
                (r'return.*,\s*400', "400 Bad Request status"),
                (r'return.*,\s*404', "404 Not Found status"),
                (r'return.*,\s*500', "500 Internal Server Error status"),
            ]
            
            status_codes_used = set()
            for pattern, description in status_code_patterns:
                if re.search(pattern, content):
                    status_codes_used.add(description)
            
            # Check if only default status codes are used
            if len(status_codes_used) <= 1:
                add_finding(
                    severity="INFO",
                    category="API Design",
                    title="Limited HTTP Status Code Usage",
                    description="API may not be using appropriate HTTP status codes",
                    file_path=file_path,
                    line_number=1,
                    recommendation="Use appropriate HTTP status codes (200, 201, 400, 404, 500, etc.)",
                    best_practice_id="BP-API-003"
                )
                
        except Exception as e:
            print(f"{Colors.YELLOW}Warning: Could not read file {file_path}: {e}{Colors.ENDC}")
    
    if found_issues == 0:
        print(f"{Colors.GREEN}✔ API design practices look good.{Colors.ENDC}")
    return found_issues

# --- Frontend Best Practices Checks ---

def check_vue_best_practices(vue_files: List[str]) -> int:
    """Check for Vue.js best practices."""
    print_header("Frontend Check: Vue.js Best Practices")
    found_issues = 0
    
    for file_path in vue_files:
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.splitlines()
            
            # Check for proper component naming
            component_name_pattern = r'name:\s*["\']([^"\']+)["\']'
            for match in re.finditer(component_name_pattern, content):
                line_num = content.count('\n', 0, match.start()) + 1
                line_content = lines[line_num - 1].strip() if line_num <= len(lines) else ""
                
                component_name = match.group(1)
                # Check if component name follows PascalCase
                if not re.match(r'^[A-Z][a-zA-Z0-9]*$', component_name):
                    add_finding(
                        severity="LOW",
                        category="Vue.js",
                        title="Component Naming Convention",
                        description=f"Component name '{component_name}' doesn't follow PascalCase",
                        file_path=file_path,
                        line_number=line_num,
                        code_snippet=line_content,
                        recommendation="Use PascalCase for component names",
                        best_practice_id="BP-VUE-001"
                    )
                    print_finding("LOW", "Component naming convention issue", file_path, line_num)
                    found_issues += 1
            
            # Check for key attribute in v-for
            v_for_pattern = r'v-for\s*=\s*["\'][^"\']*["\']'
            for match in re.finditer(v_for_pattern, content):
                line_num = content.count('\n', 0, match.start()) + 1
                line_content = lines[line_num - 1].strip() if line_num <= len(lines) else ""
                
                # Check if :key is present in the same line or nearby
                if ':key' not in line_content and 'v-bind:key' not in line_content:
                    # Check next few lines
                    key_found = False
                    for i in range(line_num, min(line_num + 3, len(lines))):
                        if ':key' in lines[i] or 'v-bind:key' in lines[i]:
                            key_found = True
                            break
                    
                    if not key_found:
                        add_finding(
                            severity="MEDIUM",
                            category="Vue.js",
                            title="Missing Key in v-for",
                            description="v-for directive without :key attribute",
                            file_path=file_path,
                            line_number=line_num,
                            code_snippet=line_content,
                            recommendation="Always use :key with v-for for better performance",
                            best_practice_id="BP-VUE-002"
                        )
                        print_finding("MEDIUM", "Missing :key in v-for", file_path, line_num)
                        found_issues += 1
            
            # Check for proper prop validation
            props_pattern = r'props:\s*\{([^}]+)\}'
            for match in re.finditer(props_pattern, content, re.DOTALL):
                props_content = match.group(1)
                # Simple check for type validation
                if 'type:' not in props_content and 'Type' not in props_content:
                    line_num = content.count('\n', 0, match.start()) + 1
                    add_finding(
                        severity="LOW",
                        category="Vue.js",
                        title="Missing Prop Validation",
                        description="Props defined without type validation",
                        file_path=file_path,
                        line_number=line_num,
                        recommendation="Add type validation to props",
                        best_practice_id="BP-VUE-003"
                    )
                    print_finding("LOW", "Missing prop validation", file_path, line_num)
                    found_issues += 1
                    
        except Exception as e:
            print(f"{Colors.YELLOW}Warning: Could not read file {file_path}: {e}{Colors.ENDC}")
    
    if found_issues == 0:
        print(f"{Colors.GREEN}✔ Vue.js practices look good.{Colors.ENDC}")
    return found_issues

def check_javascript_best_practices(js_files: List[str]) -> int:
    """Check for JavaScript/TypeScript best practices."""
    print_header("Frontend Check: JavaScript Best Practices")
    found_issues = 0
    
    for file_path in js_files:
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.splitlines()
            
            # Check for console.log statements (should be removed in production)
            console_pattern = r'console\.log\s*\([^)]*\)'
            for match in re.finditer(console_pattern, content):
                line_num = content.count('\n', 0, match.start()) + 1
                line_content = lines[line_num - 1].strip() if line_num <= len(lines) else ""
                
                # Skip if it's in a comment
                if line_content.strip().startswith('//'):
                    continue
                
                add_finding(
                    severity="LOW",
                    category="JavaScript",
                    title="Console.log Statement",
                    description="console.log statement found",
                    file_path=file_path,
                    line_number=line_num,
                    code_snippet=line_content,
                    recommendation="Remove console.log statements before production",
                    best_practice_id="BP-JS-001"
                )
                print_finding("LOW", "console.log statement found", file_path, line_num)
                found_issues += 1
            
            # Check for var usage (should use let/const)
            var_pattern = r'\bvar\s+\w+'
            for match in re.finditer(var_pattern, content):
                line_num = content.count('\n', 0, match.start()) + 1
                line_content = lines[line_num - 1].strip() if line_num <= len(lines) else ""
                
                add_finding(
                    severity="MEDIUM",
                    category="JavaScript",
                    title="Use of var keyword",
                    description="var keyword used instead of let/const",
                    file_path=file_path,
                    line_number=line_num,
                    code_snippet=line_content,
                    recommendation="Use let or const instead of var",
                    best_practice_id="BP-JS-002"
                )
                print_finding("MEDIUM", "var keyword usage", file_path, line_num)
                found_issues += 1
            
            # Check for proper error handling in async functions
            async_pattern = r'async\s+function|async\s*\([^)]*\)\s*=>'
            for match in re.finditer(async_pattern, content):
                # Find the function body
                function_start = match.end()
                brace_count = 0
                function_end = function_start
                
                for i, char in enumerate(content[function_start:], function_start):
                    if char == '{':
                        brace_count += 1
                    elif char == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            function_end = i
                            break
                
                function_body = content[function_start:function_end]
                
                # Check if try-catch is used with await
                if 'await' in function_body and 'try' not in function_body:
                    line_num = content.count('\n', 0, match.start()) + 1
                    add_finding(
                        severity="MEDIUM",
                        category="JavaScript",
                        title="Missing Error Handling in Async Function",
                        description="Async function with await but no try-catch",
                        file_path=file_path,
                        line_number=line_num,
                        recommendation="Use try-catch blocks with await statements",
                        best_practice_id="BP-JS-003"
                    )
                    print_finding("MEDIUM", "Missing error handling in async function", file_path, line_num)
                    found_issues += 1
                    
        except Exception as e:
            print(f"{Colors.YELLOW}Warning: Could not read file {file_path}: {e}{Colors.ENDC}")
    
    if found_issues == 0:
        print(f"{Colors.GREEN}✔ JavaScript practices look good.{Colors.ENDC}")
    return found_issues

def check_css_best_practices(css_files: List[str]) -> int:
    """Check for CSS best practices."""
    print_header("Frontend Check: CSS Best Practices")
    found_issues = 0
    
    for file_path in css_files:
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.splitlines()
            
            # Check for !important usage
            important_pattern = r'!\s*important'
            for match in re.finditer(important_pattern, content, re.IGNORECASE):
                line_num = content.count('\n', 0, match.start()) + 1
                line_content = lines[line_num - 1].strip() if line_num <= len(lines) else ""
                
                add_finding(
                    severity="LOW",
                    category="CSS",
                    title="Use of !important",
                    description="!important declaration found",
                    file_path=file_path,
                    line_number=line_num,
                    code_snippet=line_content,
                    recommendation="Avoid !important, use more specific selectors instead",
                    best_practice_id="BP-CSS-001"
                )
                print_finding("LOW", "!important usage", file_path, line_num)
                found_issues += 1
            
            # Check for inline styles in HTML-like content
            if file_path.endswith('.vue'):
                inline_style_pattern = r'style\s*=\s*["\'][^"\']+["\']'
                for match in re.finditer(inline_style_pattern, content):
                    line_num = content.count('\n', 0, match.start()) + 1
                    line_content = lines[line_num - 1].strip() if line_num <= len(lines) else ""
                    
                    add_finding(
                        severity="LOW",
                        category="CSS",
                        title="Inline Styles",
                        description="Inline style attribute found",
                        file_path=file_path,
                        line_number=line_num,
                        code_snippet=line_content,
                        recommendation="Use CSS classes instead of inline styles",
                        best_practice_id="BP-CSS-002"
                    )
                    print_finding("LOW", "Inline styles usage", file_path, line_num)
                    found_issues += 1
                    
        except Exception as e:
            print(f"{Colors.YELLOW}Warning: Could not read file {file_path}: {e}{Colors.ENDC}")
    
    if found_issues == 0:
        print(f"{Colors.GREEN}✔ CSS practices look good.{Colors.ENDC}")
    return found_issues

# --- Configuration and Environment Checks ---

def check_environment_configuration() -> int:
    """Check for proper environment configuration."""
    print_header("Configuration Check: Environment Setup")
    found_issues = 0
    
    # Check for environment files
    env_files = ['.env', '.env.local', '.env.production', '.env.development']
    env_files_found = []
    
    for env_file in env_files:
        if os.path.exists(env_file):
            env_files_found.append(env_file)
    
    if not env_files_found:
        add_finding(
            severity="MEDIUM",
            category="Configuration",
            title="No Environment Files Found",
            description="No .env files found for environment configuration",
            file_path="N/A",
            line_number=0,
            recommendation="Create .env files for different environments",
            best_practice_id="BP-ENV-001"
        )
        print_finding("MEDIUM", "No environment files found", "Project Root", 0)
        found_issues += 1
    else:
        # Check if .env is in .gitignore
        if os.path.exists('.gitignore'):
            with open('.gitignore', 'r') as f:
                gitignore_content = f.read()
                if '.env' not in gitignore_content:
                    add_finding(
                        severity="HIGH",
                        category="Configuration",
                        title="Environment Files Not in .gitignore",
                        description=".env files found but not excluded from version control",
                        file_path=".gitignore",
                        line_number=1,
                        recommendation="Add .env* to .gitignore to prevent committing secrets",
                        best_practice_id="BP-ENV-002"
                    )
                    print_finding("HIGH", ".env files not in .gitignore", ".gitignore", 1)
                    found_issues += 1
    
    # Check for requirements.txt or package.json
    dependency_files = ['requirements.txt', 'package.json', 'Pipfile', 'pyproject.toml']
    dependency_files_found = [f for f in dependency_files if os.path.exists(f)]
    
    if not dependency_files_found:
        add_finding(
            severity="HIGH",
            category="Configuration",
            title="No Dependency Management Files",
            description="No dependency management files found",
            file_path="N/A",
            line_number=0,
            recommendation="Create requirements.txt, package.json, or similar dependency files",
            best_practice_id="BP-ENV-003"
        )
        print_finding("HIGH", "No dependency management files", "Project Root", 0)
        found_issues += 1
    
    if found_issues == 0:
        print(f"{Colors.GREEN}✔ Environment configuration looks good.{Colors.ENDC}")
    return found_issues

def check_documentation_practices() -> int:
    """Check for proper documentation practices."""
    print_header("Documentation Check: Project Documentation")
    found_issues = 0
    
    # Check for README file
    readme_files = ['README.md', 'README.rst', 'README.txt', 'readme.md']
    readme_found = any(os.path.exists(f) for f in readme_files)
    
    if not readme_found:
        add_finding(
            severity="MEDIUM",
            category="Documentation",
            title="No README File",
            description="No README file found in project root",
            file_path="N/A",
            line_number=0,
            recommendation="Create a README.md file with project description and setup instructions",
            best_practice_id="BP-DOC-001"
        )
        print_finding("MEDIUM", "No README file found", "Project Root", 0)
        found_issues += 1
    else:
        # Check README content quality
        for readme_file in readme_files:
            if os.path.exists(readme_file):
                with open(readme_file, 'r', encoding='utf-8', errors='ignore') as f:
                    readme_content = f.read()
                    
                    # Check for essential sections
                    essential_sections = [
                        ('installation', 'Installation instructions'),
                        ('usage', 'Usage examples'),
                        ('setup', 'Setup instructions'),
                        ('requirements', 'Requirements section'),
                    ]
                    
                    missing_sections = []
                    for section, description in essential_sections:
                        if section.lower() not in readme_content.lower():
                            missing_sections.append(description)
                    
                    if len(missing_sections) > 2:
                        add_finding(
                            severity="LOW",
                            category="Documentation",
                            title="Incomplete README",
                            description=f"README missing sections: {', '.join(missing_sections)}",
                            file_path=readme_file,
                            line_number=1,
                            recommendation="Add missing sections to improve documentation",
                            best_practice_id="BP-DOC-002"
                        )
                        print_finding("LOW", "Incomplete README documentation", readme_file, 1)
                        found_issues += 1
                break
    
    # Check for API documentation
    api_doc_files = ['api.md', 'API.md', 'docs/api.md', 'swagger.yaml', 'openapi.yaml']
    api_docs_found = any(os.path.exists(f) for f in api_doc_files)
    
    # Only check if we have API routes
    has_api_routes = False
    if os.path.exists(BACKEND_DIR):
        for root, _, files in os.walk(BACKEND_DIR):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            if '@app.route' in content or '@bp.route' in content:
                                has_api_routes = True
                                break
                    except:
                        continue
            if has_api_routes:
                break
    
    if has_api_routes and not api_docs_found:
        add_finding(
            severity="LOW",
            category="Documentation",
            title="Missing API Documentation",
            description="API routes found but no API documentation",
            file_path="N/A",
            line_number=0,
            recommendation="Create API documentation (Swagger/OpenAPI or markdown)",
            best_practice_id="BP-DOC-003"
        )
        print_finding("LOW", "Missing API documentation", "Project", 0)
        found_issues += 1
    
    if found_issues == 0:
        print(f"{Colors.GREEN}✔ Documentation practices look good.{Colors.ENDC}")
    return found_issues

def check_https_best_practices(files: List[str]) -> int:
    """Check for HTTPS and secure connection best practices."""
    print_header("Security Check: HTTPS Best Practices")
    found_issues = 0
    
    for file_path in files:
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.splitlines()
            
            # Check for HTTP URLs in production code
            http_patterns = [
                (r'http://(?!localhost|127\.0\.0\.1|0\.0\.0\.0)', "HTTP URL in production code"),
                (r'api[_-]?url\s*=\s*["\']http://[^"\']*["\']', "HTTP API endpoint"),
                (r'base[_-]?url\s*=\s*["\']http://[^"\']*["\']', "HTTP base URL"),
            ]
            
            for pattern, description in http_patterns:
                for match in re.finditer(pattern, content, re.IGNORECASE):
                    line_num = content.count('\n', 0, match.start()) + 1
                    line_content = lines[line_num - 1].strip() if line_num <= len(lines) else ""
                    
                    # Skip comments and development configurations
                    if (line_content.strip().startswith('#') or 
                        line_content.strip().startswith('//') or
                        'dev' in file_path.lower() or
                        'test' in file_path.lower()):
                        continue
                    
                    add_finding(
                        severity="HIGH",
                        category="HTTPS",
                        title=description,
                        description=f"Insecure HTTP URL found: {match.group()}",
                        file_path=file_path,
                        line_number=line_num,
                        code_snippet=line_content,
                        recommendation="Use HTTPS URLs for all external connections",
                        best_practice_id="BP-HTTPS-001"
                    )
                    print_finding("HIGH", description, file_path, line_num)
                    found_issues += 1
            
            # Check for SSL verification disabled
            ssl_disable_patterns = [
                (r'verify\s*=\s*False', "SSL verification disabled"),
                (r'ssl_verify\s*=\s*False', "SSL verification disabled"),
                (r'SSLOPT_NO_VERIFY', "SSL verification bypassed"),
            ]
            
            for pattern, description in ssl_disable_patterns:
                for match in re.finditer(pattern, content):
                    line_num = content.count('\n', 0, match.start()) + 1
                    line_content = lines[line_num - 1].strip() if line_num <= len(lines) else ""
                    
                    add_finding(
                        severity="HIGH",
                        category="HTTPS",
                        title=description,
                        description="SSL certificate verification is disabled",
                        file_path=file_path,
                        line_number=line_num,
                        code_snippet=line_content,
                        recommendation="Enable SSL certificate verification for security",
                        best_practice_id="BP-HTTPS-002"
                    )
                    print_finding("HIGH", description, file_path, line_num)
                    found_issues += 1
            
            # Check for proper HTTPS redirect in Flask apps
            if file_path.endswith('.py') and 'flask' in content.lower():
                if '@app.route' in content:
                    # Check for HTTPS enforcement
                    https_patterns = [
                        r'@app\.before_request.*https',
                        r'if.*not.*request\.is_secure',
                        r'FORCE_HTTPS',
                        r'SSL_REDIRECT',
                    ]
                    
                    has_https_enforcement = any(re.search(pattern, content, re.IGNORECASE) for pattern in https_patterns)
                    
                    if not has_https_enforcement:
                        add_finding(
                            severity="MEDIUM",
                            category="HTTPS",
                            title="Missing HTTPS enforcement",
                            description="Flask app without HTTPS redirect mechanism",
                            file_path=file_path,
                            line_number=1,
                            recommendation="Implement HTTPS redirect for production deployment",
                            best_practice_id="BP-HTTPS-003"
                        )
                        print_finding("MEDIUM", "Missing HTTPS enforcement", file_path, 1)
                        found_issues += 1
            
            # Check for mixed content in frontend files
            if file_path.endswith(('.vue', '.js', '.ts', '.html')):
                mixed_content_patterns = [
                    (r'src\s*=\s*["\']http://[^"\']*["\']', "HTTP resource reference"),
                    (r'href\s*=\s*["\']http://[^"\']*["\']', "HTTP link reference"),
                ]
                
                for pattern, description in mixed_content_patterns:
                    for match in re.finditer(pattern, content, re.IGNORECASE):
                        # Skip localhost and development URLs
                        if 'localhost' in match.group() or '127.0.0.1' in match.group():
                            continue
                            
                        line_num = content.count('\n', 0, match.start()) + 1
                        line_content = lines[line_num - 1].strip() if line_num <= len(lines) else ""
                        
                        add_finding(
                            severity="MEDIUM",
                            category="HTTPS",
                            title=description,
                            description=f"Mixed content issue: {match.group()}",
                            file_path=file_path,
                            line_number=line_num,
                            code_snippet=line_content,
                            recommendation="Use HTTPS URLs or protocol-relative URLs (//)",
                            best_practice_id="BP-HTTPS-004"
                        )
                        print_finding("MEDIUM", description, file_path, line_num)
                        found_issues += 1
                        
        except Exception as e:
            print(f"{Colors.YELLOW}Warning: Could not read file {file_path}: {e}{Colors.ENDC}")
    
    if found_issues == 0:
        print(f"{Colors.GREEN}✔ HTTPS practices look good.{Colors.ENDC}")
    return found_issues

def check_security_configuration() -> int:
    """Check for security-related configuration best practices."""
    print_header("Security Check: Configuration Best Practices")
    found_issues = 0
    
    # Check for security-related configuration files
    config_files = []
    
    # Look for common configuration files
    potential_configs = [
        'config.py', 'settings.py', 'app.py', 'main.py',
        'config.json', 'settings.json',
        '.env', '.env.production', '.env.local'
    ]
    
    for config_file in potential_configs:
        if os.path.exists(config_file):
            config_files.append(config_file)
    
    # Also check in backend directory
    if os.path.exists(BACKEND_DIR):
        for root, _, files in os.walk(BACKEND_DIR):
            for file in files:
                if any(file.endswith(ext) for ext in ['.py', '.json', '.env']):
                    if any(keyword in file.lower() for keyword in ['config', 'settings', 'app']):
                        config_files.append(os.path.join(root, file))
    
    for config_file in config_files:
        try:
            with open(config_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.splitlines()
            
            # Check for debug mode in production
            debug_patterns = [
                (r'DEBUG\s*=\s*True', "Debug mode enabled"),
                (r'debug\s*=\s*True', "Debug mode enabled"),
                (r'["\']debug["\']:\s*true', "Debug mode enabled in JSON"),
            ]
            
            for pattern, description in debug_patterns:
                for match in re.finditer(pattern, content, re.IGNORECASE):
                    line_num = content.count('\n', 0, match.start()) + 1
                    line_content = lines[line_num - 1].strip() if line_num <= len(lines) else ""
                    
                    # Skip if it's clearly for development
                    if 'dev' in config_file.lower() or 'development' in config_file.lower():
                        continue
                    
                    add_finding(
                        severity="HIGH",
                        category="Security Configuration",
                        title=description,
                        description="Debug mode should be disabled in production",
                        file_path=config_file,
                        line_number=line_num,
                        code_snippet=line_content,
                        recommendation="Set DEBUG=False for production deployment",
                        best_practice_id="BP-SEC-001"
                    )
                    print_finding("HIGH", description, config_file, line_num)
                    found_issues += 1
            
            # Check for weak secret keys
            secret_patterns = [
                (r'SECRET_KEY\s*=\s*["\'](?:secret|password|123|test|dev)["\']', "Weak secret key"),
                (r'secret[_-]?key\s*=\s*["\'][^"\']{1,16}["\']', "Short secret key"),
            ]
            
            for pattern, description in secret_patterns:
                for match in re.finditer(pattern, content, re.IGNORECASE):
                    line_num = content.count('\n', 0, match.start()) + 1
                    line_content = lines[line_num - 1].strip() if line_num <= len(lines) else ""
                    
                    add_finding(
                        severity="HIGH",
                        category="Security Configuration",
                        title=description,
                        description="Weak or default secret key detected",
                        file_path=config_file,
                        line_number=line_num,
                        code_snippet=line_content,
                        recommendation="Use a strong, randomly generated secret key",
                        best_practice_id="BP-SEC-002"
                    )
                    print_finding("HIGH", description, config_file, line_num)
                    found_issues += 1
            
            # Check for missing security headers configuration
            if config_file.endswith('.py') and 'flask' in content.lower():
                security_headers = [
                    'SECURITY_HEADERS', 'CSP_', 'HSTS_', 'X_FRAME_OPTIONS'
                ]
                
                has_security_config = any(header in content for header in security_headers)
                
                if not has_security_config and ('app' in content.lower() or 'flask' in content.lower()):
                    add_finding(
                        severity="MEDIUM",
                        category="Security Configuration",
                        title="Missing security headers configuration",
                        description="No security headers configuration found",
                        file_path=config_file,
                        line_number=1,
                        recommendation="Configure security headers (CSP, HSTS, X-Frame-Options, etc.)",
                        best_practice_id="BP-SEC-003"
                    )
                    print_finding("MEDIUM", "Missing security headers config", config_file, 1)
                    found_issues += 1
                    
        except Exception as e:
            print(f"{Colors.YELLOW}Warning: Could not read config file {config_file}: {e}{Colors.ENDC}")
    
    if found_issues == 0:
        print(f"{Colors.GREEN}✔ Security configuration looks good.{Colors.ENDC}")
    return found_issues

# --- Report Generation ---

def generate_report(config: BestPracticesConfig):
    """Generate best practices audit report in specified format."""
    if config.output_format == "json":
        report = {
            "timestamp": datetime.datetime.now().isoformat(),
            "total_findings": len(findings),
            "severity_breakdown": {
                "CRITICAL": len([f for f in findings if f.severity == "CRITICAL"]),
                "HIGH": len([f for f in findings if f.severity == "HIGH"]),
                "MEDIUM": len([f for f in findings if f.severity == "MEDIUM"]),
                "LOW": len([f for f in findings if f.severity == "LOW"]),
                "INFO": len([f for f in findings if f.severity == "INFO"]),
            },
            "category_breakdown": {},
            "findings": [f.to_dict() for f in findings]
        }
        
        # Add category breakdown
        categories = {}
        for finding in findings:
            if finding.category not in categories:
                categories[finding.category] = 0
            categories[finding.category] += 1
        report["category_breakdown"] = categories
        
        output_file = config.output_file or f"best_practices_audit_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"{Colors.GREEN}Report saved to: {output_file}{Colors.ENDC}")
    
    elif config.output_format == "html":
        html_content = generate_html_report()
        output_file = config.output_file or f"best_practices_audit_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        with open(output_file, 'w') as f:
            f.write(html_content)
        print(f"{Colors.GREEN}HTML report saved to: {output_file}{Colors.ENDC}")

def generate_html_report() -> str:
    """Generate HTML best practices audit report."""
    severity_colors = {
        "CRITICAL": "#721c24",
        "HIGH": "#dc3545",
        "MEDIUM": "#fd7e14", 
        "LOW": "#0dcaf0",
        "INFO": "#6c757d"
    }
    
    # Calculate statistics
    severity_counts = {
        "CRITICAL": len([f for f in findings if f.severity == "CRITICAL"]),
        "HIGH": len([f for f in findings if f.severity == "HIGH"]),
        "MEDIUM": len([f for f in findings if f.severity == "MEDIUM"]),
        "LOW": len([f for f in findings if f.severity == "LOW"]),
        "INFO": len([f for f in findings if f.severity == "INFO"]),
    }
    
    category_counts = {}
    for finding in findings:
        if finding.category not in category_counts:
            category_counts[finding.category] = 0
        category_counts[finding.category] += 1
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Best Practices Audit Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f8f9fa; }}
            .header {{ background: #ffffff; padding: 30px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 20px; }}
            .stats {{ display: flex; gap: 20px; margin: 20px 0; }}
            .stat-card {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); flex: 1; }}
            .finding {{ margin: 15px 0; padding: 20px; border-left: 5px solid; background: white; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            .CRITICAL {{ border-color: {severity_colors['CRITICAL']}; }}
            .HIGH {{ border-color: {severity_colors['HIGH']}; }}
            .MEDIUM {{ border-color: {severity_colors['MEDIUM']}; }}
            .LOW {{ border-color: {severity_colors['LOW']}; }}
            .INFO {{ border-color: {severity_colors['INFO']}; }}
            .code {{ background: #f8f9fa; padding: 15px; font-family: 'Courier New', monospace; border-radius: 5px; margin: 10px 0; }}
            .category {{ display: inline-block; background: #e9ecef; padding: 4px 8px; border-radius: 4px; font-size: 0.8em; margin-right: 10px; }}
            .severity {{ display: inline-block; padding: 4px 8px; border-radius: 4px; color: white; font-weight: bold; font-size: 0.8em; }}
            h1 {{ color: #495057; margin-bottom: 10px; }}
            h2 {{ color: #6c757d; margin-top: 30px; }}
            h3 {{ margin-top: 0; color: #495057; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🔍 Best Practices Audit Report</h1>
            <p><strong>Generated:</strong> {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p><strong>Total Findings:</strong> {len(findings)}</p>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <h3>Severity Breakdown</h3>
    """
    
    for severity, count in severity_counts.items():
        if count > 0:
            html += f'<div><span class="severity" style="background-color: {severity_colors[severity]}">{severity}</span> {count}</div>'
    
    html += """
            </div>
            <div class="stat-card">
                <h3>Category Breakdown</h3>
    """
    
    for category, count in sorted(category_counts.items()):
        html += f'<div><span class="category">{category}</span> {count}</div>'
    
    html += """
            </div>
        </div>
        
        <h2>Findings</h2>
    """
    
    for finding in findings:
        severity_style = f'background-color: {severity_colors[finding.severity]}'
        html += f"""
        <div class="finding {finding.severity}">
            <div>
                <span class="category">{finding.category}</span>
                <span class="severity" style="{severity_style}">{finding.severity}</span>
            </div>
            <h3>{finding.title}</h3>
            <p><strong>File:</strong> {finding.file_path}:{finding.line_number}</p>
            <p><strong>Description:</strong> {finding.description}</p>
            {f'<div class="code">{finding.code_snippet}</div>' if finding.code_snippet else ''}
            {f'<p><strong>💡 Recommendation:</strong> {finding.recommendation}</p>' if finding.recommendation else ''}
            {f'<p><strong>ID:</strong> {finding.best_practice_id}</p>' if finding.best_practice_id else ''}
        </div>
        """
    
    html += """
    </body>
    </html>
    """
    return html


def run_best_practices_audit(config: BestPracticesConfig):
    """Run the comprehensive best practices audit."""
    print(f"{Colors.BOLD}Starting Best Practices Audit...{Colors.ENDC}")
    
    total_issues = 0
    
    # Collect files
    backend_py_files = []
    frontend_vue_files = []
    frontend_js_files = []
    frontend_css_files = []
    
    if os.path.isdir(BACKEND_DIR) and not config.skip_backend_checks:
        backend_py_files = find_files(BACKEND_DIR, ['.py'])
    
    if os.path.isdir(FRONTEND_DIR) and not config.skip_frontend_checks:
        frontend_vue_files = find_files(FRONTEND_DIR, ['.vue'])
        frontend_js_files = find_files(FRONTEND_DIR, ['.js', '.ts'])
        frontend_css_files = find_files(FRONTEND_DIR, ['.css', '.scss', '.sass'])
        frontend_css_files.extend(frontend_vue_files)  # Vue files can contain CSS
    
    # Backend checks
    if backend_py_files:
        total_issues += check_cors_configuration(backend_py_files)
        total_issues += check_logging_practices(backend_py_files)
        total_issues += check_error_handling(backend_py_files)
        total_issues += check_database_practices(backend_py_files)
        total_issues += check_api_best_practices(backend_py_files)
    
    # Frontend checks
    if frontend_vue_files:
        total_issues += check_vue_best_practices(frontend_vue_files)
    
    if frontend_js_files:
        total_issues += check_javascript_best_practices(frontend_js_files)
    
    if frontend_css_files:
        total_issues += check_css_best_practices(frontend_css_files)
    
    # General checks
    total_issues += check_environment_configuration()
    total_issues += check_documentation_practices()


    run_static_analysis() # pyling, flake8
    # check_for_print_statements() # leftover print statements in the backend code, 
    audit_hardcoded_secrets()

    # Security-related best practices
    all_files = []
    if backend_py_files:
        all_files.extend(backend_py_files)
    if frontend_vue_files:
        all_files.extend(frontend_vue_files)
    if frontend_js_files:
        all_files.extend(frontend_js_files)
    
    total_issues += check_https_best_practices(all_files)
    total_issues += check_security_configuration()
    
    # Generate report
    if config.output_format != "console":
        generate_report(config)
    
    # Summary
    print_header("Best Practices Audit Summary")
    severity_counts = {
        "CRITICAL": len([f for f in findings if f.severity == "CRITICAL"]),
        "HIGH": len([f for f in findings if f.severity == "HIGH"]),
        "MEDIUM": len([f for f in findings if f.severity == "MEDIUM"]),
        "LOW": len([f for f in findings if f.severity == "LOW"]),
        "INFO": len([f for f in findings if f.severity == "INFO"]),
    }
    
    print(f"Total findings: {len(findings)}")
    for severity, count in severity_counts.items():
        if count > 0:
            color = {
                "CRITICAL": Colors.RED, "HIGH": Colors.RED, "MEDIUM": Colors.YELLOW, 
                "LOW": Colors.BLUE, "INFO": Colors.CYAN
            }[severity]
            print(f"  {color}{severity}: {count}{Colors.ENDC}")
    
    # Category breakdown
    category_counts = {}
    for finding in findings:
        if finding.category not in category_counts:
            category_counts[finding.category] = 0
        category_counts[finding.category] += 1
    
    if category_counts:
        print(f"\nFindings by category:")
        for category, count in sorted(category_counts.items()):
            print(f"  {Colors.CYAN}{category}: {count}{Colors.ENDC}")
    
    if len(findings) == 0:
        print(f"{Colors.GREEN}{Colors.BOLD}✔ Excellent! All best practices are being followed.{Colors.ENDC}")
        return 0
    else:
        critical_high = severity_counts["CRITICAL"] + severity_counts["HIGH"]
        if critical_high > 0:
            print(f"{Colors.RED}{Colors.BOLD}⚠ Found {critical_high} critical/high priority best practice issues.{Colors.ENDC}")
            return 1
        else:
            print(f"{Colors.YELLOW}📋 Found some best practice improvements. Review the findings above.{Colors.ENDC}")
            return 0

def find_scan_files(directories):
    """
    Trouve tous les fichiers pertinents (.py, .js, .vue) dans les répertoires spécifiés,
    en ignorant les chemins exclus de manière efficace.
    """
    allowed_extensions = ('.py', '.js', '.vue')
    found_files = []
    
    for directory in directories:
        if not os.path.isdir(directory):
            logging.warning(f"Le répertoire d'analyse '{directory}' n'existe pas, il sera ignoré.")
            continue
            
        for root, dirs, files in os.walk(directory):
            # CORRIGÉ : Empêche os.walk d'entrer dans les répertoires exclus.
            # C'est la solution la plus performante.
            dirs[:] = [
                d for d in dirs 
                if not os.path.abspath(os.path.join(root, d)).startswith(tuple(EXCLUDED_PATHS))
            ]
            
            for file in files:
                if file.endswith(allowed_extensions):
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
    
    # La fonction find_scan_files retourne maintenant une liste déjà filtrée.
    files_to_scan = find_scan_files(SCAN_DIRECTORIES)
    
    logging.info(f"{len(files_to_scan)} fichier(s) à analyser.")
    
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
