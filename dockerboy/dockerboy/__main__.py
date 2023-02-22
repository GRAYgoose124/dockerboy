#!/usr/bin/env python3
import os
import argparse

from .dockerutils import build, run


def argparser():
    parser = argparse.ArgumentParser()
    # main cmd
    subparsers = parser.add_subparsers(dest="cmd")
    subparsers.required = True

    # build subcmd
    build_parser = subparsers.add_parser("build")
    #build_parser.add_argument("image_name", type=str)
    #build_parser.add_argument("-d", "--dir", type=str, default=".")


    # run subcmd
    run_parser = subparsers.add_parser("run")
    # run_parser.add_argument("image_name", type=str)
    # run_parser.add_argument("container_name", type=str)
    # run_parser.add_argument("host_dir", type=str)
    run_parser.add_argument("run_cmd", type=str, nargs="+")

    run_parser.add_argument("-cd", "--container_dir", type=str, default=None)
    run_parser.add_argument("-p", "--port", type=int, default=None)
    run_parser.add_argument("-i", "--interactive", action="store_true", default=True)
    run_parser.add_argument("-r", "--post_removal", action="store_true", default=True)

    # tensorboard subcmd
    tensorboard_parser = subparsers.add_parser("tensorboard")
    tensorboard_parser.add_argument("image_name", type=str)

    return parser


def my_tf_image_build():
    image_name = "my-tf-image"
    dockerfile_path = f"{os.getcwd()}/my-docker-tf/"
    build(image_name, dockerfile_path)


def my_tf_run(cmd: list[str], interactive: bool = True, post_removal: bool = True, port: int = 6006):
    # TODO: Make this data a dataclass and json serializable
    image_name = "my-tf-image"
    container_name = "my-tf-container"
    host_dir = f"{os.getcwd()}/src"
    container_dir = "/src"
    port = (6006, 6006)

    run(image_name, container_name, host_dir, cmd, 
        container_dir=container_dir, interactive=interactive, 
        post_removal=post_removal, port=port)


def main():
    parser = argparser()
    args = parser.parse_args()

    match args.cmd:
        case "build":
            my_tf_image_build()
        case "run":
            my_tf_run(args.run_cmd, args.interactive, args.post_removal)
        case "tensorboard":
            # tensorboard --logdir /tb_logs --host 0.0.0.0
            my_tf_run(["tensorboard", "--logdir", "/tb_logs", "--host", "0.0.0.0"])
        case _:
            raise ValueError(f"Invalid command: {args.cmd}")


if __name__ == "__main__":
    main()