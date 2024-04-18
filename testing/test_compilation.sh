#!/bin/bash

# Define the filename of the text file containing the list of components
components_file="components.txt"

# Define the filename to store the status of each component
status_file="component_status.txt"

# Clear the status file before starting
> "$status_file"

# Read the text file line by line and process each component
while IFS= read -r component_name; do
    # Execute the command for the current component
    echo "Running command for $component_name..."

    scons run_utest::$component_name:: codecov=True --build-config=release

    # Capture the exit status of the command
    exit_status=$?

    # Determine the status message based on the exit status
    if [ $exit_status -eq 0 ]; then
        status_message="PASS"
    else
        status_message="FAIL"
    fi

    # Print the status message for the current component
    echo "$component_name = $exit_status meaning ($status_message)"

    # Store the status of the current component in the status file
    echo "$component_name,$exit_status" >> "$status_file"

done < "$components_file"