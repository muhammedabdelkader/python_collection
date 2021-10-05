from enum import Enum


class params:
    """
    Params class define the params in Key:value and add the in_attack_scope
    flag
    """

    def __init__(self, param_name, param_value, in_attack_scope=False):

        this.param_name = param_name
        this.param_value = param_value
        this.in_attack_scope = in_attack_scope

    def welcome_message(self):
        """Welcome method tells whoami"""
        return "params Class is waving "

    class param_type(Enum):
        """
         param_type inner class used to set the params in correct location
        """
        URL = 'URL'
        Cookie = 'Cookie'
        Body = 'Body'
