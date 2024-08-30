#!/usr/bin/env python3

import os
import anthropic
import re
from pathlib import Path
import tempfile
import shutil
import textwrap

# Initialize the Anthropic client
client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

def get_docstring(filename):
    """Extract the docstring from a Python file."""
    with open(filename, 'r') as file:
        content = file.read()
    match = re.search(r'"""(.*?)"""', content, re.DOTALL)
    if match:
        return match.group(1).strip()
    else:
        # If triple quotes not found, try single quotes
        match = re.search(r"'''(.*?)'''", content, re.DOTALL)
        return match.group(1).strip() if match else ""

def get_script_description(docstring):
    """Use Anthropic API to get a description of what the script does."""
    messages = [
        {
            "role": "user",
            "content": f"Based on this docstring, briefly describe what the script does in one sentence:\n\n{docstring}"
        }
    ]
    response = client.messages.create(
        model="claude-3-sonnet-20240229",
        max_tokens=100,
        temperature=0,
        messages=messages
    )
    return response.content[0].text.strip()

def update_readme_chunk(current_content, new_descriptions):
    """Update a chunk of the README.md file with new script descriptions."""
    messages = [
        {
            "role": "user",
            "content": f"""
            Given the current README.md content:

            {current_content}

            And the following new or updated script descriptions:

            {new_descriptions}

            Please provide an updated version of the README.md that incorporates these changes. Follow these guidelines:
            1. Maintain the overall structure and any existing sections not related to script descriptions.
            2. Ensure all scripts are listed, adding new ones and updating existing ones as necessary.
            3. Use the following format for script descriptions, with word wrapping at 80 characters:
               - **script_name.py**: Brief description of what the script does, wrapped at
                 80 characters and indented properly.
            4. Preserve any existing sections like "License" or "Contributing" if present.
            5. If not present, add a "License" section at the end with the MIT License.
            6. Ensure proper Markdown formatting throughout the document.
            """
        }
    ]
    response = client.messages.create(
        model="claude-3-sonnet-20240229",
        max_tokens=2000,
        temperature=0,
        messages=messages
    )
    return response.content[0].text.strip()

def main():
    script_dir = Path(__file__).parent.resolve()
    readme_path = script_dir / "README.md"
    
    # Create a temporary file
    with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp_file:
        temp_path = Path(temp_file.name)
        
        # Read current README.md content
        current_content = ""
        if readme_path.exists():
            with open(readme_path, 'r') as readme:
                current_content = readme.read()
        
        # Write initial content to temp file
        temp_file.write(current_content)

        # Process files in chunks
        chunk_size = 5
        all_files = [f for f in os.listdir(script_dir) if f.endswith('.py') and f != Path(__file__).name]
        
        for i in range(0, len(all_files), chunk_size):
            chunk = all_files[i:i+chunk_size]
            new_descriptions = {}
            
            for filename in chunk:
                full_path = script_dir / filename
                docstring = get_docstring(full_path)
                if docstring:
                    description = get_script_description(docstring)
                    new_descriptions[filename] = description
                else:
                    print(f"No docstring found for {filename}")
            
            # Update temp file with this chunk
            current_content = update_readme_chunk(current_content, new_descriptions)
            temp_file.seek(0)
            temp_file.write(current_content)
            temp_file.truncate()
            
            print(f"Processed files {i+1} to {min(i+chunk_size, len(all_files))}")

    # Replace the original README.md with the temp file
    shutil.move(temp_path, readme_path)
    print("README.md has been fully updated.")

if __name__ == "__main__":
    main()
