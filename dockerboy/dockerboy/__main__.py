#!/usr/bin/env python3
import json
from dockerboy.dockertils.wrapper import DockerWrapper
import yaml

import os
import logging
import argparse

from .mydocker import MyContainerSpec


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


def argparser():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", type=str, help="path to config file")

    # main cmd
    subparsers = parser.add_subparsers(dest="cmd")
    subparsers.required = True

    cmds = { "Build": "b",
             "Run": "r", 
             "Remove": "rm",
             "Shutdown": "sd",
             "Tensorboard": "tb", 
             "Config gen": "cg",
             "Container management": "cm" }

    # build subcmd
    build_parser = subparsers.add_parser(cmds["Build"])

    # run subcmd
    run_parser = subparsers.add_parser(cmds["Run"])
    run_parser.add_argument("-ni", "--non-interactive", action="store_false", dest="interactive", default=True)
    run_parser.add_argument("-nrm", "--post-removal", action="store_false", dest="post_removal", default=True)
    run_parser.add_argument("run_cmd", type=str, nargs="+")

    # remove subcmd
    remove_parser = subparsers.add_parser(cmds["Remove"])
    
    # shutdown subcmd
    shutdown_parser = subparsers.add_parser(cmds["Shutdown"])

    # tensorboard subcmd
    tensorboard_parser = subparsers.add_parser(cmds["Tensorboard"])

    # config gen subcmd
    config_gen_parser = subparsers.add_parser(cmds["Config gen"])
    config_gen_parser.add_argument("config_file", type=str, help="path to config file", default=".dboy.yaml.default", nargs="?")

    # container management subcmd
    container_management_parser = subparsers.add_parser(cmds["Container management"])
    # add container management subcmd argument
    container_management_parser.add_argument("cm_cmd", type=str, help="CM command to run", choices=DockerWrapper.get_commands().values())
    container_management_parser.add_argument("cm_args", type=str, help="CM command arguments", nargs="*")

    return parser


def default_config():
    root = os.getcwd()
    return MyContainerSpec(**{
        "image_name": "default",
        "dockerfile_path": f"{root}/",
        "host_dir": f"{root}/shared",
        "ports": [(6006,6006)],
        "interactive": True,
        "post_removal": True,
    })


def main():
    parser = argparser()
    args = parser.parse_args()
    
    if args.config is not None:
        cfg_file = args.config
    else:
        cfg_file = ".dboy.yaml"

    try:
        with open(cfg_file, "r") as f:
            # TODO: Safe load config file
            config = yaml.unsafe_load(f)
    except FileNotFoundError:
        print(f"Config file {cfg_file} not found, using default config")
        config = default_config()

    my_container = config.into_container()

    match args.cmd:
        case "b":
            my_container.build_image()
        case "r":
            print(f"We will remove the container after running: {args.post_removal}")
            my_container.run(args.run_cmd, interactive=args.interactive, post_removal=args.post_removal)
        case "sd":
            my_container.shutdown()
        case "rm":
            my_container.remove()
        case "tb":
            my_container.run("tensorboard --logdir tb_logs")
        case "cg":
            with open(args.config_file, "w") as f:
                yaml.dump(default_config(), f)
        case _:
            found_cmd = False
            # container management
            for method, cmd in DockerWrapper.get_commands().items():
                if cmd == args.cm_cmd:
                    found_cmd = True
                    print(f"{cmd}: Running {method} with args {args.cm_args}")
                    print(DockerWrapper.run_method(method, *args.cm_args))
                    break
            if not found_cmd:
                print(f"Command {args.cm_cmd} not found")
                    

if __name__ == "__main__":
    main()