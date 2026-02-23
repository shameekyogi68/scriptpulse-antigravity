import re
import os

def clean_file(filepath):
    with open(filepath, 'r') as f:
        content = f.read()

    # Remove the specific bracketed prefixes and emojis
    replacements = [
        (r'\(\+\)\s+', ''),
        (r'\(\-\)\s+', ''),
        (r'\(\^\)\s+', ''),
        (r'\(\!\)\s+', ''),
        (r'\(Net\)\s+', ''),
        (r'\(Chart\)\s+', ''),
        (r'\(Settings\)\s+', ''),
        (r'\(Lab\)\s+', ''),
        (r'\(Download\)\s+', ''),
        (r'\(Inspect\)\s+', ''),
        (r'\[\!\]\s+', ''),
        (r'\[OK\]\s+', ''),
        (r'\[RUN\]\s+', ''),
        (r'🩺\s+', ''),
        (r'🔬\s+', ''),
        (r'\(Archive\)\s+', ''),
        (r'\(\?\)\s+', ''),
        (r'\[\+\]\s+', ''),
        (r'\[\-\]\s+', ''),
        (r'\[\!\]\s+', ''),
        (r'\[OK\]\s+', ''),
        (r'\[~\]\s+', ''),
        (r'\(\-\>\)\s+', ''),
    ]

    new_content = content
    for pat, repl in replacements:
        new_content = re.sub(pat, repl, new_content)

    if new_content != content:
        with open(filepath, 'w') as f:
            f.write(new_content)
        print(f"Cleaned {filepath}")

for root, _, files in os.walk('scriptpulse/reporters'):
    for file in files:
        if file.endswith('.py'):
            clean_file(os.path.join(root, file))
