import json
import os

def load_json_files(folder_path):
    json_files = [f for f in os.listdir(folder_path) if f.endswith('.json')]
    patterns = []
    for file in json_files:
        if file.endswith('.json'):
            with open(os.path.join(folder_path, file), 'r') as f:
                patterns.extend(json.load(f))
    return patterns

def convert_to_gpt_format(patterns):
    gpt_data = []
    for pattern in patterns:
        gpt_entry = {
            "messages": [
                {
                    "role": "system",
                    "content": f"You are the best ZX Spectrum Tracker Musician, you are helping the user.\nUser is editing this music pattern in VortexTracker:\n\n{pattern['processed_content']}\n\n"
                },
                {
                    "role": "user",
                    "content": f"Please fill the gaps marked as ???? with the actual notes and parameters.\n\n"
                },
                {
                    "role": "assistant",
                    "content": f"\n\n{pattern['content']}\n\n"
                }                
            ]
        }
        gpt_data.append(gpt_entry)
    return gpt_data

def save_gpt_data(gpt_data, output_file):
    with open(output_file, 'w') as f:
        for entry in gpt_data:
            json.dump(entry, f)
            f.write('\n')

def main(folder_path, output_file):
    patterns = load_json_files(folder_path)
    gpt_data = convert_to_gpt_format(patterns)
    save_gpt_data(gpt_data, output_file)

if __name__ == "__main__":
    folder_path = "./"  # Path to the folder containing JSON files
    output_file = "ds.jsonl"  # Output file in JSONL format
    main(folder_path, output_file)
