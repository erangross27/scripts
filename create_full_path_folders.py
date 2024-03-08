import os

def create_folders(folder_paths):
  for folder_path in folder_paths:
    if not os.path.exists(folder_path):
      os.makedirs(folder_path, exist_ok=True)

if __name__ == "__main__":
  folder_paths = ["c:\administrator\CommonGen\checkpoints", "c:\administrator\CommonGen\models"]
  create_folders(folder_paths)
