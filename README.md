# Tests for parser of IPPcode24 language
## How to get it going
1. Clone this repository to the same directory as your `parse.py` script
2. Start the tests by running following command:
```
bash ./test.sh
```
> You mind need to install `python3.10-venv` package

## Test structure
Test files are separated into three different files:
1. `.src` file, which contains the source IPPcode24 code
2. `.out` file that contains the output from your `parse.py` script
3. `.cmp` file with hopefully the correct output, against which your output is compared

I do not guarantee the accuracy, correctness or completeness of these tests