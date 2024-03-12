# Tests for parser of IPPcode24 language
## How to get it going
### Required packaged
1. pytest >= 8.1.1
2. xmldiff >= 2.6.3
### Placement
Unzip the `tests.zip` file and place the `tests` dir into
the same one as your `parse.py` script
### Running
1. Ender the dir `tests`. 
2. Start the tests by running following command:
```
pytest ipp_parser_tests.py
```

## Test structure
Test files are separated into three different files:
1. `.src` file, which contains the source IPPcode24 code
2. `.out` file that contains the output from your `parse.py` script
3. `.cmp` file with hopefully the correct output, against which your output is compared

I do not guarantee the accuracy, correctness or completeness of these tests