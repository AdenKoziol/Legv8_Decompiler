#!/bin/bash

# Check if the disassembler.py file exists
if [ ! -f "Disassembler.py" ]; then
    echo "Error: disassembler.py not found. Ensure it is in the same directory as this script."
    exit 1
fi

# Check if a file name was provided
if [ "$#" -ne 1 ]; then
    echo "Usage: ./run.sh <binary_file>"
    exit 1
fi

# Run the Python script with the provided file
python3 Disassembler.py "$1"
