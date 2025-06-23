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

# --- Color-coding for terminal output ---
class Colors:
    RED = '\033[91m'
    YELLOW = '\033[93m'
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

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

