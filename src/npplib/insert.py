"""A module for use with the python script notepad++ plugin.

Contains functionality for binding reformatting and inserting text based
upon current line attributes. Suggested usage is to bind the
on_CHARADDED_insert function to the SCINTILLANOTIFICATION.CHARADDED
notification. This function tests conditions for suitability each time a
key is pressed in the editor. If conditions pass, the functions
_on_CHARADDED_wrap and _on_RETURN_insert_comment fire, which
automatically format comments and docstrings under certain conditions.

Attributes:
    _lang_map (dict): A mapping of file extensions to syntax formats.
"""

from os.path import splitext
from Npp import *

from npplib.common import print_debug
from npplib.common import get_lines


_lang_map = {
    ".py": {
        "file_extension": '.py',
        "comment_str": '#',
        "style_comment": 1,
        "comment_limit": 72,
        
        "style_docstring": 7,
        "docstring_limit": 72,
        "docstring_str": "",
        },
    ".c": {
        "file_extension": '.c',
        "comment_str": '//',
        "style_comment": 2,
        "comment_limit": 72,
        },
    }


def on_CHARADDED_insert(args):
    """Auto-reformats the active file upon keypresses.
    
    The _lang_map dictionary contains the file extensions which the
    following on_chaaradded_insert methods support. If the key press is
    enter, language specific comment syntax is automatically added to
    the next line. This only happens if the previous two lines are
    comments. If any other character is added, the line is automatically
    wrapped based upon a defined line length limit.
    
    Args:
        args (dict): A mapping to scintella arguments. The key "ch"
            contains an integer representation of the character added to
            to the editor.
    """
    # Return if the file is not a supported language type.
    file_extension = splitext(notepad.getCurrentFilename())[1].lower()
    if not file_extension in (v for v in _lang_map):
        return
    
    # If key pressed is enter, continue comment (/r,/n) == (13,10).
    if args["ch"] == 10:
        _on_RETURN_insert_comment(_lang_map[file_extension])
        return
    
    if file_extension == '.py':
        _on_CHARADDED_wrap(_lang_map['.py'], args["ch"], type="docstring")
        _on_CHARADDED_wrap(_lang_map['.py'], args["ch"], type="comment")
    elif file_extension == '.c':
        _on_CHARADDED_wrap(_lang_map['.c'], args["ch"], type="comment")


def _on_CHARADDED_wrap(l_map, ch, type):
    """Hard-wraps a line if it exceeds a defined maximum line length.
    
    Supported wrap environments are comments and python docstrings. The
    line will only wrap if text is being appended to a line. The only
    exception to this is if spacebar as being pressed mid-sentence. This
    is so that users can edit words without wrapping occuring.
    
    Args:
        l_map (dict): The file's relevant language mapping.
        type (str): A string representing the wrapping format being
            attempted. Used to define unique behaviour for said type.
    """
    pos = editor.getCurrentPos()
    line_num = editor.lineFromPosition(pos)
    line = editor.getLine(line_num)
    
    # A test line that should eventually print end of line end of line 
    # Return if not end of line or spacebar
    if pos != editor.getLineEndPosition(line_num) and ch != 32:
        return
    
    # Set context specific variables
    if type == "docstring":
        # Return if style at current position isn't docstring
        if editor.getStyleAt(pos) != l_map["style_docstring"]:
            return
        
        line_len_limit = l_map["docstring_limit"]
        str_start = l_map["docstring_str"]
        
    elif type == "comment":
        # Return if the current line isn't a comment
        if not _is_comment(l_map["comment_str"], line):
            return
            
        line_len_limit = l_map["comment_limit"]
        str_start = l_map["comment_str"]
        
    else:
        return
    
    # Return if the line isn't long enough to require wrapping
    if len(line.rstrip()) <= line_len_limit:
        return
        
    # Split the line by spaces into words
    words = line.split()
    white_space = line[:line.index(words[0][0])]
    
    # Return if the line is nothing but whitespace
    if words == []:
        return
    
    # Remove the first word if it's equal to str_start, e.g. "#"
    if words[0] == str_start:
        del words[0]
    
    # Return if the line is whitespace or a single string
    if words == [] or len(words) <= 1:
        return
       
    # Replace "#word" "//word" with "word"
    if str_start and words[0].startswith(str_start):
        words[0] = words[0][len(str_start):]
    
    # Save a reference to the line start and lengths
    if str_start:
        line_start = "".join([white_space, str_start, " "])
    else:
        line_start = white_space
    line_start_len = len(line_start)
    
    # Begin constructing new string
    it = iter(words)
    new_words = [line_start, next(it, None)]   # "    # word"
    line_len = line_start_len + len(new_words[1])  # Length of "    #"
    word_count = 1
    for word in iter(it):
        # See the length the new line would be
        line_len += len(word) + 1  # length of previous + " word"
        word_count += 1
        
        if line_len > line_len_limit:
            if word_count == 1:
                # Exceed line_len_limit if the line is only 1 word long
                new_words.extend([word, "\r\n", line_start, next(it, None)])
            else:
                # Otherwise add word to the next line
                new_words.extend(["\r\n", line_start, word])
            # Reset variables
            line_len = line_start_len + len(word)
            word_count = 1
        else:
            new_words.extend([" ", word])
    
    # Replace the current line contents then add text
    editor.replaceLine(line_num, "")
    editor.addText("".join(new_words))
    
    # Set the cursor to the end of the formatted paragraph
    editor.lineEnd()
    
    # Move the caret before docstring quotes if nessary
    if type == "docstring":
        if new_words[-1].endswith('"""'):
            editor.charLeft()
            editor.charLeft()
            editor.charLeft()
        

def _on_RETURN_insert_comment(l_map):
    """Insert comment syntax upon pressing enter if appropriate.

    Comment syntax is only added if the previous two lines are comments,
    or if the previous line was a comment and enter was pressed such
    that a trailing string carried over to the new line.
    
    Args:
        l_map (dict): The file's relevant language mapping.
    """
    line_num = editor.lineFromPosition(editor.getCurrentPos())
    p_line, pp_line = get_lines([line_num - 1, line_num - 2])

    trailing_string = editor.getLine(line_num).strip()
        
    if (not (_is_comment(l_map["comment_str"], pp_line) or trailing_string)
            or not _is_comment(l_map["comment_str"], p_line)):
        return

    # Replace the newline with a formatted line "whitespace" + "# " +
    # "trailing string". Set the caret to the end of the new line.
    editor.replaceLine(line_num,
        "".join([p_line[:p_line.index(l_map["comment_str"])],
                 l_map["comment_str"],
                 " ",
                 trailing_string]))
    editor.lineEnd()


def _is_comment(comment_str, line):
    """Checks if the line contains only a comment.
    
    Args:
        comment_str (str): The language specific string denoting a
            comment., for example '#' in python.
        line (str): An line to check for single line comment candidacy.
    
    Returns:
        True if the line is a comment, False otherwise.
    """
    return True if line.lstrip().startswith(comment_str) else False


def _are_comments(comment_str, lines):
    """Checks if all of the lines contain only comments.
    
    Args:
        comment_str (str): The language specific string denoting a
            comment., for example '#' in python.
        lines (iter): An iterable series of line strings to check
            for single line comment candidacy.
    
    Returns:
        True if all of the lines are comments, False otherwise.
    """
    return True if all(_is_comment(comment_str, l) for l in lines) else False

