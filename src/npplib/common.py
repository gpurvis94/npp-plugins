from Npp import *

def print_debug(*args):
    """Prints each element of args to the console separated by a space.
    
    Args:
        args (*args): The objects to convert to string and print.
    """
    console.write(" ".join([str(elem) for elem in args] + ["\r\n"]))

    
def print_err(*args):
    """Prints each element of args to the console separated by a space.
    
    Args:
        args (*args): The objects to convert to string and print.
    """
    console.writeError(" ".join([str(elem) for elem in args] + ["\r\n"]))


def get_lines(line_nums):
    """Returns the contents of the specified line numbers.
    
    Args:
        line_nums (iter): An iterable series of integers which
            refer to the desired 0-indexed lines.
    
    Returns:
        A generator of strings holding the line contents.
    """
    return (editor.getLine(i) for i in line_nums)
