
# Recursive File Extraction by Format..
import os

# Recursively Extract File by Format
def search_files(directory='.', extension=''):
    extension = extension.lower()
    for dirpath, dirnames, files in os.walk(directory):
        for name in files:
            if extension and name.lower().endswith(extension):
                print(os.path.join(dirpath, name))
            elif not extension:
                print(os.path.join(dirpath, name))

# Arguments Directory and Format type
search_files("c:/",".txt")
