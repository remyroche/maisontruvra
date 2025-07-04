#!/usr/bin/env python3
import subprocess
import sys
from datetime import datetime

# --- Configuration ---
# Centralized Ruff rule selection for consistency.
# E,F: Standard flake8
# B: flake8-bugbear
# SIM: flake8-simplify
# PL: Pylint
# D: pydocstyle
# TID252: flake8-tidy-imports
# I: isort (import sorting)
# UP: pyupgrade (modernize syntax)
RUFF_SELECT = "E,F,B,SIM,PL,D,TID252,I,UP"

# Directory to exclude from all operations
EXCLUDE_DIR = "website/node_modules"

def run_command(command, description):
    """Runs a command, prints a description, and handles common errors."""
    print(f"--- {description}... ---")
    try:
        # Using check=True to automatically raise an exception on non-zero exit codes.
        # We capture output to prevent it from cluttering the main script's output.
        subprocess.run(command, check=True, capture_output=True, text=True)
        print(f"--- {description} complete. ---")
    except FileNotFoundError:
        print(f"Error: '{command[0]}' command not found. Is it installed and in your PATH?", file=sys.stderr)
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        # This will catch errors from the command itself, like syntax errors.
        print(f"Error during '{description}'. Return code: {e.returncode}", file=sys.stderr)
        print(f"Stdout:\n{e.stdout}", file=sys.stderr)
        print(f"Stderr:\n{e.stderr}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred during '{description}': {e}", file=sys.stderr)
        sys.exit(1)

def main():
    """
    Formats, lints, and auto-fixes the current directory using Ruff, generating reports.
    """
    # Generate a timestamp for unique report filenames
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    
    # Consistent file paths for reports with timestamps
    fix_diff_file = f"{timestamp}_ruff_fix_diff.txt"
    full_report_file = f"{timestamp}_ruff_full_report.txt"
    unfixed_report_file = f"{timestamp}_ruff_unfixed_report.txt"

    # --- Step 1: Format the codebase (replaces Black) ---
    format_command = [
        "ruff", "format", ".",
        f"--exclude={EXCLUDE_DIR}"
    ]
    run_command(format_command, "Formatting with Ruff (Black equivalent)")

    # --- Step 2: Lint, apply fixes, and generate initial reports ---
    print("--- Linting and auto-fixing with a comprehensive Ruff configuration... ---")
    
    # Base command for linting checks
    base_check_command = [
        "ruff", "check", ".",
        f"--select={RUFF_SELECT}",
        "--ignore=E501",
        f"--exclude={EXCLUDE_DIR}"
    ]
    
    issues_found = False
    try:
        # This single command applies fixes, captures the diff, and saves the full report.
        fix_command = base_check_command + [
            "--fix",
            "--diff",
            f"--output-file={full_report_file}"
        ]
        
        result = subprocess.run(
            fix_command,
            capture_output=True,
            text=True,
            check=False
        )

        with open(fix_diff_file, "w") as f:
            f.write(result.stdout)
        
        print(f"--- Ruff fix diff saved to {fix_diff_file} ---")
        print(f"--- Full report saved to {full_report_file} ---")

        if result.returncode > 1:
            print(f"Ruff encountered an error. Stderr:\n{result.stderr}", file=sys.stderr)
            sys.exit(result.returncode)
        
        issues_found = result.returncode == 1

    except FileNotFoundError:
        print("Error: 'ruff' command not found. Is Ruff installed and in your PATH?", file=sys.stderr)
        sys.exit(1)

    # --- Step 3: Generate a report of any remaining (unfixed) issues ---
    if issues_found:
        print("--- Checking for remaining (unfixed) issues... ---")
        try:
            unfixed_command = base_check_command + [f"--output-file={unfixed_report_file}"]
            subprocess.run(unfixed_command, check=False)
            print(f"--- Remaining issues saved to {unfixed_report_file} ---")
        except Exception as e:
            print(f"An error occurred while checking for unfixed issues: {e}", file=sys.stderr)
    else:
        with open(unfixed_report_file, "w") as f:
            f.write("No issues found.\n")
        print("--- No remaining issues found. ---")

    print("\n--- All linting and formatting tasks complete. ---")

if __name__ == "__main__":
    main()
