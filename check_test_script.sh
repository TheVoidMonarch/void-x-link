#!/bin/bash
# Script to check the test1.sh file

echo "Checking test1.sh file content:"
cat -A test1.sh

echo -e "\nChecking file encoding:"
file test1.sh

echo -e "\nChecking file permissions:"
ls -la test1.sh