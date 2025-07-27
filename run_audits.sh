#!/bin/bash

# ==============================================================================
# Comprehensive Code & Security Audit Script
# ==============================================================================
# This script performs a series of audits on the codebase, including:
# 1. Dependency Vulnerability Scan: Checks for known vulnerabilities in packages.
# 2. Static Security Analysis: Scans the code for common security issues.
# 3. Code Linting: Checks for style errors, potential bugs, and cyclic imports.
# 4. Code Formatting: Ensures code adheres to consistent formatting standards.
# 5. Custom Audits: Runs the project-specific audit scripts.
#
# The script will exit immediately if any critical command fails.
# ==============================================================================

# --- Setup ---
# Exit immediately if a command exits with a non-zero status.
set -e
# Treat unset variables as an error when substituting.
set -u
# The return value of a pipeline is the status of the last command to exit with a non-zero status.
set -o pipefail

# --- Configuration ---
LOG_DIR="logs"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
AUDIT_LOG_FILE="${LOG_DIR}/audit_log_${TIMESTAMP}.txt"
BACKEND_DIR="backend"
FRONTEND_DIR="website"

# --- Colors for better output ---
# Exporting these is generally good practice, but the issue might be deeper
export COLOR_GREEN='\033[0;32m'
export COLOR_YELLOW='\033[1;33m'
export COLOR_RED='\033[0;31m'
export COLOR_NC='\033[0m'

# --- Helper Functions ---
function print_step {
    echo -e "\n${COLOR_YELLOW}>>> $1${COLOR_NC}"
}

function print_success {
    echo -e "${COLOR_GREEN}✓ $1${COLOR_NC}"
}

function print_error {
    echo -e "${COLOR_RED}✗ ERROR: $1${COLOR_NC}" >&2
    exit 1
}

function check_command {
    if ! command -v "$1" &> /dev/null; then
        print_error "'$1' command not found. Please install it or ensure it's in your PATH."
    fi
}

function check_command_optional {
    if ! command -v "$1" &> /dev/null; then
        echo -e "${COLOR_YELLOW}⚠ WARNING: '$1' command not found. Audits using this tool will be skipped by the Python script.${COLOR_NC}" >&2
        return 1 # Indicate failure, but don't exit the script
    fi
}

# --- Main Script ---
mkdir -p "$LOG_DIR"

# Redirect all output to both console and log file
exec > >(tee -a "${AUDIT_LOG_FILE}") 2>&1

# Use simple echoes for the very initial banner to avoid variable issues
echo "=========================================="
echo "   Starting Maison Truvra Code Audits     "
echo "=========================================="
echo "Full log will be saved to: ${AUDIT_LOG_FILE}"
echo "--------------------------------------------------"

# --- Prerequisite Tool Checks ---
print_step "Checking for externally managed tools"
check_command_optional codeql || true      # Must be installed manually. Used by security_audit.py
check_command_optional sonar-scanner || true # Must be installed manually. Used by security_audit.py
print_success "Checks for externally managed tools complete."

# --- Installation/Mise à jour des outils d'audit Python ---
print_step "Installation/Mise à jour des outils d'audit Python"
pip install --upgrade pip bandit pip-audit ruff semgrep mypy defusedcsv
if [ $? -ne 0 ]; then
    print_error "Échec de l'installation des outils d'audit Python."
fi
print_success "Outils d'audit Python prêts."

# --- Frontend Dependency Vulnerability Fix ---
print_step "Fixing known frontend dependency vulnerabilities..."
npm audit fix --prefix "$FRONTEND_DIR"
print_success "npm audit fix complete."

print_step "Running Python Linter (Ruff)..."
python3 run_linter.py
print_success "Python linter script finished."
# --- 2. Custom Backend Security Audit (via security_audit.py which should handle pip-audit and bandit) ---
# Assuming security_audit.py internally runs pip-audit and bandit.
# Make sure security_audit.py exits with 0 if it successfully *runs* the audits,
# and only exits non-zero if it *fails* to perform the audits (e.g., config error, tool not found).
print_step "Running Custom Backend Security Audit (Pip-Audit, Bandit etc.)..."
python3 security_audit.py
SECURITY_AUDIT_EXIT_CODE=$?
if [ ${SECURITY_AUDIT_EXIT_CODE} -ne 0 ]; then
    # security_audit.py exits with 1 if findings are present. This is not a script failure.
    # We log it as a warning and continue, allowing the full script to complete.
    echo -e "${COLOR_YELLOW}⚠ security_audit.py reported findings (Exit Code: ${SECURITY_AUDIT_EXIT_CODE}). See logs above for details.${COLOR_NC}"
fi
print_success "Custom security audit script finished."

# --- 4. Code Formatting Checks (Handled by Ruff) ---
# The run_linter.py script handles all formatting and linting via Ruff,
# which replaces the need for separate black and isort checks here.
print_step "Code formatting and import sorting checks were handled by 'run_linter.py'."

echo -e "${COLOR_YELLOW}==========================================${COLOR_NC}"
echo -e "${COLOR_YELLOW}   All Audits Complete                    ${COLOR_NC}"
echo -e "${COLOR_YELLOW}==========================================${COLOR_NC}"

# Exit with 0 if all steps completed without critical errors
exit 0
