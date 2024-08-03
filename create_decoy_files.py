import os
import random

def create_decoy_files(directory, num_files):
    decoy_contents = [
        "Confidential: Do not distribute",
        "Top Secret: Eyes Only",
        "Internal Use Only: Proprietary Information"
    ]

    for i in range(num_files):
        filename = f"decoy_{i}.txt"
        filepath = os.path.join(directory, filename)
        
        with open(filepath, 'w') as f:
            f.write(random.choice(decoy_contents))
        
        print(f"Created decoy file: {filepath}")

if __name__ == "__main__":
    target_dir = input("Enter the directory to create decoy files in: ")
    num_files = int(input("Enter the number of decoy files to create: "))
    
    if os.path.exists(target_dir):
        create_decoy_files(target_dir, num_files)
    else:
        print("The specified directory does not exist.")
