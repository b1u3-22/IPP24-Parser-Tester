#!/bin/sh

tests_location="./IPP24-Parser-Tester"

# Check for existence of python venv
# If it doesn't exist, then create it
if ! test -d "${tests_location}/venv"; then
  echo "Creating Python virtual environment"
  python3 -m venv "${tests_location}/venv"
  . "${tests_location}/venv/bin/activate"
  echo "Installing required packages"
  pip3 install -r "${tests_location}/requirements.txt"
  deactivate
fi

# Check for existence of parse.py script
if ! test -f ./parse.py; then
  echo "Could not find the parse.py script. Exiting."
  exit 1
fi

.  "${tests_location}/venv/bin/activate" # Activate python venv
clear
cd "${tests_location}" || echo "Could not enter test directory" || exit 1 # Enter directory with tests
pytest "./ipp_parser_tests.py"  # Start tests
deactivate # Deactivate python venv
