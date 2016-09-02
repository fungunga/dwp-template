#!/usr/bin/env python3

from subprocess import run
from readchar import readkey
import sys
import os


def yn(*prompt, default=True):
    """
    Prompts the user to answer a yes/no question.

    Args:
        *prompt: List of arguments that form a prompt. Passed on to `print`.
        default (bool): Yes or no when the user hits enter?

    Returns:
        (bool) The user's choice.

    Raises:
        `KeyboardInterrupt` when the user has pressed Ctrl+C
    """
    if default:
        options = " [Y/n]? "
    else:
        options = " [y/N]? "

    accept = "yYjJ"
    reject = "nN\x1b\x07"          # Esc, ^G
    default_keys = " \r"           # Space, Return

    print(*prompt, end=options, flush=True)
    while True:
        key = readkey()[0]

        if key in accept or default and key in default_keys:
            print(accept[0])
            return True
        elif key in reject or not default and key in default_keys:
            print(reject[0])
            return False
        elif key == "\x03": # ^C
            raise KeyboardInterrupt()
        else:
            print(key, "\x08", sep="", end="", flush=True)


def run_pandoc(filename, args):
    """
    Runs pandoc with appropriate arguments.

    Args:
        filename (str): The input file to run pandoc on
        args: Iterable with additional arguments to pass to pandoc.

    Returns:
        (int) pandoc's exit code
    """
    args = ["pandoc"] + args
    argnames = [arg.split('=')[0] for arg in args]
    basename, extension = os.path.splitext(filename)
    pdfname = basename + '.pdf'

    if "-o" not in argnames:
        args.extend(["-o", pdfname])
    if "--latex-engine" not in argnames:
        args.append("--latex-engine=lualatex")
    if "--template" not in argnames:
        args.append("--template=DWP")
    args.append(filename)

    print(" ".join(args))
    result = run(args)
    return result.returncode


def main(argv):
    if argv is None:
        argv = []
    if len(argv) < 2:
        print("Usage: {} filename".format(argv[0]))
        sys.exit(1)

    filename = argv[-1]
    basename, extension = os.path.splitext(filename)
    if extension == "":
        filename = filename + ".md"
        extension = ".md"

    if os.path.exists(filename):
        if run_pandoc(filename, argv[1:-1]) == 0:
            if yn("Show PDF?"):
                run(["xdg-open", basename + ".pdf"])
        elif yn("Generate .tex for debugging?"):
            run_pandoc(filename, ["-o", basename + ".tex"] + argv[1:-1])


if __name__ == "__main__":
    main(sys.argv)
