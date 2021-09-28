import json

import yaml

__version__ = "0.1"


class converter:


    """ Converter class """


def __init__(self, file_path=0):
    if file_path:
        self.file_path = file_path


def json_2_yaml(self, json_file_path=0):


    """ Change json to yaml file """
if json_file_path:
    self.json_file_path = json_file_path
elif self.file_path:
    self.json_file_path = self.file_path
else:
    return
with open(self.json_file_path, 'r+') as json_file:
    return yaml.dump(json.load(json_file))


def yaml_2_json(self, yaml_file_path=0):


    """ change yaml file to json file """
if yaml_file_path:
    self.yaml_file_path = yaml_file_path
elif self.file_path:
    self.yaml_file_path = self.file_path
else:
    return
with open(self.yaml_file_path, 'r+') as yaml_file:
    return json.dumps(yaml.safe_load(yaml_file))
