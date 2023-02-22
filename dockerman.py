#!/usr/bin/env python3
import argparse
import subprocess

def build(image_name, dir="."):
    # build the docker image
    subprocess.run(["docker", "build", "-t", image_name, "."])

def run(image_name: str, container_name: str, host_dir: str, 
        cmd: list[str], container_dir: str = None, port: int | tuple = None, 
        interactive: bool = True, post_removal: bool = True
    ):
    # runs docker run -it [-p 6006:6006] [--it] [--rm] --gpus all --name $CONTAINER_NAME -v $HOST_DIR:$CONTAINER_DIR -w $CONTAINER_DIR $IMAGE_NAME "$*"
    # where flags in [] can be omitted
    interactive = True
    post_removal = True

    optional = []

    if port is not None:
        # if isinstance(port, int):
        #     port2 = port
        # else:
        #     port2 = port[1]
        #     port = port[0]
        optional = ["-p", f"{port}:{port}"]

    if interactive:
        optional.append("-it")

    if post_removal:
        optional.append("--rm")

    # if container_dir is not specified, use the last directory in host_dir
    if container_dir is None:
        container_dir = host_dir.split("/")[-1]

    subprocess.run(["docker", "run", *optional, "--gpus", "all",
                    "--name", container_name, "-v", f"{host_dir}:{container_dir}", 
                    "-w", container_dir, image_name, *cmd])


def argparser():
    parser = argparse.ArgumentParser()
    # main cmd
    subparsers = parser.add_subparsers(dest="cmd")
    subparsers.required = True

    # build subcmd
    build_parser = subparsers.add_parser("build")
    build_parser.add_argument("image_name", type=str)
    build_parser.add_argument("-d", "--dir", type=str, default=".")


    # run subcmd
    run_parser = subparsers.add_parser("run")
    run_parser.add_argument("image_name", type=str)
    run_parser.add_argument("container_name", type=str)
    run_parser.add_argument("host_dir", type=str)
    
    run_parser.add_argument("run_cmd", type=str, nargs="+")
    run_parser.add_argument("-cd", "--container_dir", type=str, default=None)
    run_parser.add_argument("-p", "--port", type=int, default=None)
    run_parser.add_argument("-i", "--interactive", action="store_true", default=True)
    run_parser.add_argument("-r", "--post_removal", action="store_true", default=True)

    return parser


if __name__ == "__main__":
    parser = argparser()
    args = parser.parse_args()

    match args.cmd:
        case "build":
            build(args.image_name, args.dir)
        case "run":
            run(args.image_name, args.container_name, args.host_dir, 
                args.run_cmd, args.container_dir, args.port, args.interactive, args.post_removal)
        case _:
            raise ValueError(f"Invalid command: {args.cmd}")