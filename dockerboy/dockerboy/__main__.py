#!/usr/bin/env python3
import json
import yaml

import os
import argparse

from .mydocker import MyContainer, MyImage, MyContainerSpec


def argparser():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", type=str, help="path to config file")

    # main cmd
    subparsers = parser.add_subparsers(dest="cmd")
    subparsers.required = True

    cmds = { "Build": "b", "Run": "r", "Tensorboard": "tb", }

    # build subcmd
    build_parser = subparsers.add_parser(cmds["Build"])

    # run subcmd
    run_parser = subparsers.add_parser(cmds["Run"])
    run_parser.add_argument("run_cmd", type=str, nargs="+")

    run_parser.add_argument("-cd", "--container_dir", type=str, default=None)
    run_parser.add_argument("-p", "--port", type=int, default=None)
    run_parser.add_argument("-i", "--interactive", action="store_true", default=True)
    run_parser.add_argument("-r", "--post_removal", action="store_true", default=True)

    # tensorboard subcmd
    tensorboard_parser = subparsers.add_parser(cmds["Tensorboard"])

    return parser


def default_config():
    root = os.getcwd()
    return MyContainerSpec(**{
        "image_name": "default",
        "dockerfile_path": f"{root}/",
        "host_dir": f"{root}/shared",
        "ports": [(6006,)],
        "interactive": True,
        "post_removal": True,
    })


def main():
    parser = argparser()
    args = parser.parse_args()
    
    if args.config is not None:
        cfg_file = args.config
    else:
        cfg_file = "default-dboy-config.yaml"

    try:
        with open(cfg_file, "r") as f:
            # TODO: Safe load config file
            config = yaml.unsafe_load(f)
    except FileNotFoundError:
        print(f"Config file {cfg_file} not found, using default config")
        config = default_config()

    my_image = MyImage(config.image_name, config.dockerfile_path)
    my_container = MyContainer.from_image(my_image).configure(config.host_dir, config.ports)

    match args.cmd:
        case "b":
            my_image.build()
        case "r":
            my_container.run(args.run_cmd)
        case "tb":
            my_container.run(["tensorboard", "--logdir", "tb_logs"])
        case _:
            raise ValueError(f"Invalid command: {args.cmd}")


if __name__ == "__main__":
    main()