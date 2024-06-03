import re
import statistics

class Pattern:
    def __init__(self, number, density, lines, uri, content):
        self.number = number
        self.density = density
        self.lines = lines
        self.uri = uri
        self.content = content

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
        content = match.group('content').strip()
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
    filtered_patterns = filter_patterns(patterns, min_density=650, max_density=99999, min_lines=64, max_lines=64)
    print(f"\nNumber of filtered patterns: {len(filtered_patterns)}")

    # Placeholder for processing each pattern
    for pattern in patterns:
        # Process the pattern (actual logic to be implemented later)
        input_pattern = pattern.content
        processed_pattern = input_pattern  # Placeholder for actual processing logic
        #print(f"Processing Pattern {pattern.number}:")
        #print(f"Input Pattern:\n{input_pattern}")
        #print(f"Processed Pattern:\n{processed_pattern}\n")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        file_path = "unique_patterns.txt"
        #print("Usage: python script.py <path_to_file>")
    else:
        file_path = sys.argv[1]
    
    main(file_path)