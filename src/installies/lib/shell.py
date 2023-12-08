class Shell:
    """
    A base class to store script shells.
    """

    name = 'shell'
    file_extension = 'sh'
    file_mimetype = 'application/x-shellscript'
    interpreter_path = '/bin/sh'
    interpreter_arg = ''

    function_matcher_start = ''
    function_matcher_block = '''
if [ "<action>" == "$1" ]; then
    <action>
    exit
fi'''
    function_matcher_end = '''
echo "Please re-run the script with one of the following actions as the first argument: <actions>."'''

    @classmethod
    def get_all_subshells(cls):
        """Gets all the sub classes of the shell."""
        return set(cls.__subclasses__()).union(
            [s for c in cls.__subclasses__() for s in c.get_all_subshells()])
    
    @classmethod
    def get_all_names(cls):
        """Gets all the names of the shell subclasses."""
        all_shells = cls.get_all_subshells()

        # the list of shells are reverse so that the bash shell is the first.
        return [shell.name for shell in all_shells][::-1]

    @classmethod
    def get_shell_by_name(cls, name: str):
        """Gets a shell by it's name."""
        all_shells = cls.get_all_subshells()

        for shell in all_shells:
            if shell.name == name:
                return shell

        return None


class BashShell(Shell):

    name = 'bash'
    interpreter_path = '/bin/bash'

class PythonShell(Shell):
    
    name = 'python'
    file_extension = 'py'
    file_mimetype = 'text/x-python'
    interpreter_path = '/bin/python'

    function_matcher_start = '''
import sys'''
    function_matcher_block = '''
if len(sys.argv) > 1 and sys.argv[1] == '<action>':
    <action>()
    sys.exit()'''
    function_matcher_end = '''
print(f'Please re-run the script with one of the following actions as the first argument: {", ".join("<actions>".split())}.')'''
    
