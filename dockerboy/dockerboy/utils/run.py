import subprocess
import logging

from dockerboy.utils.wrapper import DockerWrapper
from dockerboy.utils.misc import format_port

logger = logging.getLogger(__name__)


def container_run(image_name: str, container_name: str, host_dir: str,
        cmd: list[str], container_dir: str = None, port: list[tuple] | tuple = (None, None),
        interactive: bool = True, post_removal: bool = True
    ):
        optional = []

        if isinstance(port, list):
            for p in port:
                p = format_port(p)
                optional.extend(["-p", f"0.0.0.0:{p[0]}:{p[1]}"])
        else:
            port = format_port(port)
            optional.extend(["-p", f"0.0.0.0:{port[0]}:{port[1]}"])

        if interactive:
            optional.append("-it")

        if post_removal:
            optional.append("--rm")

        # if container_dir is not specified, use the last directory in host_dir
        if container_dir is None:
            container_dir = host_dir.split("/")[-1]

        final_cmd = ["docker", "run", *optional, "--gpus", "all",
                        "--name", container_name, "-v", f"{host_dir}:{container_dir}", 
                        "-w", container_dir, image_name, *cmd]

        logger.debug(f"Running command: {' '.join(final_cmd)}")
        subprocess.run(final_cmd)


def cmd_new_container(image_name: str, container_name: str, host_dir: str,
        cmd: list[str], container_dir: str = None, port: list[tuple] | tuple = (None, None),
        interactive: bool = True, post_removal: bool = True):
    # https://stackoverflow.com/questions/32353055/how-to-start-a-stopped-docker-container-with-a-different-command
    # https://www.thorsten-hans.com/how-to-run-commands-in-stopped-docker-containers/

    if DockerWrapper.does_container_exist(container_name):
        if DockerWrapper.is_container_running(container_name):
            DockerWrapper.shutdown_container(container_name)

        DockerWrapper.remove_container(container_name)
    
    container_run(image_name, container_name, host_dir, cmd, container_dir, port, interactive, post_removal)


def exec_or_run(image_name: str, container_name: str, host_dir: str, 
        cmd: list[str], container_dir: str = None, port: list[tuple] | tuple = (None, None), 
        interactive: bool = True, post_removal: bool = True, rebuild: bool = False
    ):
    # If the container is already running, just execute the command in it
    if DockerWrapper.is_container_running(container_name):
        print(f"Container {container_name} already exists. Executing \"{cmd}\" in it.")
        subprocess.run(["docker", "exec", "-it", container_name, *cmd])
    elif DockerWrapper.does_container_exist(container_name):
        # TODO: Restart with new command either by rebuilding from image or by using docker commit
        # This probably only works for containers that were originally started with a living process
        # such as python or bash.
        print(f"Container {container_name} already exists, but is not running. Starting it and executing \"{cmd}\"")
        start_str = subprocess.run(["docker", "start", container_name], capture_output=True).stdout.decode()
        if "Error" in start_str:
            print("Error starting container. Creating a new one and executing the command.")
            if rebuild:
                print("Rebuilding container")
                container_name = DockerWrapper.update_and_rebuild_container(container_name)
                container_run(image_name, container_name, host_dir, cmd, container_dir, port, interactive, post_removal)
            else:
                cmd_new_container(image_name, container_name, host_dir, cmd, container_dir, port, interactive, post_removal)
        else:
            print("Started container")
            subprocess.run(["docker", "exec", "-it", container_name, *cmd])
    else:
        print(f"Container {container_name} does not exist. Creating it and executing \"{cmd}\"")
        cmd_new_container(image_name, container_name, host_dir, cmd, container_dir, port, interactive, post_removal)

    return container_name
