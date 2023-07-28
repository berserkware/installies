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

class Installed:
    """An object to get and save the data from ~/.cache/installies/installed.json."""

    def __init__(self, data: dict):
        self.data = data
    
    @classmethod
    def get_or_create(cls):
        """
        Gets the data from the installed.json file.

        If the file doesn't exist, it is created.
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
                f.write(json.dumps({'installed_apps': {}}))

        data = {}
        with open(installed_apps_file, 'r') as f:
            data = json.loads(f.read())
            if 'installed_apps' not in data.keys():
                data['installed_apps'] = {}
            
        return cls(data)

    def save(self):
        """Saves the data."""
        installed_apps_file = Path(f'~/.config/installies/installed.json').expanduser()
        with open(installed_apps_file, 'w') as f:
            f.write(json.dumps(self.data))

installed = Installed.get_or_create()
            
class AppRequest:
    """
    A class to store data the user has given about the app they want to get scripts of.
    """

    def __init__(self, app_name: str):
        split_app_name = args.app_name.split('==')
        
        self.name = split_app_name[0]

        #if the user specifies a version of the app to get
        self.version = (split_app_name[1] if len(split_app_name) == 2 else None)
            
    
class Script:
    """An object for retrieving and storing scripts."""

    def __init__(self, action, content, version):
        self.action = action
        self.content = content
        self.version = version

    @classmethod
    def get_app(cls, app_request):
        """
        Gets the data of an app from a request.

        :param app_request: The data of the app to get.
        """
        apps = requests.get(
            url=f'http://localhost:8000/api/apps',
            params={'name':name},
        ).json()['apps']

        if len(apps) == 0:
             print(f"\033[31mError: No matching app found for {app_request.name}")
             sys.exit()

        app = apps[0]
        
        return app
        
    @classmethod
    def get(cls, app_request, action, distro_id, architechture, for_version=None):
        """Gets a Script or list of Scripts by some parameters."""
        params = {
            'action': action,
            'supports': f'{distro_id}:{architechture}',
        }

        if for_version is not None:
            params['version'] = for_version
        
        r = requests.get(
            url=f'http://localhost:8000/api/apps/{ app_request.name }/scripts',
            params=params
        )

        data = r.json()
    
        scripts = data['scripts']

        if len(scripts) == 0:
            print(f"\033[31mError: No matching script found for {distro_id}: {architechture}")
            sys.exit()

        app = cls.get_app()
            
        script_list = []
        for script in scripts:
            
            version = app.current_version
            if app_request.version is not None:
                version = app_request.version
                
            script['content'].replace('<version>', version)
            script_list.append(
                cls(
                    action=script['action'],
                    content=script['content'],
                    version=version,
                )
            )

        if len(script_list) == 1:
            return script_list[0]

        return script_list


    def create_file(self, app_name):
        """
        Create a bash file for the script. Returns the path to the file.

        :param app_name: The name of the app the script is for.
        """
        path_to_app = Path(f'~/.cache/installies/{app_name}').expanduser()
        if not os.path.exists(path_to_app):
            os.makedirs(path_to_app)

        path = f'{path_to_app}/{self.action}.sh'
        with open(path, 'w') as f:
            f.write(self.content)

        os.system(f'chmod +x {path}')
        return path

        
def confirm(prompt: str):
    """
    Asks the user a yes or no question.

    If the user replies with anything other that "Y", the program exits. The string
    " [Y/n]" is appended to the ending of the prompt.

    :param prompt: The question to ask the user.
    """

    answer = input(f'{prompt} [Y/n]')
    if answer != 'Y':
        sys.exit()

def run_script(script, args):
    """Runs the inputted script."""

    script_file_path = script.create_file()

    # warns user if cli is running in sudo mode
    if os.getuid() == 0:
        confirm(
            '\033[38;5;214mWarning: You are running the script in sudo mode, do you want to continue?'
        )

    confirm(':: Proceed?')

    print(f'-- Executing {script.action} script. --')
    subprocess.run([script_file_path], shell=True)
    
def install(args):
    pass

def remove(args):
    pass

def update(args):
    pass

def compile(args):
    pass

def run(args):
    pass

def create_parser():
    """Creates the parser."""
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

    return main_parser


if __name__ == '__main__':
    parser = create_parser()
    args = parser.parse_args()

    if args.version:
        print(f'Installies CLI v{__version__}')

    if not hasattr(args, 'action'):
        sys.exit()
