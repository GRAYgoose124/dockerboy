#!/usr/bin/env python3
from dockerboy.utils.wrapper import DockerWrapper
from dockerboy.utils.config import interactive_config_builder, load_config, default_config, save_config
import yaml

import os
import logging
import argparse


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

cmds = { "Build": "b",
            "Run": "r", 
            "Remove": "rm",
            "Shutdown": "sd",
            "Tensorboard": "tb", 
            "Config gen": "cfg",
            "Container management": "cm" }

def argparser():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", type=str, help="path to config file")

    # main cmd
    subparsers = parser.add_subparsers(dest="cmd")
    subparsers.required = True

    # build subcmd
    build_parser = subparsers.add_parser(cmds["Build"])
    build_parser.add_argument("-r", "--rebuild", action="store_true", dest="rebuild", default=False)

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
    config_gen_parser.add_argument("-i", "--interactive", action="store_true", dest="build_cfg_interactive", default=False)

    # container management subcmd
    container_management_parser = subparsers.add_parser(cmds["Container management"])
    # add container management subcmd argument
    help_str = "\n".join([f"\t\t{name} - {c}" for name, c in DockerWrapper.get_commands().items()])

    container_management_parser.add_argument("cm_cmd", type=str, help=f"CM cmds: {help_str}", choices=DockerWrapper.get_commands().values())
    container_management_parser.add_argument("cm_args", type=str, help="CM command arguments", nargs="*")

    return parser


def main():
    parser = argparser()
    args = parser.parse_args()
    
    if args.config is not None:
        cfg_file = args.config
    else:
        cfg_file = ".dboy.yaml"

    # If this is set, we're running a `cfg` command which will generate a config file and exit.
    if args.cmd == cmds["Config gen"]:
        if args.build_cfg_interactive:
            save_config(interactive_config_builder(), args.config)
        else:
            save_config(default_config(), args.config)
    else:
        if not os.path.exists(cfg_file):
            # Generate config
            config = interactive_config_builder()
            save_config(config, cfg_file)
        else:
            config = load_config(cfg_file)

        my_container = config.into_container()

    match args.cmd:
        case "b":
            if args.rebuild:
                my_container.rebuild()
            else:
                my_container.build_image()
        case "r":
            print(f"We will remove the container after running: {args.post_removal}")
            my_container.run(args.run_cmd, interactive=args.interactive, post_removal=args.post_removal)

            # if a container was created without --rm before, we need to remove it manually
            if args.post_removal and DockerWrapper.does_container_exist(my_container.name):
                my_container.remove()
        # TODO: can be CM commands?
        case "sd":
            my_container.shutdown()
        case "tb":
            my_container.run("tensorboard --logdir tb_logs")
        case "cm":
            found_cmd = False
            for method, cmd in DockerWrapper.get_commands().items():
                if cmd == args.cm_cmd:
                    found_cmd = True
                    print(f"{cmd}: Running {method} with args {args.cm_args}")
                    print(DockerWrapper.run_method(method, *args.cm_args))
                    break
            if not found_cmd:
                print(f"Command {args.cm_cmd} not found")
        case "cfg":
            pass
        case _:
            print("Unknown command")
                    

if __name__ == "__main__":
    main()