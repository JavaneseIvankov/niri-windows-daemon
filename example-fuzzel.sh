#!/bin/bash

# Read the file content
FILE_PATH="/tmp/niri_windows_entries.txt"

# Extract the id from the formatted string using fuzzel
id=$(fuzzel -d < "$FILE_PATH" | awk -F '::' '{print $1}')

# Execute the command
niri msg action focus-window --id "$id"
