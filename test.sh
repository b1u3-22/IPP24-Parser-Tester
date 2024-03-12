#!/bin/sh

# Check for existence of python venv
# If it doesn't exist, then create it
if ! test -d ./venv; then
  python -m venv ./venv
  . ./venv/bin/activate
  pip3 install -r ./requirements.txt
  deactivate
fi

# Check for existence of parse.py script
if ! test -f ../parse.py; then
  echo "Could not find the parse.py script. Exiting."
  exit 1
fi

.  ./venv/bin/activate        # Activate python venv
clear                         # Clear terminal
pytest ./ipp_parser_tests.py  # Start tests
deactivate                    # Deactivate python venv