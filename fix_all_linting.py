#!/usr/bin/env python3
"""
Script to automatically fix linting issues across the entire VoidLink codebase.
This script uses autopep8 to fix common Python style issues.
"""

import os
import sys
import subprocess
import glob
import argparse


def find_python_files(directory):
    """Find all Python files in the given directory and its subdirectories"""
    python_files = []
    for root, dirs, files in os.walk(directory):
        # Skip virtual environment directories
        if "venv" in root or "env" in root or "__pycache__" in root:
            continue

        for file in files:
            if file.endswith(".py"):
                python_files.append(os.path.join(root, file))

    return python_files


def fix_file(file_path, aggressive=False):
    """Fix linting issues in a single file using autopep8"""
    print(f"Fixing {file_path}...")

    # Determine aggressiveness level
    aggressive_arg = []
    if aggressive:
        aggressive_arg = ["--aggressive", "--aggressive"]

    try:
        # Run autopep8 on the file
        result = subprocess.run(
            ["autopep8", "--in-place"] + aggressive_arg + [file_path],
            check=True,
            capture_output=True,
            text=True
        )

        if result.stderr:
            print(f"  Warning: {result.stderr}")

        return True
    except subprocess.CalledProcessError as e:
        print(f"  Error: {e.stderr}")
        return False
    except FileNotFoundError:
        print("  Error: autopep8 not found. Please install it with 'pip install autopep8'.")
        return False


def fix_all_files(directory, aggressive=False):
    """Fix linting issues in all Python files in the given directory"""
    python_files = find_python_files(directory)

    if not python_files:
        print(f"No Python files found in {directory}")
        return

    print(f"Found {len(python_files)} Python files to fix")

    success_count = 0
    for file_path in python_files:
        if fix_file(file_path, aggressive):
            success_count += 1

    print(f"Fixed {success_count} out of {len(python_files)} files")


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Fix linting issues in Python files")
    parser.add_argument(
        "--directory",
        "-d",
        default=".",
        help="Directory to search for Python files")
    parser.add_argument(
        "--aggressive",
        "-a",
        action="store_true",
        help="Use aggressive autopep8 mode")
    parser.add_argument("--file", "-f", help="Fix a specific file instead of all files")
    args = parser.parse_args()

    # Check if autopep8 is installed
    try:
        subprocess.run(["autopep8", "--version"], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Error: autopep8 not found. Please install it with 'pip install autopep8'.")
        return 1

    # Fix a specific file or all files
    if args.file:
        if not os.path.exists(args.file):
            print(f"Error: File {args.file} not found")
            return 1

        if fix_file(args.file, args.aggressive):
            print(f"Successfully fixed {args.file}")
            return 0
        else:
            print(f"Failed to fix {args.file}")
            return 1
    else:
        fix_all_files(args.directory, args.aggressive)
        return 0


if __name__ == "__main__":
    sys.exit(main())
