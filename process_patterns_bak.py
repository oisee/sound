import re
import statistics
import json

class Pattern:
    def __init__(self, number, density, lines, uri, content, masks=None, skip_lines=1):
        self.number = number
        self.density = density
        self.lines = lines
        self.uri = uri
        self.content = content
        self.masks = masks if masks is not None else []
        self.skip_lines = skip_lines
        self.processed_content = content

def parse_file(file_path):
    patterns = []
    with open(file_path, 'r') as file:
        content = file.read()

    pattern_regex = re.compile(r'\[Pattern(?P<number>\d+)\] \[Density=(?P<density>\d+)\] \[Lines=(?P<lines>\d+)\] \[URI=(?P<uri>[^\]]+)\]\n(?P<content>.*?)(?=\n\[Pattern|\Z)', re.S)
    for match in pattern_regex.finditer(content):
        number = int(match.group('number'))
        density = int(match.group('density'))
        lines = int(match.group('lines'))
        uri = match.group('uri')
        content = match.group('content') #.strip() # 
        # Create pattern with default masks and skip_lines
        patterns.append(Pattern(number, density, lines, uri, content))
    
    return patterns

def compute_statistics(patterns):
    densities = [pattern.density for pattern in patterns]
    lines = [pattern.lines for pattern in patterns]
    return {
        'lowest_density': min(densities),
        'highest_density': max(densities),
        'average_density': sum(densities) / len(densities),
        'median_density': statistics.median(densities),
        'lowest_lines': min(lines),
        'highest_lines': max(lines),
    }

def filter_patterns(patterns, min_density=None, max_density=None, min_lines=None, max_lines=None):
    filtered = patterns
    if min_density is not None:
        filtered = [pattern for pattern in filtered if pattern.density >= min_density]
    if max_density is not None:
        filtered = [pattern for pattern in filtered if pattern.density <= max_density]
    if min_lines is not None:
        filtered = [pattern for pattern in filtered if pattern.lines >= min_lines]
    if max_lines is not None:
        filtered = [pattern for pattern in filtered if pattern.lines <= max_lines]
    return filtered

def mask_line(line, mask):
    return ''.join(char if mask_char != '?' else '?' for char, mask_char in zip(line, mask))

def process_patterns(patterns_in, masks=None, skip_lines=0):
    patterns = patterns_in.copy()
    print(f"Processing {len(patterns)} patterns")
    for pattern in patterns:
        lines = pattern.content.split('\n')
        processed_lines = []
        for i, line in enumerate(lines):
            for mask in masks:
                if skip_lines == 0:
                    line = mask_line(line, mask)
                    print(f"Masking    line {i} {line}")
                elif (i % skip_lines) == 0:
                    line = mask_line(line, mask)
                    print(f"Masking    line {i} {line}")                    
                else:
                    print(f"Processing line {i} {line}")

            processed_lines.append(line)
        pattern.processed_content = '\n'.join(processed_lines)
    return patterns

def save_patterns_to_json(patterns, file_path):
    patterns_data = [{
        'number': pattern.number,
        'density': pattern.density,
        'lines': pattern.lines,
        'uri': pattern.uri,
        'content': pattern.content,
        'processed_content': pattern.processed_content
    } for pattern in patterns]
    
    with open(file_path, 'w') as json_file:
        json.dump(patterns_data, json_file, indent=4)

def main(file_path):
    # Load and parse the file
    patterns = parse_file(file_path)

    # Compute and display statistics
    stats = compute_statistics(patterns)
    print("Statistics:")
    for key, value in stats.items():
        print(f"{key}: {value}")

    print(f"\nNumber of patterns: {len(patterns)}")

    # Example filtering usage
    #filtered_patterns = filter_patterns(patterns, min_density=20, max_density=50, min_lines=5, max_lines=10)
    filtered_patterns = filter_patterns(patterns, min_density=650, max_density=99999, min_lines=64, max_lines=64)
    print(f"\nNumber of filtered patterns: {len(filtered_patterns)}")

    # Example setting masks and skip_lines for specific patterns
    #iterate through filtered_patterns to apply masks and skip_lines
    # Process patterns
    masks = [
        '....|..|--- .... ....|--- .... ....|??? ???? ....',
        '....|..|??? ???? ....|--- .... ....|... .... ....',
        '....|..|--- .... ....|??? ???? ....|--- .... ....', 
        '????|..|--- .... ....|--- .... ....|--- .... ....'
    ]
    skip_lines = 2
    processed_patterns1 = process_patterns(filtered_patterns, masks[0:1], skip_lines)
    save_patterns_to_json(processed_patterns1, 'processed_patterns1.json')    
    processed_patterns2 = process_patterns(filtered_patterns, masks[1:2], skip_lines)
    save_patterns_to_json(processed_patterns2, 'processed_patterns2.json')    
    processed_patterns3 = process_patterns(filtered_patterns, masks[2:3], skip_lines)    
    save_patterns_to_json(processed_patterns3, 'processed_patterns3.json')    
    processed_patterns4 = process_patterns(filtered_patterns, masks[3:4], skip_lines)    
    save_patterns_to_json(processed_patterns4, 'processed_patterns4.json')    

    return
    # Display processed patterns
    for pattern in processed_patterns[0:1]:
        print('--' * 40)        
        print(f"Processed Pattern {pattern.number}:")
        print('\n')
        print(f"Original Content:\n{pattern.content}")
        print('\n')        
        print(f"Processed Content:\n{pattern.processed_content}\n")
   

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        file_path = "unique_patterns.txt"
        print(f"No file path provided. Using default: {file_path}")
    else:
        file_path = sys.argv[1]
    
    main(file_path)
