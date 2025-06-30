#!/bin/bash

# This script runs a series of audits on the Maison Truvra codebase.
# It checks for best practices, security vulnerabilities, and code quality.

# Define colors for output (these will still be in the file, but won't render as colors in a plain text editor)
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Define the log file name
LOG_FILE="audit_log_$(date +%Y%m%d_%H%M%S).txt"

# Redirect all stdout and stderr to the log file
exec > >(tee -a "$LOG_FILE") 2>&1

echo -e "${YELLOW}==========================================${NC}"
echo -e "${YELLOW}   Starting Maison Truvra Code Audits     ${NC}"
echo -e "${YELLOW}==========================================${NC}"

# --- 1. Best Practices & Static Analysis Audit (Backend) ---
echo -e "\n${GREEN}--- Running Backend Best Practices Audit ---${NC}"
python3 best_practices_audit.py
echo -e "${GREEN}--- Backend Best Practices Audit Complete ---\n${NC}"

# --- 2. Security Focused Audit (Backend) ---
echo -e "${GREEN}--- Running Backend Security Audit ---${NC}"
python3 security_audit.py
echo -e "${GREEN}--- Backend Security Audit Complete ---\n${NC}"


# --- 3. Dependency & Component Security ---
echo -e "${GREEN}--- Running Dependency & Component Security Audit ---${NC}"

# 3a. Backend Python Dependencies
echo -e "\n${YELLOW}Scanning Python dependencies for vulnerabilities...${NC}"
# First, ensure safety is installed
if ! python3 -m pip show safety &> /dev/null; then
    echo "Installing safety..."
    python3 -m pip install safety
fi
# Run the check against the requirements file
python3 -m safety check -r backend/requirements.txt
if [ $? -eq 0 ]; then
    echo -e "${GREEN}No known security vulnerabilities found in Python packages.${NC}"
else
    echo -e "${RED}Vulnerabilities found in Python packages. Please review the output above.${NC}"
fi

# 3b. Frontend Node.js Dependencies
echo -e "\n${YELLOW}Scanning Node.js dependencies for vulnerabilities...${NC}"
# Navigate to the website directory to run npm audit
(cd website && npm audit)
if [ $? -eq 0 ]; then
    echo -e "${GREEN}No known security vulnerabilities found in Node.js packages.${NC}"
else
    echo -e "${RED}Vulnerabilities found in Node.js packages. Please review the output above.${NC}"
fi

echo -e "${GREEN}--- Dependency & Component Security Audit Complete ---\n${NC}"


echo -e "${YELLOW}==========================================${NC}"
echo -e "${YELLOW}   All Audits Complete                    ${NC}"
echo -e "${YELLOW}==========================================${NC}"

# Restore stdout and stderr (optional, but good practice if the script continues after logging)
exec 1>&3 2>&4