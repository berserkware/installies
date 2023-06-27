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

def get_scripts(app_name):
    """Gets the app's scripts in json"""
    r = requests.get(url=f'http://localhost:8000/api/apps/{ app_name }/scripts')
    
    if r.status_code == 404:
        raise AppNotFoundError()
    
    return r.json()['scripts']

def get_matching_scripts(scripts, distro_id, architechture):
    """Gets the scripts matching the distro_id and architechture"""

    matching_scripts = []
    
    for script in scripts:
        for distro_architechture in script['supported_distros'].keys():
            if distro_architechture == architechture or distro_architechture == '*':
                for distro in script['supported_distros'][distro_architechture]:
                    if distro == distro_id or distro == '*':
                        matching_scripts.append(script)

    if matching_scripts == []:
        raise ScriptNotFoundError()

    return matching_scripts

def create_script_file(app_name, script):
    """Creates a file for a script, returns the path."""
    path_to_app = Path(f'~/.cache/installies/{app_name}').expanduser()
    if not os.path.exists(path_to_app):
        os.makedirs(path_to_app)

    path = f'{path_to_app}/{script["action"]}.sh'
    with open(path, 'w') as f:
        f.write(script['content'])

    os.system(f'chmod +x {path}')
    return path

def do_action(args):
    """Does a action like install, remove, or update"""
    try:
        scripts = get_scripts(args.app_name)
    except AppNotFoundError:
        print(f"\033[31mError: No matching app found for {args.app_name}")
        sys.exit()

    distro_id = distro.id()
    architechture = platform.machine()
    if architechture == 'x86_64':
        architechture = 'amd64'

    try:
        scripts = get_matching_scripts(scripts, distro_id, architechture)
    except ScriptNotFoundError:
        print(f"\033[31mError: No matching script found for {distro_id}: {architechture}")
        sys.exit()

    try:
        script = get_script_for_action(scripts, args.action)
    except ScriptNotFoundError:
        print(f"\033[31mError: No {args.action} script found.")
        sys.exit()

    script_file_path = create_script_file(args.app_name, script)

    if os.getuid() == 0:
        answer = input('\033[38;5;214mWarning: You are running the script in sudo mode, do you want to continue? [Y,n] ')
        if answer != 'Y':
            sys.exit()

    if args.output_script:
        print(':: Script Content Start')
        print(script['content'])
        print(':: Script Content End')
        print('')
            
    answer = input(':: Proceed with installation? [Y,n] ')
    if answer != 'Y':
        sys.exit()
            
    print(f'-- Executing {args.action} script. --')
    subprocess.run([script_file_path], shell=True)


def get_script_for_action(scripts, action):
    """Gets a script for a specific action."""

    for script in scripts:
        if script['action'] == action:
            return script

    raise ScriptNotFoundError()

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
