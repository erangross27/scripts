#!/usr/bin/env python3

"""
This script processes Python files in a directory, extracts their docstrings,
generates brief descriptions using the Anthropic API, and updates a README.md
file with these descriptions. It also manages a PostgreSQL database to track
processed files and avoid unnecessary reprocessing. The script ensures proper
setup of the database and handles the creation of necessary tables. It also
checks for and includes license information in the README.md file.

Key features:
- Processes Python files in the script's directory
- Extracts docstrings from Python files
- Uses Anthropic API to generate brief descriptions of scripts
- Updates README.md with script descriptions and license information
- Manages a PostgreSQL database to track processed files
- Handles database and user creation if they don't exist
- Calculates file hashes to detect changes

Dependencies:
- anthropic
- psycopg2
- hashlib
- subprocess

Environment variables:
- ANTHROPIC_API_KEY: API key for Anthropic
- DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT: Database connection parameters

Usage:
Run the script directly to process files and update the README.md.
"""
import os
import anthropic
import re
from pathlib import Path
import psycopg2
from psycopg2 import sql
import hashlib
import subprocess
from datetime import datetime

# Initialize the Anthropic client
client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

# Database connection parameters
DB_NAME = os.environ.get('DB_NAME', 'scripts_db')
DB_USER = os.environ.get('DB_USER', 'scripts_user')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'scripts_password')
DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_PORT = os.environ.get('DB_PORT', '5432')

def create_db_and_user():
    """
    Create the database and user if they don't exist.
    Also creates the 'processed_files' table in the database.
    """
    try:
        # Check if user exists
        user_exists = subprocess.run(['sudo', '-u', 'postgres', 'psql', '-tAc', 
                                      f"SELECT 1 FROM pg_roles WHERE rolname='{DB_USER}'"],
                                     capture_output=True, text=True).stdout.strip() == '1'
        if not user_exists:
            subprocess.run(['sudo', '-u', 'postgres', 'psql', '-c', 
                            f"CREATE USER {DB_USER} WITH PASSWORD '{DB_PASSWORD}';"],
                           check=True)
            print(f"Created user: {DB_USER}")
        else:
            print(f"User {DB_USER} already exists")

        # Check if database exists
        db_exists = subprocess.run(['sudo', '-u', 'postgres', 'psql', '-tAc', 
                                    f"SELECT 1 FROM pg_database WHERE datname='{DB_NAME}'"],
                                   capture_output=True, text=True).stdout.strip() == '1'
        if not db_exists:
            subprocess.run(['sudo', '-u', 'postgres', 'psql', '-c', 
                            f"CREATE DATABASE {DB_NAME} OWNER {DB_USER};"],
                           check=True)
            print(f"Created database: {DB_NAME}")
        else:
            print(f"Database {DB_NAME} already exists")

        # Connect to the database as the user to create the table
        conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT)
        cur = conn.cursor()
        cur.execute("""
        CREATE TABLE IF NOT EXISTS processed_files (
            filename TEXT PRIMARY KEY,
            last_modified TIMESTAMP,
            file_hash TEXT
        )
        """)
        conn.commit()
        cur.close()
        conn.close()
    except subprocess.CalledProcessError as e:
        print(f"Error executing PostgreSQL command: {e}")
        return False
    except psycopg2.Error as e:
        print(f"Error connecting to PostgreSQL: {e}")
        return False
    return True

def get_db_connection():
    """
    Establish and return a connection to the database.
    """
    return psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT)

def ensure_db_setup():
    """
    Ensure the database, user, and necessary tables are set up.
    """
    if create_db_and_user():
        print("Database setup confirmed.")
        return True
    else:
        print("Failed to set up the database. Exiting.")
        return False

def get_file_hash(filepath):
    """
    Calculate and return the MD5 hash of a file.
    """
    with open(filepath, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()

def is_file_processed(filename, last_modified, file_hash):
    """
    Check if a file has already been processed by comparing its last modified time and hash.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT last_modified, file_hash FROM processed_files WHERE filename = %s", (filename,))
    result = cur.fetchone()
    cur.close()
    conn.close()

    if result:
        db_last_modified, db_file_hash = result
        # Compare timestamps within a small tolerance (e.g., 1 second)
        time_difference = abs(db_last_modified.timestamp() - last_modified)
        return time_difference < 1 and db_file_hash == file_hash
    return False

def update_processed_file(filename, last_modified, file_hash):
    """
    Update or insert a record for a processed file in the database.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
    INSERT INTO processed_files (filename, last_modified, file_hash)
    VALUES (%s, %s, %s)
    ON CONFLICT (filename) DO UPDATE
    SET last_modified = EXCLUDED.last_modified, file_hash = EXCLUDED.file_hash
    """, (filename, datetime.fromtimestamp(last_modified), file_hash))
    conn.commit()
    cur.close()
    conn.close()


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

def get_license_filename(script_dir):
    """Find the correct license filename in the directory."""
    license_variants = ['LICENSE', 'LICENSE.md', 'License.md', 'license.md']
    for variant in license_variants:
        if os.path.exists(os.path.join(script_dir, variant)):
            return variant
    return None

def update_readme_content(current_content, script_name, script_description, license_filename):
    """Update the README.md content for a single script and ensure license section exists."""
    license_link = f"[{license_filename}]({license_filename})" if license_filename else "LICENSE file (not found)"
    
    messages = [
        {
            "role": "user",
            "content": f"""
Given the current README.md content:
{current_content}

Update or add the description for the script "{script_name}" with the following description:
{script_description}

Please follow these guidelines:
1. Maintain the overall structure and any existing sections not related to script descriptions.
2. Use the following format for the script description, with word wrapping at 80 characters:
   **`{script_name}`**: {script_description}
   (wrapped at 80 characters and indented properly)
3. If the script already exists in the README, update its description. If it's new, add it to the appropriate section.
4. Preserve any existing sections like "License" or "Contributing" if present.
5. If a "License" section is not present, add it at the end with the following content:

## License

This project is licensed under the MIT License - see the {license_link} for details.

6. If a "License" section is already present, ensure it uses the correct license filename: {license_filename}
7. Ensure proper Markdown formatting throughout the document.
Return the entire updated README content.
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
    """
    Main function to process Python files and update the README.md.
    """
    if not ensure_db_setup():
        exit(1)

    script_dir = Path(__file__).parent.resolve()
    readme_path = script_dir / "README.md"
    license_filename = get_license_filename(script_dir)

    # Read current README.md content
    current_content = ""
    if readme_path.exists():
        with open(readme_path, 'r') as readme:
            current_content = readme.read()

    # Process files individually
    all_files = [f for f in os.listdir(script_dir) if f.endswith('.py')]
    for i, filename in enumerate(all_files, 1):
        full_path = script_dir / filename
        last_modified = os.path.getmtime(full_path)
        file_hash = get_file_hash(full_path)

        if not is_file_processed(filename, last_modified, file_hash):
            docstring = get_docstring(full_path)
            if docstring:
                description = get_script_description(docstring)
                current_content = update_readme_content(current_content, filename, description, license_filename)
                update_processed_file(filename, last_modified, file_hash)
                print(f"Processed file {i} of {len(all_files)}: {filename}")
            else:
                print(f"No docstring found for {filename}")
        else:
            print(f"Skipped file {i} of {len(all_files)}: {filename} (no changes)")

    # Write the updated content to README.md
    with open(readme_path, 'w') as readme:
        readme.write(current_content)

    print("README.md has been fully updated.")

    if not license_filename:
        print("Warning: No LICENSE file found in the project directory.")

if __name__ == "__main__":
    main()
