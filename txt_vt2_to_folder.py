import os
import shutil
import hashlib

def hash_file_content(content):
    """Compute the hash of the file content."""
    hash_obj = hashlib.sha256()
    hash_obj.update(content.encode('utf-8'))
    return hash_obj.hexdigest()

def scan_and_copy_files(input_folder, output_folder):
    # Ensure the output folder exists
    os.makedirs(output_folder, exist_ok=True)
    
    # List to hold files that meet the criteria
    matching_files = []
    file_hashes = set()
    # Walk through the directory recursively
    for root, dirs, files in os.walk(input_folder):
        for file in files:
            file_lower = file.lower()
            if file_lower.endswith('.txt') or file_lower.endswith('.vt2'):
            # Construct full file path
                full_file_path = os.path.join(root, file)
                print(f"Processing: {full_file_path}")
            else:
                #full_file_path = os.path.join(root, file)
                #print(f"Skipping: {full_file_path}")
                continue
            try:
                # Try to open the file with UTF-8 encoding
                with open(full_file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except UnicodeDecodeError:
                # If UTF-8 fails, try ISO-8859-1
                with open(full_file_path, 'r', encoding='ISO-8859-1') as f:
                    content = f.read()            
            # Rest of your code...

            if '[Module]' in content:
                # Compute the hash of the file content
                file_hash = hash_file_content(content)
                
                # Check if this content hash is already seen
                if file_hash not in file_hashes:
                    file_hashes.add(file_hash)
                    matching_files.append(full_file_path)
                    print(f"\tFound a matching file: {full_file_path}")
                else:
                    print(f"\tDuplicate content: {full_file_path}")
            else:
                print(f"\tContent does not match: {full_file_path}")

            # if '[Module]' in content:
            #     matching_files.append(full_file_path)
            #     print(f"\tFound a matching file: {full_file_path}")

            # else:
            #     print(f"\tContent does not match: {full_file_path}")
    
    # Sort the matching files by name
    matching_files.sort(key=os.path.basename)

    print(f"Found {len(matching_files)} matching files")
    print(f"Copying files to {output_folder}")
    print(matching_files)

    # Copy and rename files with a 4-digit prefix
    for idx, file_path in enumerate(matching_files):
        prefix = f"{idx:04d}_"
        new_file_name = prefix + os.path.basename(file_path)
        shutil.copy(file_path, os.path.join(output_folder, new_file_name))

# Example usage:
input_folder = '/mnt/f/Users/alice/Dropbox/'
output_folder = './all_txt/'
scan_and_copy_files(input_folder, output_folder)
