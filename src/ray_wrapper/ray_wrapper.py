import yaml
from pathlib import Path

with open('development_requirements.yml', 'r') as stream:
    development_requirements = yaml.safe_load(stream)


def load_deployment_config(deployment_config_path: Path):
    with open(deployment_config_path, 'r') as f:
        try:
            config = yaml.safe_load(f)
            return config
        except yaml.YAMLError as exc:
            return exc

class ConfigCheck:
    #check if the deployment config is correct
    """

    """
    def __init__(self, config:dict):
        self.config = config

    def check_required_fields(self):
        keys = self.config.keys()
        missing = set(development_requirements['required_fields']) - set(keys)

        if missing:
            raise KeyError(f"The following required values for deployment are missing in the given config: {", ".join(missing)}")


class ModelLoader:
    """

    """
    def __init__(self):
        pass
        #check if the model class has the correct function (needs to have a __call__function)

class Deployment:
    """

    """
    def __init__(self):
        pass


        #find a way to load the model and bind it into an app
        #create a unique id for the deployemnt and for the app
        #serve run
