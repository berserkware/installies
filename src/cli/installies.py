import argparse
import requests
import json
import sys
import platform
import distro
import os
from pathlib import Path
import subprocess

__version__ = '0.1.0'

class AppNotFoundError(Exception):
    """Raised when an app is not found."""

class ScriptNotFoundError(Exception):
    """Raised when an script is not found"""

class VersionDoesNotMatchRegexError(Exception):
    """Raised when a version does not match an app's versioning regex."""

class Script:
    """A object for retrieving and storing scripts."""

    def __init__(self, app_name, action, content, for_version, last_modified, supported_distros):
        self.app_name = app_name
        self.action = action
        self.content = content
        self.for_version = for_version
        self.last_modified = last_modified
        self.supported_distros = supported_distros


    @classmethod
    def get(cls, app_name, action, distro_id, architechture, for_version=None):
        """Gets a Script or list of Scripts by some parameters."""
        params = {
            'action': action,
            'supports': f'{distro_id}:{architechture}',
        }

        if for_version is not None:
            params['version'] = for_version
        
        r = requests.get(
            url=f'http://localhost:8000/api/apps/{ app_name }/scripts',
            params=params
        )

        if r.status_code == 404:
            raise AppNotFoundError()

        data = r.json()
        
        if 'error' in data.keys() and data['error'] == 'VersionDoesNotMatchRegex':
            raise VersionDoesNotMatchRegexError()

        scripts = data['scripts']

        if len(scripts) == 0:
            raise ScriptNotFoundError()

        script_list = []
        for script in scripts:
            script_list.append(
                cls(
                    app_name=app_name,
                    **script
                )
            )

        if len(script_list) == 1:
            return script_list[0]

        return script_list


    def create_file(self):
        """Create a bash file for the script. Returns the path to the file."""
        path_to_app = Path(f'~/.cache/installies/{self.app_name}').expanduser()
        if not os.path.exists(path_to_app):
            os.makedirs(path_to_app)

        path = f'{path_to_app}/{self.action}.sh'
        with open(path, 'w') as f:
            f.write(self.content)

        os.system(f'chmod +x {path}')
        return path

def do_action(args):
    """Does a action like install, remove, or update"""
    distro_id = distro.id()
    architechture = platform.machine()
    if architechture == 'x86_64':
        architechture = 'amd64'

    split_app_name = args.app_name.split('==')
    app_name = args.app_name
    version = None
    if len(split_app_name) == 2:
        app_name = split_app_name[0]
        version = split_app_name[1]
        
    try:
        script = Script.get(
            app_name,
            args.action,
            distro_id,
            architechture,
            version
        )
    except AppNotFoundError:
        print(f"\033[31mError: No matching app found for {args.app_name}")
        sys.exit()
    except ScriptNotFoundError:
        print(f"\033[31mError: No matching script found for {distro_id}: {architechture}")
        sys.exit()
    except VersionDoesNotMatchRegexError:
        print(f"\033[31mError: Version \"{version}\" does not match app's versioning regex.")
        sys.exit()

    if type(script) == list:
        script = script[0]

    script_file_path = script.create_file()
    
    if os.getuid() == 0:
        answer = input('\033[38;5;214mWarning: You are running the script in sudo mode, do you want to continue? [Y,n] ')
        if answer != 'Y':
            sys.exit()

    if args.output_script:
        print(':: Script Content Start')
        print(script.content)
        print(':: Script Content End')
        print('')
            
    answer = input(':: Proceed with installation? [Y,n] ')
    if answer != 'Y':
        sys.exit()
            
    print(f'-- Executing {args.action} script. --')
    subprocess.run([script_file_path], shell=True)


if __name__ == '__main__':
    main_parser = argparse.ArgumentParser(
        prog='installies',
    )
    main_parser.add_argument('-v', '--version', action='store_true', help="show version")
    subparsers = main_parser.add_subparsers(
        title="Commands"
    )

    action_parser = argparse.ArgumentParser()
    action_parser.add_argument(
        '-o',
        '--output-script',
        action='store_true',
        help="shows the script before exectuting"
    )
    action_parser.add_argument('app_name')
    
    install_parser = subparsers.add_parser(
        "install",
        help="Installs apps",
        parents=[action_parser],
        add_help=False
    )
    install_parser.set_defaults(action='install')

    remove_parser = subparsers.add_parser(
        "remove",
        help="Removes apps",
        parents=[action_parser],
        add_help=False
    )
    remove_parser.set_defaults(action='remove')

    update_parser = subparsers.add_parser(
        "update",
        help="Updates apps",
        parents=[action_parser],
        add_help=False
    )
    update_parser.set_defaults(action='update')

    compile_parser = subparsers.add_parser(
        "compile",
        help="Compiles apps",
        parents=[action_parser],
        add_help=False
    )
    compile_parser.set_defaults(action='compile')
    
    args = main_parser.parse_args()

    if args.version:
        print(f'Installies CLI v{__version__}')

    try:
        if hasattr(args, 'action'):
            do_action(args)
    except KeyboardInterrupt:
        print('\nKeyboardInterrupt, Aborting.')
        sys.exit()

    print('Nothing To Do.')
