from installies.globals import (
    supported_distros, 
    database, 
    apps_path
)
from installies.database.models import User, App, Script
from installies.lib.url import make_slug
from installies.lib.random import gen_random_id
from datetime import date
from peewee import *

import os
import json

def get_script_data_from_post(post: dict):
    """
    Gets the data about the scripts from POST data, and parses it 
    into a list of dictionary. The list is layed out as follows.
    
    [
        {
            'action': 'The script action, (install or remove),',
            'varients': [
                {
                    'content': 'the content of the script area',
                    'works_on': ['ubuntu', 'debian', 'pop_os']
                }
            ]
        }
    ]
    
    The list contains dictionaries which contain the data about 
    the scripts. The scripts have a varients key which is a list
    of the script's varients, with the content of the script, and
    the distros that it works on, which will be left empty if no
    distros combatible.
    
    :param post: The post data to get the data about the scripts
        from.
    """
    
    # this dictionary contains all the script data, except with
    # there ids being the keys. This is to organize the script data.
    temp_dict = {}
    
    for key in post.keys():
        split_key = key.split('-')
        
        # keys that are not scripts are ignored
        if split_key[0] != 'script':
            continue
        
        # adds the dictionary for the script if it doesnt exist
        if len(split_key) >= 2 and split_key[1] not in temp_dict:
            temp_dict[split_key[1]] = {
                'varients': {}
            }
            
        # adds script action to temp_dict if key contains it
        if len(split_key) == 3 and split_key[2] == 'action':
            temp_dict[split_key[1]]['action'] = post[key]
            continue
        
        # creates dictionary for varient under scripts if doesnt already exist
        if len(split_key) >= 4 and split_key[2] == 'varient' and split_key[3] not in temp_dict[split_key[1]]['varients']:
            temp_dict[split_key[1]]['varients'][split_key[3]] = {
                'works_on': []
                }
            
        # if the key contains a compatible distro, add to dictionary
        if len(split_key) == 6 and split_key[4] == 'compatible':
            temp_dict[split_key[1]]['varients'][split_key[3]]['works_on'].append(split_key[5])
            
        # if the key contains a script text area, add it to the content
        if len(split_key) == 5 and split_key[4] == 'textarea':
            temp_dict[split_key[1]]['varients'][split_key[3]]['content'] = post[key]
            
    # this holds the data after the ids of the scripts and varients
    # have been removed
    script_list = []
    
    for script_keys in temp_dict.keys():
        # gets the script dictionarys
        script = temp_dict[script_keys]
        
        new_script = {}
        new_script['action'] = script['action']
        
        # removes the ids of the varients and adds them to the new script
        new_script['varients'] = list(script['varients'].values())
        
        script_list.append(new_script)
            
    return script_list

def create_app_folder(app: App):
    """
    Creates the folders to put the app's scripts in. Returns the path
    
    :param app: The app to get the data to create the folder from.
    """
    
    app_author = User.get_by_id(app.author.id)
    
    # creates a folder for the user, to store the apps in
    user_dir = os.path.join(apps_path, app_author.username)
    if os.path.isdir(user_dir) == False:
        os.mkdir(user_dir)
        
    # creates the folder for the app
    app_dir = os.path.join(user_dir, app.slug)
    if os.path.isdir(app_dir) == False:
        os.mkdir(app_dir)
        
    return app_dir

def create_app(name: str, description: str, author_id: int) -> App:
    """
    Creates an App object.
    
    :param name: The name of the app.
    :param description: The app description.
    :param author_id: The id of the author of the script.
    """
    
    # creates a slug out of the name of the script
    slug = make_slug(name)
    
    # gets the creation date of the app
    creation_date = date.today()
    
    author = User.get(User.id == author_id)
    
    app = App(
        name=name,
        slug=slug,
        description=description,
        creation_date=creation_date,
        author=author
    )
    
    create_app_folder(app)
    
    return app
    
def create_script_file(content: str, app_filepath: str) -> str:
    """
    Creates the file for the script content. Returns the path to the
    file.
    
    :param content: The content of the script.
    :param app_filepath: The filepath of the app the script is a part
        of.
    """
    
    script_filename = f'script-{gen_random_id()}.sh'
    
    script_filepath = os.path.join(app_filepath, script_filename)
    
    with open(script_filepath, 'w') as f:
        f.write(content)
        
    return script_filepath
    
def create_script(
    action: str, 
    works_on: list, 
    content: str, 
    app_filepath: str,
    app: App
    ) -> Script:
    """
    Creates a Script object.
    
    :param action: The action of the script.
    :param works_on: 
    """
    
    works_on_str = json.dumps(works_on)
    
    script_filepath = create_script_file(content, app_filepath)
    
    script = Script(
        action=action,
        works_on=works_on_str,
        filepath=script_filepath,
        app=app
    )
    
    return script