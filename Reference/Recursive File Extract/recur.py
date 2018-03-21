
# Version 1.3 - Finished!

# Recursive File Scan
# Wayne Kenney (Pythogen) - 2016
# Extract all files on a drive of a specific format.

# Update (Refined): Now this script runs with two seperate operations:
# 1) Operation - Gathers all Directory/File details and includes them into an Array.
# 2) Feedback  - Displays Array Content with Loop revealing all Directory/Files Gathered.

# Operating System Interfaces Module (Required)
import os
# For delay (optional)
import time
# For Progress Bar (Optional)
from tqdm import tqdm

def rget(path):
    dirlist = os.listdir(path)
    dirlist.sort()
    return dirlist

# Recursive listing
def rscan(path, prefix = ""):
    # Directory List
    dirlist = rget(path)
    # Loop directories/files
    for f in tqdm(dirlist):
        # Print 'f' for File
        # Print 'path' for Directory

        # Text File format specified
        if f.find(".txt") != -1:
            # Append to Array for Final Output
            fDir.append(path + "/" + f + "\n")
            # Delay Results for Debug
            time.sleep(0.1)
            
        fullname = os.path.join(path, f)
        if os.path.isdir(fullname):
            rscan(fullname, prefix + "| ")

# Script Details (Output)
print ("\nThis script will scan your harddrive recursively.\n\n\n"

    "Application:\n"
    " - File Search/Scan \n"
    " - Mass-Data Injection \n"
    " - Overwrite/Modification \n")

# Array Declaration
fDir = []

# Prompt to Start. Press Enter to Begin the Scan (Output/Input)
x = raw_input("Press Enter to Start Scan...\n")

# Scan Started Feedback (Output)
print "Scan initialized...\n"

# Dir for Windows
forWindows = "C:\Users\Developer\Desktop"
# Dir for Linux (My Primary OS)
forLinux = "/home/developer/Desktop"

# Call Scan function for Linux
rscan(forLinux)

# Finally Display all Directory/Files Added to Array for Viewing (Output)
for fDirOut in fDir:
    print fDirOut

# Completion Feedback (Output)
print ("\nOperation Complete!\n\n"
        "Results: All extracted from your drive.\n")