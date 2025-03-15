#!/usr/bin/env python3
"""
Quick Lint Fix - Fixes the most common linting issues
"""

import os
import re
import sys


def fix_file(file_path):
    """Fix common linting issues in a file"""
    with open(file_path, 'r') as file:
        content = file.read()

    # Fix 1: Remove trailing whitespace
    content = re.sub(r'[ \t]+$', '', content, flags=re.MULTILINE)

    # Fix 2: Ensure final newline
    if not content.endswith('\n'):
        content += '\n'

    # Fix 3: Remove multiple blank lines (more than 2)
    content = re.sub(r'\n{3,}', '\n\n', content)

    # Fix 4: Fix indentation (4 spaces instead of tabs)
    content = content.replace('\t', '    ')

    # Fix 5: Fix imports (add newline after imports)
    content = re.sub(r'((?:from [.\w]+ import .*|import .*)\n)(?=[^\n])', r'\1\n', content)

    # Fix 6: Fix missing whitespace after commas
    content = re.sub(r',([^\s])', r', \1', content)

    # Fix 7: Fix missing whitespace around operators
    content = re.sub(r'([^\s])([+\-*/=<>])([^\s])', r'\1 \2 \3', content)

    # Write the fixed content back to the file
    with open(file_path, 'w') as file:
        file.write(content)


def main():
    """Main function"""
    # Find all Python files in the current directory and subdirectories
    python_files = []
    for root, _, files in os.walk('.'):
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))

    # Fix each file
    for file_path in python_files:
        print(f"Fixing {file_path}...")
        fix_file(file_path)

    print(f"Fixed {len(python_files)} files.")


if __name__ == '__main__':
    main()
