#!/usr/bin/env python3
"""
Script to fix common syntax issues in Python files that autopep8 might not catch.
"""

import os
import sys
import re
import argparse
import ast


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


def check_syntax(file_path):
    """Check if a file has syntax errors"""
    with open(file_path, 'r', encoding='utf-8') as file:
        try:
            content = file.read()
            ast.parse(content)
            return True, None
        except SyntaxError as e:
            return False, e


def fix_indentation_issues(content):
    """Fix common indentation issues"""
    # Fix inconsistent indentation (mix of tabs and spaces)
    lines = content.split('\n')
    fixed_lines = []

    for line in lines:
        # Replace tabs with 4 spaces
        if '\t' in line:
            fixed_line = line.replace('\t', '    ')
            fixed_lines.append(fixed_line)
        else:
            fixed_lines.append(line)

    return '\n'.join(fixed_lines)


def fix_missing_colons(content):
    """Fix missing colons in if/for/while/def/class statements"""
    patterns = [
        (r'(if\s+[^:]+)\s*$', r'\1:'),
        (r'(elif\s+[^:]+)\s*$', r'\1:'),
        (r'(else)\s*$', r'else:'),
        (r'(for\s+[^:]+)\s*$', r'\1:'),
        (r'(while\s+[^:]+)\s*$', r'\1:'),
        (r'(def\s+[^:]+)\s*$', r'\1:'),
        (r'(class\s+[^:]+)\s*$', r'\1:'),
        (r'(try)\s*$', r'try:'),
        (r'(except\s*[^:]*)\s*$', r'\1:'),
        (r'(finally)\s*$', r'finally:')
    ]

    fixed_content = content
    for pattern, replacement in patterns:
        fixed_content = re.sub(pattern, replacement, fixed_content)

    return fixed_content


def fix_mismatched_parentheses(content):
    """Fix mismatched parentheses, brackets, and braces"""
    # This is a simple approach and might not catch all issues
    lines = content.split('\n')
    fixed_lines = []

    for line in lines:
        # Count opening and closing parentheses
        open_parens = line.count('(')
        close_parens = line.count(')')

        # Count opening and closing brackets
        open_brackets = line.count('[')
        close_brackets = line.count(']')

        # Count opening and closing braces
        open_braces = line.count('{')
        close_braces = line.count('}')

        # Fix mismatched parentheses
        if open_parens > close_parens:
            line += ')' * (open_parens - close_parens)
        elif close_parens > open_parens:
            line = '(' * (close_parens - open_parens) + line

        # Fix mismatched brackets
        if open_brackets > close_brackets:
            line += ']' * (open_brackets - close_brackets)
        elif close_brackets > open_brackets:
            line = '[' * (close_brackets - open_brackets) + line

        # Fix mismatched braces
        if open_braces > close_braces:
            line += '}' * (open_braces - close_braces)
        elif close_braces > open_braces:
            line = '{' * (close_braces - open_braces) + line

        fixed_lines.append(line)

    return '\n'.join(fixed_lines)


def fix_missing_imports(content, file_path):
    """Fix missing imports based on common patterns"""
    # This is a simple approach and might not catch all issues
    imports_to_add = []

    # Check for common modules that might be used without being imported
    if 'json.dumps' in content or 'json.loads' in content:
        if 'import json' not in content and 'from json import' not in content:
            imports_to_add.append('import json')

    if 'os.path' in content:
        if 'import os' not in content and 'from os import' not in content:
            imports_to_add.append('import os')

    if 'sys.exit' in content or 'sys.argv' in content:
        if 'import sys' not in content and 'from sys import' not in content:
            imports_to_add.append('import sys')

    if 'time.time' in content or 'time.sleep' in content:
        if 'import time' not in content and 'from time import' not in content:
            imports_to_add.append('import time')

    if 'datetime.datetime' in content or 'datetime.timedelta' in content:
        if 'import datetime' not in content and 'from datetime import' not in content:
            imports_to_add.append('import datetime')

    if 're.match' in content or 're.search' in content or 're.sub' in content:
        if 'import re' not in content and 'from re import' not in content:
            imports_to_add.append('import re')

    # Add imports if needed
    if imports_to_add:
        # Find the position to insert imports
        lines = content.split('\n')
        insert_pos = 0

        # Skip shebang and docstring
        for i, line in enumerate(lines):
            if i == 0 and line.startswith('#!'):
                insert_pos = 1
                continue

            if line.strip().startswith('"""') or line.strip().startswith("'''"):
                # Skip until the end of the docstring
                for j in range(i + 1, len(lines)):
                    if lines[j].strip().endswith('"""') or lines[j].strip().endswith("'''"):
                        insert_pos = j + 1
                        break
                break

            if line.strip() and not line.startswith('#'):
                insert_pos = i
                break

        # Insert imports
        for imp in imports_to_add:
            lines.insert(insert_pos, imp)
            insert_pos += 1

        return '\n'.join(lines)

    return content


def fix_syntax_issues(file_path):
    """Fix syntax issues in a single file"""
    print(f"Checking {file_path}...")

    # Check if the file has syntax errors
    syntax_ok, error = check_syntax(file_path)
    if syntax_ok:
        print(f"  No syntax errors found in {file_path}")
        return True

    print(f"  Syntax error found in {file_path}: {error}")

    # Read the file content
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # Apply fixes
    fixed_content = content
    fixed_content = fix_indentation_issues(fixed_content)
    fixed_content = fix_missing_colons(fixed_content)
    fixed_content = fix_mismatched_parentheses(fixed_content)
    fixed_content = fix_missing_imports(fixed_content, file_path)

    # Check if the fixes resolved the syntax errors
    try:
        ast.parse(fixed_content)
        print(f"  Syntax issues fixed in {file_path}")

        # Write the fixed content back to the file
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(fixed_content)

        return True
    except SyntaxError as e:
        print(f"  Failed to fix all syntax issues in {file_path}: {e}")
        return False


def fix_all_files(directory):
    """Fix syntax issues in all Python files in the given directory"""
    python_files = find_python_files(directory)

    if not python_files:
        print(f"No Python files found in {directory}")
        return

    print(f"Found {len(python_files)} Python files to check")

    success_count = 0
    for file_path in python_files:
        if fix_syntax_issues(file_path):
            success_count += 1

    print(f"Fixed syntax issues in {success_count} out of {len(python_files)} files")


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Fix syntax issues in Python files")
    parser.add_argument(
        "--directory",
        "-d",
        default=".",
        help="Directory to search for Python files")
    parser.add_argument("--file", "-f", help="Fix a specific file instead of all files")
    args = parser.parse_args()

    # Fix a specific file or all files
    if args.file:
        if not os.path.exists(args.file):
            print(f"Error: File {args.file} not found")
            return 1

        if fix_syntax_issues(args.file):
            print(f"Successfully fixed syntax issues in {args.file}")
            return 0
        else:
            print(f"Failed to fix all syntax issues in {args.file}")
            return 1
    else:
        fix_all_files(args.directory)
        return 0


if __name__ == "__main__":
    sys.exit(main())
