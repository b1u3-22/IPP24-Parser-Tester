"""
Skript na otestování funkčnosti parseru pro jazyk IPPcode24
@author: Jiří Sedlák
"""
import os
from subprocess import run, PIPE

import pytest

from xmldiff import formatting
from xmldiff import main as xmldiff

python = "python3"
parser_file = "../parse.py"

arg = f"{python} {parser_file}"

NO_ERROR = 0
ARG_ERROR = 10
HEADER_ERROR = 21
OPCODE_ERROR = 22
OTHER_ERROR = 23

formatter = formatting.DiffFormatter()


def compare_xml(expected, actual):
    edit_list = xmldiff.diff_files(expected, actual, formatter=formatter).split('\n')

    if len(edit_list) == 1 and edit_list[0] == '':
        return True

    for action in edit_list:
        if not ("update-text" in action and "null" in action):
            return False

    return True


def base(folder_name, return_code=NO_ERROR, compare=True, suffix=""):
    input_file_name = f"{folder_name}/{folder_name}{suffix}.src"
    output_file_name = f"{folder_name}/{folder_name}{suffix}.out"
    compare_file_name = f"{folder_name}/{folder_name}{suffix}.cmp"

    input_file = open(input_file_name, encoding="utf-8")
    output_file = open(output_file_name, "w", encoding="utf-8")

    parser = run(arg, stdin=input_file, stdout=output_file, stderr=PIPE, shell=True)
    output_file.close()

    if compare:
        output_file = open(output_file_name, "r", encoding="utf-8")
        compare_file = open(compare_file_name, "r", encoding="utf-8")
        assert compare_xml(compare_file_name, output_file_name), (f"XML tree generated from {input_file_name} "
                                                                  f"in {output_file_name} "
                                                                  f"does not match expected output "
                                                                  f"in {compare_file_name}")
        compare_file.close()

    assert parser.returncode == return_code, (f"Unexpected return code "
                                              f"(expected: {return_code}, output: {parser.returncode}) "
                                              f"when testing with file {input_file_name}")

    input_file.close()
    output_file.close()


def base_group(folder_name, number_of_tests, return_code=OTHER_ERROR, compare=False):
    for test in range(1, number_of_tests + 1):
        base(folder_name, return_code, compare=compare, suffix=f"_{test}")


def base_create_test_file(folder_name, source, suffix="", header=".IPPcode24\n"):
    source_file_name = f"{folder_name}/{folder_name}{suffix}.src"
    source_file = open(source_file_name, "w", encoding="utf-8")
    source_file.write(header)
    source_file.write(source)
    source_file.close()


# ----------------------------------------------------------------------------------------------------------------------

def test_encoding():
    base("encoding_test")


def test_escape_char():
    base("escape_char_test")


def test_comment():
    base("comment_test")


def test_invalid_int():
    base("invalid_int_test",
         compare=False,
         return_code=OTHER_ERROR
         )


def test_at_in_string():
    base("at_in_string_test")


def test_two_opcodes_on_one_line():
    base("two_opcodes_on_one_line_test",
         compare=False,
         return_code=OTHER_ERROR
         )


def test_one_opcode_on_two_lines():
    base("one_opcode_on_two_lines_test",
         compare=False,
         return_code=OTHER_ERROR
         )


def test_space():
    base("space_test")


@pytest.mark.parametrize("source", [("WRITE int@henlo", 1), ("WRITE int@*5", 2), ("WRITE int@true", 3)],
                         ids=lambda source: str(source[0]))
def test_valid_bool(source):
    folder_name = "invalid_int_test"
    suffix = f"_{source[1]}"
    base_create_test_file(folder_name, source[0], suffix=suffix)
    base(folder_name, compare=False, suffix=suffix, return_code=OTHER_ERROR)


@pytest.mark.parametrize("source", [("WRITE bool@1", 1), ("WRITE bool@0", 2), ("WRITE bool@bonjour", 3)],
                         ids=lambda source: str(source[0]))
def test_invalid_bool(source):
    folder_name = "invalid_bool_test"
    suffix = f"_{source[1]}"
    base_create_test_file(folder_name, source[0], suffix=suffix)
    base(folder_name, compare=False, suffix=suffix, return_code=OTHER_ERROR)


def test_invalid_arguments():
    parser = run(arg + " --invalid_arg", stdout=PIPE, stderr=PIPE, shell=True)
    assert parser.returncode == ARG_ERROR


def test_valid_arguments():
    parser = run(arg + " --help", stdout=PIPE, stderr=open(os.devnull, 'wb'), shell=True)
    assert len(parser.stdout) > 0
    assert parser.returncode == NO_ERROR


def test_invalid_help():
    parser = run(arg + " --help --help", stdout=PIPE, stderr=PIPE, shell=True)
    assert parser.returncode == ARG_ERROR


@pytest.mark.parametrize("source", [(".IPPcode2", 1), ("", 2)], ids=["Invalid header", "Missing header"])
def test_invalid_header(source):
    folder_name = "invalid_header_test"
    suffix = f"_{source[1]}"
    base_create_test_file(folder_name, source[0], suffix=suffix, header="")
    base(folder_name, compare=False, suffix=suffix, return_code=HEADER_ERROR)


def test_valid_header():
    base("valid_header_test")


def test_krivka_read():
    base("krivka_read_test")


def test_krivka_simple_tag():
    base("krivka_simple_tag_test")


def test_krivka_syntax_error():
    base("krivka_syntax_error",
         compare=False,
         return_code=OTHER_ERROR
         )


def test_krivka_write():
    base("krivka_write_test")


def test_krivka_string():
    base("krivka_string_test")


def test_invalid_keyword():
    base("invalid_keyword_test",
         compare=False,
         return_code=OPCODE_ERROR
         )


def test_opcode_as_label():
    base("opcode_as_label_test")


def test_valid_no_arg_keywords():
    base("valid_no_arg_keywords_test")


@pytest.mark.parametrize("source",
                         [("CREATEFRAME GF@a", 1), ("PUSHFRAME GF@b", 2), ("POPFRAME GF@c", 3), ("RETURN GF@d", 4),
                          ("BREAK GF@f", 5), ("CREATEFRAME int", 6), ("PUSHFRAME string@henlo", 7)],
                         ids=lambda source: str(source[0]))
def test_invalid_no_arg_keywords(source):
    folder_name = "invalid_no_arg_keywords_test"
    suffix = f"_{source[1]}"
    base_create_test_file(folder_name, source[0], suffix=suffix)
    base(folder_name, compare=False, suffix=suffix, return_code=OTHER_ERROR)


def test_valid_var_arg_keywords():
    base("valid_var_arg_keywords_test")


@pytest.mark.parametrize("source", [("DEFVAR", 1), ("DEFVAR int@6", 2), ("DEFVAR GF@a TF@b", 3),
                                    ("DEFVAR GF@a string@ahoj", 4), ("POPS", 5), ("POPS int@5", 6),
                                    ("POPS GF@a TF@b", 7), ("POPS GF@a bool@true", 8)],
                         ids=lambda source: str(source[0]))
def test_invalid_var_arg_keywords(source):
    folder_name = "invalid_var_arg_keywords_test"
    suffix = f"_{source[1]}"
    base_create_test_file(folder_name, source[0], suffix=suffix)
    base(folder_name, compare=False, suffix=suffix, return_code=OTHER_ERROR)


def test_valid_sym_arg_keywords():
    base("valid_sym_arg_keywords_test")


@pytest.mark.parametrize("source", [("PUSHS", 1), ("PUSHS int", 2), ("PUSHS GF@a int@5", 3),
                                    ("WRITE", 4), ("WRITE string", 5), ("WRITE string@henlo LF@a", 6),
                                    ("EXIT", 7), ("EXIT bool", 8), ("EXIT string@ahoj bool@true", 9)],
                         ids=lambda source: str(source[0]))
def test_invalid_sym_arg_keywords(source):
    folder_name = "invalid_sym_arg_keywords_test"
    suffix = f"_{source[1]}"
    base_create_test_file(folder_name, source[0], suffix=suffix)
    base(folder_name, compare=False, suffix=suffix, return_code=OTHER_ERROR)


def test_valid_label_arg_keywords():
    base("valid_label_arg_keywords_test")


@pytest.mark.parametrize("source", [("CALL", 1), ("CALL GF@a", 2), ("CALL string", 3), ("CALL string@bonjour", 4),
                                    ("LABEL", 5), ("LABEL TF@b", 6), ("LABEL int", 7), ("LABEL int@5", 8),
                                    ("JUMP", 9), ("JUMP bool", 10), ("JUMP bool@false", 11), ("JUMP LF@c", 10)],
                         ids=lambda source: str(source[0]))
def test_invalid_label_arg_keywords(source):
    folder_name = "invalid_label_arg_keywords_test"
    suffix = f"_{source[1]}"
    base_create_test_file(folder_name, source[0], suffix=suffix)
    base(folder_name, compare=False, suffix=suffix, return_code=OTHER_ERROR)


def test_valid_var_type_arg_keywords():
    base("valid_var_type_arg_keywords_test")


@pytest.mark.parametrize("source", [("READ", 1), ("READ GF@a", 2), ("READ TF@b string@ahoj", 3), ("READ LF@c LF@d", 4),
                                    ("READ LF@c bool LF@a", 5), ("READ int int", 6), ("READ GF@a GF@b", 7),
                                    ("READ bool TF@a", 8)],
                         ids=lambda source: str(source[0]))
def test_invalid_var_type_arg_keywords(source):
    folder_name = "invalid_var_type_arg_keywords_test"
    suffix = f"_{source[1]}"
    base_create_test_file(folder_name, source[0], suffix=suffix)
    base(folder_name, compare=False, suffix=suffix, return_code=OTHER_ERROR)


def test_valid_var_sym_sym_arg_keywords():
    base("valid_var_sym_sym_arg_keywords_test")


@pytest.mark.parametrize("source", [("ADD", 1), ("ADD TF@b", 2), ("ADD int@49", 3), ("ADD LF@a int@49", 4),
                                    ("ADD int@49 int@49 int@49", 5), ("ADD LF@d int@49 string@henlo LF@a", 6),
                                    ("ADD GF@e int bool@false", 7),

                                    ("SUB", 8), ("SUB TF@b", 9), ("SUB int@49", 10), ("SUB LF@a int@49", 11),
                                    ("SUB int@49 int@49 int@49", 12), ("SUB LF@d int@49 string@henlo LF@a", 13),
                                    ("SUB GF@e int bool@false", 14),

                                    ("MUL", 15), ("MUL TF@b", 16), ("MUL int@49", 17), ("MUL LF@a int@49", 18),
                                    ("MUL int@49 int@49 int@49", 19), ("MUL LF@d int@49 string@henlo LF@a", 20),
                                    ("MUL GF@e int bool@false", 21),

                                    ("IDIV", 22), ("IDIV TF@b", 23), ("IDIV int@49", 24), ("IDIV LF@a int@49", 25),
                                    ("IDIV int@49 int@49 int@49", 26), ("IDIV LF@d int@49 string@henlo LF@a", 27),
                                    ("IDIV GF@e int bool@false", 28),

                                    ("LT", 29), ("LT TF@b", 30), ("LT int@49", 31), ("LT LF@a int@49", 32),
                                    ("LT int@49 int@49 int@49", 33), ("LT LF@d int@49 string@henlo LF@a", 34),
                                    ("LT GF@e int bool@false", 35),

                                    ("GT", 36), ("GT TF@b", 37), ("GT int@49", 38), ("GT LF@a int@49", 39),
                                    ("GT int@49 int@49 int@49", 40), ("GT LF@d int@49 string@henlo LF@a", 41),
                                    ("GT GF@e int bool@false", 42),

                                    ("EQ", 43), ("EQ TF@b", 44), ("EQ int@49", 45), ("EQ LF@a int@49", 46),
                                    ("EQ int@49 int@49 int@49", 47), ("EQ LF@d int@49 string@henlo LF@a", 48),
                                    ("EQ GF@e int bool@false", 49),

                                    ("AND", 50), ("AND TF@b", 51), ("AND int@49", 52), ("AND LF@a int@49", 53),
                                    ("AND int@49 int@49 int@49", 54), ("AND LF@d int@49 string@henlo LF@a", 55),
                                    ("AND GF@e int bool@false", 56),

                                    ("OR", 57), ("OR TF@b", 58), ("OR int@49", 59), ("OR LF@a int@49", 60),
                                    ("OR int@49 int@49 int@49", 61), ("OR LF@d int@49 string@henlo LF@a", 62),
                                    ("OR GF@e int bool@false", 63),

                                    ("NOT", 64), ("NOT TF@b", 65), ("NOT int@49", 66), ("NOT LF@a int@49", 67),
                                    ("NOT int@49 int@49 int@49", 68), ("NOT LF@d int@49 string@henlo LF@a", 69),
                                    ("NOT GF@e int bool@false", 70),

                                    ("STRI2INT", 71), ("STRI2INT TF@b", 72), ("STRI2INT int@49", 73),
                                    ("STRI2INT LF@a int@49", 74),
                                    ("STRI2INT int@49 int@49 int@49", 75),
                                    ("STRI2INT LF@d int@49 string@henlo LF@a", 76),
                                    ("STRI2INT GF@e int bool@false", 77),

                                    ("CONCAT", 78), ("CONCAT TF@b", 79), ("CONCAT int@49", 80),
                                    ("CONCAT LF@a int@49", 81),
                                    ("CONCAT int@49 int@49 int@49", 82), ("CONCAT LF@d int@49 string@henlo LF@a", 83),
                                    ("CONCAT GF@e int bool@false", 84),

                                    ("GETCHAR", 85), ("GETCHAR TF@b", 86), ("GETCHAR int@49", 87),
                                    ("GETCHAR LF@a int@49", 88),
                                    ("GETCHAR int@49 int@49 int@49", 89), ("GETCHAR LF@d int@49 string@henlo LF@a", 90),
                                    ("GETCHAR GF@e int bool@false", 91),

                                    ("SETCHAR", 92), ("SETCHAR TF@b", 93), ("SETCHAR int@49", 94),
                                    ("SETCHAR LF@a int@49", 95),
                                    ("SETCHAR int@49 int@49 int@49", 96), ("SETCHAR LF@d int@49 string@henlo LF@a", 97),
                                    ("SETCHAR GF@e int bool@false", 98)
                                    ],
                         ids=lambda source: str(source[0]))
def test_invalid_var_sym_sym_sym_arg_keywords(source):
    folder_name = "invalid_var_sym_sym_arg_keywords_test"
    suffix = f"_{source[1]}"
    base_create_test_file(folder_name, source[0], suffix=suffix)
    base(folder_name, compare=False, suffix=suffix, return_code=OTHER_ERROR)


def test_valid_label_sym_sym_arg_keywords():
    base("valid_label_sym_sym_arg_keywords_test")


@pytest.mark.parametrize("source", [("JUMPIFEQ", 1), ("JUMPIFEQ label1", 2), ("JUMPIFEQ label1 TF@b", 3),
                                    ("JUMPIFEQ label1 TF@c GF@b LF@b", 4), ("JUMPIFEQ int TF@a GF@b", 5),
                                    ("JUMPIFEQ label2 int GF@b", 6), ("JUMPIFEQ label1 int@a bool", 7),
                                    ("JUMPIFEQ label1 TF@a wrong_label", 8),

                                    ("JUMPIFNEQ", 9), ("JUMPIFNEQ label1", 10), ("JUMPIFNEQ label1 TF@b", 11),
                                    ("JUMPIFNEQ label1 TF@c GF@b LF@b", 12), ("JUMPIFNEQ int TF@a GF@b", 13),
                                    ("JUMPIFNEQ label2 int GF@b", 14), ("JUMPIFNEQ label1 int@a bool", 15),
                                    ("JUMPIFNEQ label1 TF@a wrong_label", 16)
                                    ],
                         ids=lambda source: str(source[0]))
def test_invalid_label_sym_sym_arg_keywords(source):
    folder_name = "invalid_label_sym_sym_arg_keywords_test"
    suffix = f"_{source[1]}"
    base_create_test_file(folder_name, source[0], suffix=suffix)
    base(folder_name, compare=False, suffix=suffix, return_code=OTHER_ERROR)


def test_nil():
    base("nil_test")
