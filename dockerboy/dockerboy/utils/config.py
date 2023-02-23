import os
from dockerboy.mydocker import MyContainerSpec
import yaml
from os.path import join

from .misc import format_ports

def default_config():
    root = os.getcwd()
    return {
        "image_name": "default",
        "dockerfile_path": f"{root}/",
        "host_dir": f"{root}/shared",
        "ports": [(6006,6006)],
        "interactive": True,
        "post_removal": True,
        "rebuild": True
    }

def load_config(cfg_file):
    try:
        with open(cfg_file, "r") as f:
            # TODO: Safe load config file
            config = yaml.unsafe_load(f)
    except FileNotFoundError:
        print(f"Config file {cfg_file} not found, using default config")
        config = MyContainerSpec(**default_config())
    
    return config

def save_config(config, cfg_file):
    # if file exists back it up
    if os.path.exists(cfg_file):
        os.rename(cfg_file, f"{cfg_file}.bak")
        print(f"Config file {cfg_file} already exists, backing up to {cfg_file}.bak")
        
    with open(cfg_file, "w") as f:
                yaml.dump(config, f)

def interactive_config_builder(cwd=False):
    if cwd:
        root = os.getcwd()
    else:
        root = ""

    config = default_config()
    config["image_name"] = input("Image name: ")
    config["dockerfile_path"] = join(root, input("Dockerfile path: "))
    config["host_dir"] = join(root, input("Host shared directory: "))
    config["ports"] = format_ports(input("Ports: "))
    config["interactive"] = False if input("Interactive mode? (Y/n): ").lowercase() != "y" else True
    config["post_removal"] = False if input("Post removal? (Y/n): ").lowercase() != "y" else True
    config["rebuild"] =  False if input("Rebuild? (Y/n): ").lowercase() != "y" else True
    return config