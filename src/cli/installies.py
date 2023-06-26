import argparse
import requests
import json
import sys
import platform
import distro

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
    subparsers = main_parser.add_subparsers(
        title="Commands"
    )

    install_parser = subparsers.add_parser("install", help="Installs apps")
    install_parser.add_argument('app_name')
    install_parser.set_defaults(action='install')
    
    args = main_parser.parse_args()

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

    print(script)
