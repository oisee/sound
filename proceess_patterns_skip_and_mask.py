import re
import statistics
import json
import random

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
        content = match.group('content')
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

def apply_mask(content, mask, ml):
    lines = content.split('\n')
    masked_lines = []
    for i in range(len(lines)):
        if i % ml == 0:
            masked_lines.append(mask_line(lines[i], mask))
        else:
            masked_lines.append(lines[i])
    return '\n'.join(masked_lines)

def process_patterns(patterns_in, masks=None, sl=0, ml=1):
    patterns = patterns_in.copy()
    print(f"Processing {len(patterns)} patterns")
    for pattern in patterns:
        lines = pattern.content.split('\n')
        processed_lines = []
        for i in range(0, len(lines), sl + ml):
            chunk = lines[i:i+sl]
            processed_lines.extend(chunk)
            if i + sl < len(lines):
                chunk_to_mask = lines[i+sl:i+sl+ml]
                for line in chunk_to_mask:
                    masked_line = apply_mask(line, masks[0], ml)
                    processed_lines.append(masked_line)
        pattern.processed_content = '\n'.join(processed_lines)
    return patterns

def save_patterns_to_json(patterns, filename):
    with open(filename, 'w') as file:
        json.dump([pattern.__dict__ for pattern in patterns], file, indent=4)

def main(file_path, sl, ml):
    patterns = parse_file(file_path)
    statistics = compute_statistics(patterns)
    print("Statistics:", statistics)
    
    # Filtering patterns based on some example criteria
    filtered_patterns = filter_patterns(patterns, min_density=20, max_density=50, min_lines=5, max_lines=10)
    filtered_patterns = filter_patterns(patterns, min_density=850, max_density=99999, min_lines=64, max_lines=64)
    print(f"\nNumber of filtered patterns: {len(filtered_patterns)}")

    # Masks
    masks = [
        '....|..|--- .... ....|--- .... ....|??? ???? ....',
        '....|..|??? ???? ....|--- .... ....|... .... ....',
        '....|..|--- .... ....|??? ???? ....|--- .... ....',
        '????|..|--- .... ....|--- .... ....|--- .... ....'
    ]

    # Shuffle and distribute masks
    random.shuffle(filtered_patterns)
    total_patterns = len(filtered_patterns)
    mask_distribution = [
        (masks[0], int(0.30 * total_patterns)),
        (masks[1], int(0.30 * total_patterns)),
        (masks[2], int(0.30 * total_patterns)),
        (masks[3], total_patterns - int(0.90 * total_patterns))
    ]

    index = 0
    for mask, count in mask_distribution:
        to_process = filtered_patterns[index:index + count]
        index += count
        processed_patterns = process_patterns(to_process, [mask], sl=sl, ml=ml)
        save_patterns_to_json(processed_patterns, f'processed_patterns_{index}.json')

    return

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 4:
        file_path = "unique_patterns.txt"
        sl = 4  # default skip-lines
        ml = 4  # default mask-lines
        print(f"No file path provided. Using default: {file_path}, skip-lines: {sl}, mask-lines: {ml}")
    else:
        file_path = sys.argv[1]
        sl = int(sys.argv[2])
        ml = int(sys.argv[3])
    
    main(file_path, sl, ml)
