import json
import random

def split_jsonl_file(input_file, train_file, test_file, train_ratio=0.8):
    with open(input_file, 'r') as file:
        lines = file.readlines()
    
    # Shuffle the lines to ensure random distribution
    random.shuffle(lines)
    
    # Calculate split index
    split_index = int(len(lines) * train_ratio)
    
    # Split lines into training and testing sets
    train_lines = lines[:split_index]
    test_lines = lines[split_index:]
    
    # Write training lines to train_file
    with open(train_file, 'w') as train_f:
        for line in train_lines:
            train_f.write(line)
    
    # Write testing lines to test_file
    with open(test_file, 'w') as test_f:
        for line in test_lines:
            test_f.write(line)

# Usage example
input_file = 'ds.jsonl'
train_file = 'train_ds.jsonl'
test_file = 'test_ds.jsonl'
split_jsonl_file(input_file, train_file, test_file)
