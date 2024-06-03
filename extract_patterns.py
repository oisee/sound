import os
import re
import hashlib

def hash_pattern_content(content):
    """Compute the hash of the pattern content."""
    hash_obj = hashlib.sha256()
    hash_obj.update(content.encode('utf-8'))
    return hash_obj.hexdigest()

def extract_patterns(file_content, filename):
    """Extract patterns from file content."""
    pattern_regex = re.compile(r'\[Pattern(\d+)\](.*?)((?=\[Pattern\d+\])|$)', re.DOTALL)
    patterns = []
    for match in pattern_regex.finditer(file_content):
        pattern_number = match.group(1)
        pattern_content = match.group(2).strip()
        uri = f"{filename}_Pattern{pattern_number}"
        patterns.append((uri, pattern_content))
    return patterns

def scan_and_extract_patterns(input_folder, output_file):
    patterns_set = set()
    unique_patterns = []

    # Walk through the directory recursively
    for root, dirs, files in os.walk(input_folder):
        for file in files:
            if file.lower().endswith('.txt') or file.lower().endswith('.vt2'):
                # Construct full file path
                full_file_path = os.path.join(root, file)
                print(f"Processing: {full_file_path}")
                
                try:
                    # Try to open the file with UTF-8 encoding
                    with open(full_file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                except UnicodeDecodeError:
                    # If UTF-8 fails, try ISO-8859-1
                    with open(full_file_path, 'r', encoding='ISO-8859-1') as f:
                        content = f.read()            
                
                patterns = extract_patterns(content, os.path.basename(full_file_path))
                for uri, pattern_content in patterns:
                    pattern_hash = hash_pattern_content(pattern_content)
                    if pattern_hash not in patterns_set:
                        patterns_set.add(pattern_hash)
                        unique_patterns.append((uri, pattern_content))
                        print(f"\tFound a unique pattern: {uri}")
                    else:
                        print(f"\tDuplicate pattern: {uri}")

    # Save unique patterns to the output file
    with open(output_file, 'w', encoding='utf-8') as f_out:
        for uri, pattern_content in unique_patterns:
            f_out.write(f"URI: {uri}\n")
            f_out.write(f"{pattern_content}\n\n")

# Example usage:
input_folder = './all_txt/'
output_file = 'unique_patterns.txt'
scan_and_extract_patterns(input_folder, output_file)
