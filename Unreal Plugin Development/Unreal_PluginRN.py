import os
import json
import fileinput
import shutil

# Define old and new plugin names
old_plugin_name = "GPT2_Conv_AI_Plugin_UE"
new_plugin_name = "GPTNPC"

# Define project directory and plugin directory
project_dir = "E:/ai_integration2/MyProject8"
plugin_dir = os.path.join(project_dir, "Plugins", old_plugin_name)

# Rename the plugin folder
os.rename(plugin_dir, os.path.join(project_dir, "Plugins", new_plugin_name))

# Update plugin directory
plugin_dir = os.path.join(project_dir, "Plugins", new_plugin_name)

# Rename and edit .uplugin file
with open(os.path.join(plugin_dir, f"{old_plugin_name}.uplugin"), 'r+') as f:
    data = json.load(f)
    data['FriendlyName'] = new_plugin_name
    data['Name'] = new_plugin_name
    f.seek(0)
    json.dump(data, f, indent=4)
    f.truncate()

os.rename(os.path.join(plugin_dir, f"{old_plugin_name}.uplugin"), 
          os.path.join(plugin_dir, f"{new_plugin_name}.uplugin"))

# Rename source directory and .cs files
shutil.move(os.path.join(plugin_dir, "Source", old_plugin_name), 
            os.path.join(plugin_dir, "Source", new_plugin_name))

for dirpath, dirnames, filenames in os.walk(os.path.join(plugin_dir, "Source", new_plugin_name)):
    for filename in filenames:
        if old_plugin_name in filename:
            os.rename(os.path.join(dirpath, filename), 
                      os.path.join(dirpath, filename.replace(old_plugin_name, new_plugin_name)))

# Replace all occurrences of old plugin name with new plugin name in .cs files
for dirpath, dirnames, filenames in os.walk(os.path.join(plugin_dir, "Source", new_plugin_name)):
    for filename in filenames:
        if filename.endswith('.cs'):
            with fileinput.FileInput(os.path.join(dirpath, filename), inplace=True) as file:
                for line in file:
                    print(line.replace(old_plugin_name, new_plugin_name), end='')

# Remove Intermediate directory
shutil.rmtree(os.path.join(project_dir, "Intermediate"), ignore_errors=True)
