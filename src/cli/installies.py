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


class AppRequest:
    """
    A class to store data the user has given about the app they want to get scripts of.
    """

    def __init__(self, app_name: str):
        split_app_name = args.app_name.split('==')
        
        self.name = split_app_name[0]

        #if the user specifies a version of the app to get
        self.version = (split_app_name[1] if len(split_app_name) == 2 else None)
    

class App:
    """An object for retrieving and storing apps."""

    def __init__(
            self,
            name,
            display_name,
            current_version,
            creation_date,
            last_modified,
            submitter,
    ):
        self.name = name
        self.display_name = display_name
        self.current_version = current_version
        self.creation_date = creation_date
        self.last_modified = last_modified
        self.submitter = submitter

    @classmethod
    def get(cls, name):
        """Gets an app."""

        params = {
            'name': name,
        }

        r = requests.get(
            url=f'http://localhost:8000/api/apps',
            params=params,
        )

        data = r.json()

        apps = data['apps']

        if len(apps) == 0:
            raise AppNotFoundError()

        app = apps[0]
        
        return cls(
            name=app['name'],
            display_name=app['display_name'],
            current_version=app['current_version'],
            creation_date=app['creation_date'],
            last_modified=app['last_modified'],
            submitter=app['submitter'],
        )
    
    
class Script:
    """An object for retrieving and storing scripts."""

    def __init__(self, app: App, action, content, for_version, last_modified, supported_distros):
        self.app = app
        self.action = action
        self.content = content
        self.for_version = for_version
        self.last_modified = last_modified
        self.supported_distros = supported_distros


    @classmethod
    def get(cls, app, action, distro_id, architechture, for_version=None):
        """Gets a Script or list of Scripts by some parameters."""
        params = {
            'action': action,
            'supports': f'{distro_id}:{architechture}',
        }

        if for_version is not None:
            params['version'] = for_version
        
        r = requests.get(
            url=f'http://localhost:8000/api/apps/{ app.name }/scripts',
            params=params
        )

        if r.status_code == 404:
            raise AppNotFoundError()

        data = r.json()
    
        scripts = data['scripts']

        if len(scripts) == 0:
            raise ScriptNotFoundError()

        script_list = []
        for script in scripts:
            script_list.append(
                cls(
                    app=app,
                    **script
                )
            )

        if len(script_list) == 1:
            return script_list[0]

        return script_list


    def create_file(self):
        """Create a bash file for the script. Returns the path to the file."""
        path_to_app = Path(f'~/.cache/installies/{self.app.name}').expanduser()
        if not os.path.exists(path_to_app):
            os.makedirs(path_to_app)

        path = f'{path_to_app}/{self.action}.sh'
        with open(path, 'w') as f:
            f.write(self.content)

        os.system(f'chmod +x {path}')
        return path


def get_or_create_installed_file():
    """
    Creates the folder and file for installed.json if it doesn't exist.

    Returns the path.
    """

    cache_folder = Path(f'~/.config/installies').expanduser()
    if not os.path.exists(cache_folder):
        os.makedirs(cache_folder)

    installed_apps_file = os.path.join(cache_folder, 'installed.json')
    try:
        f = open(installed_apps_file, 'x')
        f.close()
    except FileExistsError:
        pass

    # if file cannot be loaded into json, it is marked as empty
    empty = False
    with open(installed_apps_file, 'r') as f:
        content = f.read()
        try:
            json.loads(content)
        except json.JSONDecodeError:
            empty = True

    # if file is empty, write empty json data to it
    if empty:
        with open(installed_apps_file, 'w') as f:
            f.write('{}')
    
    return installed_apps_file

    
def do_action(args):
    """Does a action like install, remove, or update"""
    installed_file = get_or_create_installed_file()

    installed = {}
    with open(installed_file, 'r') as f:
        installed = json.loads(f.read())

    if 'installed_apps' not in installed.keys():
        installed['installed_apps'] = {}
    
    distro_id = distro.id()
    architechture = platform.machine()
    if architechture == 'x86_64':
        architechture = 'amd64'

    app_request = AppRequest(args.app_name)

    try:
        app = App.get(name=app_request.name)
    except AppNotFoundError:
        print(f"\033[31mError: No matching app found for {app_request.name}")
        sys.exit()
    
    try:
        script = Script.get(
            app,
            args.action,
            distro_id,
            architechture,
            app_request.version,
        )

        # if more than one scripts are returned, use the first one
        if type(script) == list:
            script = script[0]
            
    except ScriptNotFoundError:
        print(f"\033[31mError: No matching script found for {distro_id}: {architechture}")
        sys.exit()

    version = app.current_version
    if app_request.version is not None:
        version = app_request.version
    script.content = script.content.replace('<version>', version)
        
    script_file_path = script.create_file()

    # warns user if cli is running in sudo mode
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

    if args.action.lower() == 'install':
        installed['installed_apps'][app_request.name] = version

    if args.action.lower() == 'remove':
        if app_request.app_name in installed['installed_apps'].keys():
            del installed['installed_apps'][app_request.name]

    with open(installed_file, 'w') as f:
        f.write(json.dumps(installed))


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
