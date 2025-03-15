#!/usr/bin/env python3
"""
VoidLink Linting Fixes - Script to fix common linting issues
"""

import os
import re
import sys
from typing import List, Dict, Tuple


def fix_imports(file_path: str) -> int:
    """Fix import order and grouping"""
    with open(file_path, 'r') as file:
        content = file.read()

    # Find import statements
    import_pattern = r'((?:from [.\w]+ import .*|import .*)\n)+'
    imports_match = re.search(import_pattern, content)

    if not imports_match:
        return 0

    imports_block = imports_match.group(0)
    imports = imports_block.strip().split('\n')

    # Sort imports
    std_lib_imports = []
    third_party_imports = []
    local_imports = []

    for imp in imports:
        if imp.startswith('import '):
            module = imp.split()[1].split('.')[0]
            if module in sys.stdlib_module_names:
                std_lib_imports.append(imp)
            else:
                third_party_imports.append(imp)
        elif imp.startswith('from '):
            module = imp.split()[1].split('.')[0]
            if module in sys.stdlib_module_names:
                std_lib_imports.append(imp)
            elif module == '.' or module.startswith('.'):
                local_imports.append(imp)
            else:
                third_party_imports.append(imp)

    # Sort each group
    std_lib_imports.sort()
    third_party_imports.sort()
    local_imports.sort()

    # Combine groups with blank lines between them
    new_imports = '\n'.join(std_lib_imports)
    if std_lib_imports and (third_party_imports or local_imports):
        new_imports += '\n\n'

    if third_party_imports:
        new_imports += '\n'.join(third_party_imports)
        if local_imports:
            new_imports += '\n\n'

    if local_imports:
        new_imports += '\n'.join(local_imports)

    new_imports += '\n\n'

    # Replace old imports with new imports
    new_content = content.replace(imports_block, new_imports)

    if new_content != content:
        with open(file_path, 'w') as file:
            file.write(new_content)
        return 1

    return 0


def fix_line_length(file_path: str, max_length: int = 100) -> int:
    """Fix lines that are too long"""
    with open(file_path, 'r') as file:
        lines = file.readlines()

    fixed_count = 0
    fixed_lines = []

    for line in lines:
        if len(line.rstrip()) > max_length:
            # Try to break at a sensible point
            if '=' in line:
                parts = line.split('=', 1)
                indent = len(parts[0]) - len(parts[0].lstrip())
                new_indent = ' ' * (indent + 4)
                fixed_line = parts[0] + '=\\\n' + new_indent + parts[1].lstrip()
                fixed_lines.append(fixed_line)
                fixed_count += 1
            elif ',' in line:
                # Break at a comma
                last_comma = line.rstrip().rfind(',', 0, max_length)
                if last_comma > 0:
                    indent = len(line) - len(line.lstrip())
                    new_indent = ' ' * indent
                    fixed_line = line[:last_comma + 1] + '\n' + \
                        new_indent + line[last_comma + 1:].lstrip()
                    fixed_lines.append(fixed_line)
                    fixed_count += 1
                else:
                    fixed_lines.append(line)
            else:
                fixed_lines.append(line)
        else:
            fixed_lines.append(line)

    if fixed_count > 0:
        with open(file_path, 'w') as file:
            file.writelines(fixed_lines)

    return fixed_count


def fix_whitespace(file_path: str) -> int:
    """Fix whitespace issues (trailing whitespace, blank lines)"""
    with open(file_path, 'r') as file:
        lines = file.readlines()

    fixed_count = 0
    fixed_lines = []

    for line in lines:
        # Remove trailing whitespace
        stripped = line.rstrip()
        if stripped != line.rstrip('\n'):
            fixed_count += 1

        if stripped:
            fixed_lines.append(stripped + '\n')
        else:
            fixed_lines.append('\n')

    # Remove multiple blank lines
    i = 0
    while i < len(fixed_lines) - 1:
        if fixed_lines[i] == '\n' and fixed_lines[i + 1] == '\n':
            # Check for more than 2 consecutive blank lines
            j = i + 2
            while j < len(fixed_lines) and fixed_lines[j] == '\n':
                fixed_lines.pop(j)
                fixed_count += 1
        i += 1

    if fixed_count > 0:
        with open(file_path, 'w') as file:
            file.writelines(fixed_lines)

    return fixed_count


def fix_docstrings(file_path: str) -> int:
    """Fix missing or malformed docstrings"""
    with open(file_path, 'r') as file:
        content = file.read()

    # Find function definitions without docstrings
    func_pattern = r'def\s+(\w+)\s*\([^)]*\)\s*:'
    func_matches = re.finditer(func_pattern, content)

    fixed_count = 0
    new_content = content

    for match in func_matches:
        func_name = match.group(1)
        func_start = match.end()

        # Check if there's a docstring after the function definition
        docstring_pattern = r'\s*"""[^"]*"""'
        docstring_match = re.match(docstring_pattern, content[func_start:])

        if not docstring_match:
            # No docstring found, add a simple one
            indent_match = re.match(r'\s*', content[func_start:])
            indent = indent_match.group(0) if indent_match else '    '

            # Insert docstring after function definition
            new_docstring = f'\n{indent}"""Function {func_name}"""\n'
            new_content = new_content[:func_start] + new_docstring + new_content[func_start:]

            # Adjust positions for subsequent matches
            func_start += len(new_docstring)
            fixed_count += 1

    if fixed_count > 0:
        with open(file_path, 'w') as file:
            file.write(new_content)

    return fixed_count


def fix_variable_names(file_path: str) -> int:
    """Fix non-snake_case variable names"""
    with open(file_path, 'r') as file:
        content = file.read()

    # Find variable assignments with camelCase
    var_pattern = r'([a-z]+[a-z0-9]*[A-Z][a-zA-Z0-9]*)\s*='
    var_matches = re.finditer(var_pattern, content)

    fixed_count = 0
    replacements = {}

    for match in var_matches:
        camel_case = match.group(1)

        # Convert camelCase to snake_case
        snake_case = re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', camel_case).lower()

        if camel_case != snake_case:
            replacements[camel_case] = snake_case
            fixed_count += 1

    # Apply replacements
    new_content = content
    for camel, snake in replacements.items():
        # Replace variable assignments
        new_content = re.sub(r'\b' + camel + r'\b\s*=', snake + ' =', new_content)

        # Replace variable usages
        new_content = re.sub(r'\b' + camel + r'\b', snake, new_content)

    if fixed_count > 0:
        with open(file_path, 'w') as file:
            file.write(new_content)

    return fixed_count


def fix_python_file(file_path: str) -> Dict[str, int]:
    """Apply all fixes to a Python file"""
    results = {
        'imports': fix_imports(file_path),
        'line_length': fix_line_length(file_path),
        'whitespace': fix_whitespace(file_path),
        'docstrings': fix_docstrings(file_path),
        'variable_names': fix_variable_names(file_path)
    }

    return results


def find_python_files(directory: str) -> List[str]:
    """Find all Python files in a directory"""
    python_files = []

    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))

    return python_files


def main():
    """Main function to fix linting issues"""
    directory = os.path.dirname(os.path.abspath(__file__))
    python_files = find_python_files(directory)

    total_fixes = {
        'imports': 0,
        'line_length': 0,
        'whitespace': 0,
        'docstrings': 0,
        'variable_names': 0
    }

    for file_path in python_files:
        print(f"Fixing {os.path.basename(file_path)}...")
        results = fix_python_file(file_path)

        for fix_type, count in results.items():
            total_fixes[fix_type] += count

    print("\nLinting fixes applied:")
    print(f"- Import order: {total_fixes['imports']} files")
    print(f"- Line length: {total_fixes['line_length']} lines")
    print(f"- Whitespace: {total_fixes['whitespace']} issues")
    print(f"- Docstrings: {total_fixes['docstrings']} functions")
    print(f"- Variable names: {total_fixes['variable_names']} variables")


if __name__ == "__main__":
    main()
