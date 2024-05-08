import os
import re
import json

# Function to extract component information
def extract_component_info(component_list_file, project_root, install_dir):
    component_info = {}
    errors = []

    # Read component list from text file
    with open(component_list_file, 'r') as file:
        components = file.read().splitlines()

    so_pattern = re.compile(r'libamplxe_(\w+)_\d+\.\d+\.so')

    # Iterate over each component and search for profraw and so files
    for component in components:
        profraw_path = None
        so_file_path = None

        # Search for profraw file
        for root, dirs, files in os.walk(project_root):
            for directory in dirs:
                if component in directory:
                    profraw_path = os.path.join(root, directory, 'default.profraw')
                    break
            if profraw_path:
                break

        # Search for so file
        so_dir = os.path.join(install_dir, 'lib64')
        if os.path.exists(so_dir):
            for file in os.listdir(so_dir):
                if component in file:
                #match = so_pattern.match(file)
                #if match and match.group(1) == component:
                    so_file_path = os.path.join(so_dir, file)
                    break

        # Append component info to dictionary or errors list
        if profraw_path or so_file_path:
            component_info[component] = {'profraw_path': profraw_path, 'so_file_path': so_file_path}
        else:
            errors.append(component)

    return component_info, errors

# Define paths and file names
component_list_file = 'component_list.txt'
root_path = "/home/sdp/workspace/anurag/fresh_attempt/applications.analyzers.vtune"
project_root = f'{root_path}/unit_tests/posix-x86_64'
install_dir = f'{root_path}/install'

# Extract component information
component_info, errors = extract_component_info(component_list_file, project_root, install_dir)

# Write component information to JSON file
with open('component_info.json', 'w') as json_file:
    json.dump(component_info, json_file, indent=4)

# Write errors to errors file
with open('errors.txt', 'w') as errors_file:
    errors_file.write('\n'.join(errors))

