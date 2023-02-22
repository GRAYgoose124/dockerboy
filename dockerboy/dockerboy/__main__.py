#!/usr/bin/env python3
import os
import argparse

from .mydocker import MyTfContainer, MyTFImage


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
    # tensorboard_parser.add_argument("image_name", type=str)

    return parser


def main():
    parser = argparser()
    args = parser.parse_args()

    image_name = "my-tf-image"
    dockerfile_path = f"{os.getcwd()}/my-docker-tf/"
    host_dir = f"{os.getcwd()}/src"
    # container_dir = "/src"
    port = (6006, 6006)

    # my_image = MyTFImage("my-tf-image", f"{os.getcwd()}/my-docker-tf/", f"{os.getcwd()}/src", "/src", [(6006, 6006)])
    my_image = MyTFImage(image_name, dockerfile_path)
    my_container = MyTfContainer.from_image(my_image).configure(host_dir, [port])

    match args.cmd:
        case "build":
            my_image.build()
        case "run":
            my_container.run(args.run_cmd)
        case "tensorboard":
            my_container.run(["tensorboard", "--logdir", "tb_logs"])
        case _:
            raise ValueError(f"Invalid command: {args.cmd}")


if __name__ == "__main__":
    main()