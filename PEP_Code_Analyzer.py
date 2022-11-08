"""The functionality for open files with Python code and checking in accordance PEP8."""
import string
import os
import sys
import re
import ast


class PEP8AstVisitor(ast.NodeVisitor):
    """The visit of the Code object and check class, function, function arguments and variables names in accordance
    with PEP8."""

    def __init__(self, path):
        self.path = path

    def visit_ClassDef(self, node):
        """Check definition of class name in accordance with PEP8"""
        if not re.match(r"[\WA-Z]", node.name):
            print(f"{self.path}: Line {node.lineno}: S008 Class name '{node.name}' should use CamelCase")
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        """Check definition of 'Function name', 'argument name' in accordance with PEP8
        """
        if not re.match(r"[^A-Z].*", node.name):
            print(f"{self.path}: Line {node.lineno}: S009 Function name '{node.name}' should use snake_case")
        for argument_name in [a.arg for a in node.args.args]:
            if re.match(r'^[A-Z]', argument_name):
                print(f"{self.path}: Line {node.lineno}: S010 Argument name {argument_name} "
                      f"should be written in snake_case")
        for arguments in node.args.defaults:
            if isinstance(arguments, ast.List):
                print(f"{self.path}: Line {node.lineno}: S012 Default argument value is mutable")
        self.generic_visit(node)

    def visit_Name(self, node):
        """Check definition of 'Variable' in accordance with PEP8"""
        if isinstance(node, ast.Name):
            if isinstance(node.ctx, ast.Store):
                if re.match(r'^[A-Z]', node.id):
                    print(f"{self.path}: Line {node.lineno}: S011 Variable {node.id} should be snake_case")
        self.generic_visit(node)


class CodeLines:
    """The creation of the Code object and the related functionality."""

    def __init__(self, path, code):
        """
        The initializer for class

        Arguments:\n
        path -- a string representing the path to file.\n
        line_num -- an integer representing number of code line.\n
        code -- a string with code imported from file.\n
        code_list -- a list of code split by newline character '\\n'.\n
        code_line -- a string representing the code line.\n
        check_set -- a set representing set of symbols in code line.\n
        blank_lines -- an integer representing the blank lines number before present line."""
        self.path = path
        self.line_num = 1
        self.code = code
        self.code_list = code.splitlines()
        self.code_line = ""
        self.check_set = set()
        self.blank_lines = 0

    def whitespace_check(self, start_index=0):
        """Return whitespaces number of indentation or before inline comment.

        When start_index=0 count and return number of whitespaces in indentation of code line.\n
        When start_index non-zero count and return number of whitespaces before inline comment."""
        whitespace_count = 0
        if start_index != 0:
            for symbol_index in range(start_index - 1, -len(self.code_line), -1):
                if self.code_line[symbol_index] in string.whitespace:
                    whitespace_count += 1
                else:
                    break
        else:
            for i in self.code_line:
                if i in string.whitespace:
                    whitespace_count += 1
                else:
                    break
        return whitespace_count

    def symbol_membership(self, symbol: "; or todo"):
        """Check the position of ; or todo relative to #"""
        comment_hash_index = self.code_line.index("#")
        if symbol == ";":
            line_without_comment = self.code_line[:comment_hash_index].rstrip()
            if line_without_comment.endswith(symbol):
                return True
        elif symbol == "todo":
            lower_case_slice = self.code_line[comment_hash_index:].lower()
            if symbol in lower_case_slice:
                return True

    def length_check(self):
        """Check the length of a string for compliance with PEP8."""
        required_length = 79
        if len(self.code_line) > required_length:
            print(f"{self.path}: Line {self.line_num}: S001 is contrary to the requirements of PEP8")

    def indentation_check(self):
        """Check indentation rule of PEP8 in passed code line."""
        required_indentation = 4
        if self.code_line[0] in string.whitespace:
            if self.whitespace_check() % required_indentation != 0:
                print(f"{self.path}: Line {self.line_num}: S002 Indentation is not a multiple of four")

    def semicolon_check(self):
        """Check position of semicolon symbol in code line."""
        if ";" in self.check_set:
            if "#" in self.check_set:
                if self.symbol_membership(";"):
                    print(f"{self.path}: Line {self.line_num}: S003 Unnecessary semicolon")
            elif self.code_line.endswith(";"):
                print(f"{self.path}: Line {self.line_num}: S003 Unnecessary semicolon")

    def comment_check(self):
        """Check spaces before inline comments in accordance PEP8."""
        if "#" in self.check_set:
            if self.code_line.startswith("#"):
                pass
            else:
                comment_hash_index = self.code_line.index("#")
                if self.whitespace_check(comment_hash_index) != 2:
                    print(f"{self.path}: Line {self.line_num}: S004 Less than two spaces before inline comments")

    def todo_check(self):
        if "todo" in self.code_line.lower():
            if "#" in self.check_set:
                if self.symbol_membership("todo"):
                    print(f"{self.path}: Line {self.line_num}: S005 TODO found")

    def blank_lines_error(self):
        """Check quantity of blank lines before present line."""
        if self.blank_lines > 2:
            print(f"{self.path}: Line {self.line_num}: S006 More than two blank lines used before this line")

    def spaces_after_class_def(self, mode):
        """Check whitespaces after 'class' or 'def' declaring"""
        if not re.match(r".*?(class|def)\s\w+?", self.code_line):
            print(f"{self.path}: Line {self.line_num}: S007 Too many spaces after '{mode}'")

    def spaces_after_class_def_name(self, mode):
        """Check whitespaces after 'class' or 'def' name"""
        if "(" in self.check_set:
            open_bracket_index = self.code_line.index("(")
            if self.code_line[open_bracket_index - 1] in string.whitespace:
                print(f"{self.path}: Line {self.line_num}: S013 Too many spaces after {mode} name")
        elif ":" in self.check_set:
            colons_index = self.code_line.index(":")
            if self.code_line[colons_index - 1] in string.whitespace:
                print(f"{self.path}: Line {self.line_num}: S007 Too many spaces after {mode} name")

    def class_def_check(self):
        """Check code line with classes or functions declaring"""
        if "class" in self.code_line:
            self.spaces_after_class_def("class")
            self.spaces_after_class_def_name("class")
        if "def" in self.code_line:
            self.spaces_after_class_def("def")
            self.spaces_after_class_def_name("def")

    def code_check(self: 'file line to check') -> 'messages with error for line if were found inconsistencies to PEP8':
        """Check code line in accordance PEP8.

        Return error message if inconsistencies are found in the format:
        Path to file: Line number: Error code message."""
        self.length_check()
        self.indentation_check()
        self.semicolon_check()
        self.comment_check()
        self.todo_check()
        self.blank_lines_error()
        self.class_def_check()

    def file_check(self):
        for line in self.code_list:
            if len(line) == 0:
                self.blank_lines += 1
            else:
                self.code_line = line
                self.check_set = set(line)
                self.code_check()
                self.blank_lines = 0
            self.line_num += 1
        tree = ast.parse(self.code)
        PEP8AstVisitor(self.path).visit(tree)


def file_open(path: 'path to checked filed') -> "messages with error for file if were found inconsistencies to PEP8":
    """Open file with given path and check it line by line."""
    with open(path, "r") as check_file:
        code = check_file.read()
        check_code = CodeLines(path, code)
        check_code.file_check()


def main():
    args = sys.argv
    if os.path.isdir(args[1]):
        files = os.listdir(sys.argv[1])
        files.sort()
        for file_name in files:
            if file_name.endswith(".py"):
                file_open(os.path.join(args[1], file_name))
    else:
        file_open(args[1])


if __name__ == "__main__":
    main()
