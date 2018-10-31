"""A script enabling autoformat features upon CHARADDED.

Todo:
    - Make it only work if active file ends '.py'.
    - Make the reformat line work for splitting into multiple lines.
    - Make it work for docstrings too?
    - Currently assuming line endings are /r/n
    - If there's a selection wrap with "" '' {} [] () <>
    - Reformat paragraphs intelligently (if key press is enter, etc)
"""

from npplib.common import print_debug
from npplib.insert import on_CHARADDED_insert


def main():
    """Binds the callbacks to the relevant notifications.
    
    Script acts as a toggle for binding/unbinding the callback.
    """
    try:
        bound = not bound
    except Exception:
        global bound
        bound = True
    
    if bound:
        print_debug("Binding on_CHARADDED_insert functions")
        editor.callback(on_CHARADDED_insert, [SCINTILLANOTIFICATION.CHARADDED])
    else:
        print_debug("Un-binding on_CHARADDED_insert functions")
        editor.clearCallbacks(on_CHARADDED_insert, [SCINTILLANOTIFICATION.CHARADDED])

    
if __name__ == '__main__':
    main()
