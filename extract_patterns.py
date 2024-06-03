import os
import hashlib

def hash_pattern_content(content):
    """Compute the hash of the pattern content."""
    hash_obj = hashlib.sha256()
    hash_obj.update(content.encode('utf-8'))
    return hash_obj.hexdigest()

def calculate_density(pattern_content):
    """Calculate the density of non-space and non-period characters in the pattern content."""
    return sum(1 for char in pattern_content if char not in {' ', '.', '-', '\n', '|'})

def extract_patterns(file_content, filename):
    """Extract patterns from file content handling multiple [Module] sections."""
    patterns = []
    lines = file_content.splitlines()
    in_pattern = False
    pattern_number = None
    pattern_content = []
    module_count = 0

    for line in lines:
        if line.startswith('[Module]'):
            module_count += 1
        if line.startswith('[Pattern'):
            if in_pattern and pattern_content:
                # Store the previous pattern before starting a new one
                pattern_str = '\n'.join(pattern_content).strip()
                num_lines = len(pattern_content)
                uri = f"{filename}/Pattern{pattern_number}.{module_count}"
                patterns.append((pattern_number, num_lines, uri, pattern_str))
            
            # Start a new pattern
            in_pattern = True
            pattern_number = line.split(']')[0][8:]
            pattern_content = [line]
        elif in_pattern:
            if line.startswith('[') and not line.startswith('[Pattern'):
                # End of the current pattern
                pattern_str = '\n'.join(pattern_content).strip()
                num_lines = len(pattern_content)
                uri = f"{filename}/Pattern{pattern_number}.{module_count}"
                patterns.append((pattern_number, num_lines, uri, pattern_str))
                in_pattern = False
                pattern_content = []
            else:
                pattern_content.append(line)
    
    # Add the last pattern if any
    if in_pattern and pattern_content:
        pattern_str = '\n'.join(pattern_content).strip()
        num_lines = len(pattern_content)
        uri = f"{filename}/Pattern{pattern_number}.{module_count}"
        patterns.append((pattern_number, num_lines, uri, pattern_str))
    
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
                
                if not content.startswith('[Module]'):
                    print(f"Skipping file (no [Module] start): {full_file_path}")
                    continue
                
                patterns = extract_patterns(content, os.path.basename(full_file_path))
                for pattern_number, num_lines, uri, pattern_content in patterns:
                    pattern_hash = hash_pattern_content(pattern_content)
                    if pattern_hash not in patterns_set:
                        patterns_set.add(pattern_hash)
                        density = calculate_density(pattern_content)
                        unique_patterns.append((pattern_number, num_lines, uri, pattern_content, density))
                        print(f"\tFound a unique pattern: {uri}")
                    else:
                        print(f"\tDuplicate pattern: {uri}")

    # Sort unique patterns by number of lines and density
    unique_patterns.sort(key=lambda x: (x[1], x[4]))

    # Save unique patterns to the output file with unique enumeration
    with open(output_file, 'w', encoding='utf-8') as f_out:
        for idx, (pattern_number, num_lines, uri, pattern_content, density) in enumerate(unique_patterns):
            f_out.write(f"[Pattern{idx}] [Density={density}] [Lines={num_lines-2}] [URI={uri}]\n")
            if pattern_content.startswith('[Pattern'):
                #replace the first line with the pattern number
                pattern_content = pattern_content.split('\n', 1)[1]
                f_out.write(f"{pattern_content}\n\n")
            else:
                print(f"Pattern does not start with [Pattern]: {uri}")

# Example usage:
input_folder = './all_txt/'
output_file = 'unique_patterns.txt'
scan_and_extract_patterns(input_folder, output_file)
