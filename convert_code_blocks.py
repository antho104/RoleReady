#!/usr/bin/env python3
"""
Convert indented code blocks to fenced code blocks with language tags.
Detects language based on context clues (file extensions, keywords, etc.)
"""

import re
import sys

def detect_language(context_before, code_content):
    """Detect programming language from context and content."""
    context = context_before.lower()
    code_lower = code_content.lower()

    # Check context for file extensions or explicit mentions
    if '.py' in context or 'python' in context or 'pytest' in context:
        return 'python'
    if '.ts' in context or 'typescript' in context or '.tsx' in context:
        return 'typescript'
    if '.js' in context or 'javascript' in context or '.jsx' in context:
        return 'javascript'
    if 'bash' in context or 'shell' in context or 'terminal' in context:
        return 'bash'
    if '.json' in context or 'package.json' in context:
        return 'json'
    if '.yaml' in context or '.yml' in context:
        return 'yaml'
    if 'sql' in context or 'query' in context:
        return 'sql'

    # Check code content for language-specific patterns
    if re.search(r'\bdef\s+\w+\(|import\s+\w+|from\s+\w+\s+import|\bclass\s+\w+:|__init__|lambda\s+\w+:', code_content):
        return 'python'
    if re.search(r'\bconst\s+\w+|let\s+\w+|function\s+\w+|export\s+(class|interface|const)|=>|\.tsx?', code_content):
        return 'typescript'
    if re.search(r'^\s*[{}\[\]]|\baws\b.*:|".*":\s*[{\[]', code_content, re.MULTILINE):
        if '{' in code_content and '"' in code_content:
            return 'json'
    if re.search(r'^\s*-\s+\w+:|^\s+\w+:\s*$', code_content, re.MULTILINE):
        return 'yaml'
    if re.search(r'\b(SELECT|FROM|WHERE|INSERT|UPDATE|DELETE)\b', code_content, re.IGNORECASE):
        return 'sql'
    if re.search(r'^\s*#\s*\w+|^\s*\$\s+\w+|cd\s+|ls\s+|npm\s+|git\s+', code_content, re.MULTILINE):
        return 'bash'

    # Default to no language (plain text)
    return ''

def convert_indented_to_fenced(content):
    """Convert 4-space indented code blocks to fenced code blocks with language tags."""
    lines = content.split('\n')
    result = []
    i = 0

    while i < len(lines):
        line = lines[i]

        # Check if this line starts a code block (4+ spaces or tab, not a list continuation)
        if line and (line.startswith('    ') or line.startswith('\t')) and not re.match(r'^\s*[-*+]\s+', line):
            # Gather context (previous non-empty lines)
            context_lines = []
            for j in range(max(0, i-5), i):
                if lines[j].strip():
                    context_lines.append(lines[j])
            context = ' '.join(context_lines)

            # Collect all consecutive indented lines
            code_lines = []
            j = i
            while j < len(lines):
                if lines[j] and (lines[j].startswith('    ') or lines[j].startswith('\t')):
                    # Remove 4 spaces or 1 tab
                    if lines[j].startswith('    '):
                        code_lines.append(lines[j][4:])
                    else:
                        code_lines.append(lines[j][1:])
                    j += 1
                elif not lines[j].strip():  # Allow blank lines within code block
                    code_lines.append('')
                    j += 1
                else:
                    break

            # Remove trailing blank lines
            while code_lines and not code_lines[-1].strip():
                code_lines.pop()

            if code_lines:
                code_content = '\n'.join(code_lines)
                language = detect_language(context, code_content)

                # Add fenced code block
                result.append(f'```{language}')
                result.extend(code_lines)
                result.append('```')

                i = j
                continue

        result.append(line)
        i += 1

    return '\n'.join(result)

if __name__ == '__main__':
    input_file = 'TECHNICAL_DOCUMENTATION_from_docx.md'
    output_file = 'TECHNICAL_DOCUMENTATION_from_docx_fenced.md'

    print(f"Reading {input_file}...")
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()

    print("Converting indented code blocks to fenced code blocks...")
    converted = convert_indented_to_fenced(content)

    print(f"Writing to {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(converted)

    # Count conversions
    original_indented = len(re.findall(r'^    \w', content, re.MULTILINE))
    fenced_blocks = len(re.findall(r'^```', converted, re.MULTILINE)) // 2

    print(f"✅ Conversion complete!")
    print(f"   - Found ~{original_indented} indented code lines")
    print(f"   - Created {fenced_blocks} fenced code blocks")
    print(f"   - Output: {output_file}")
