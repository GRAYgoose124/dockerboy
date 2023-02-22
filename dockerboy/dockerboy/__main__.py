#!/usr/bin/env python3
import json
import yaml

import os
import logging
import argparse

from .mydocker import MyContainer, MyImage, MyContainerSpec


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


def argparser():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", type=str, help="path to config file")

    # main cmd
    subparsers = parser.add_subparsers(dest="cmd")
    subparsers.required = True

    cmds = { "Build": "b", "Run": "r", "Tensorboard": "tb", "Config gen": "cg" }

    # build subcmd
    build_parser = subparsers.add_parser(cmds["Build"])

    # run subcmd
    run_parser = subparsers.add_parser(cmds["Run"])
    run_parser.add_argument("run_cmd", type=str, nargs="+")

    # tensorboard subcmd
    tensorboard_parser = subparsers.add_parser(cmds["Tensorboard"])

    # config gen subcmd
    config_gen_parser = subparsers.add_parser(cmds["Config gen"])
    config_gen_parser.add_argument("config_file", type=str, help="path to config file", default=".dboy.yaml.default", nargs="?")

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
            my_container.run(args.run_cmd)
        case "tb":
            my_container.run("tensorboard --logdir tb_logs")
        case "cg":
            with open(args.config_file, "w") as f:
                yaml.dump(default_config(), f)
        case _:
            raise ValueError(f"Invalid command: {args.cmd}")


if __name__ == "__main__":
    main()