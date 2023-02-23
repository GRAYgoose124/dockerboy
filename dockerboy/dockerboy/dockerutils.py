import subprocess
import logging
import time

logger = logging.getLogger(__name__)


def build(image_name, dockerfile_path="."):
    # build the docker image and get the results
    results = subprocess.run(["docker", "build", "-t", image_name, dockerfile_path],
                            capture_output=True).stdout.decode()
    
    # if the image was built successfully, return True
    if "Successfully built" in results:
        return True
    else:
        return False


def portcheck(port: tuple[int, int]):
    """ Ports can be malformed: (a,a) (a,) (,b) (a,b) """
    if isinstance(port[0], int) or isinstance(port[1], int):
        if port[0] is None:
            port = (port[1], port[1])
        elif port[1] is None:
            port = (port[0], port[0])

    return port


def container_run(image_name: str, container_name: str, host_dir: str,
        cmd: list[str], container_dir: str = None, port: list[tuple] | tuple = (None, None),
        interactive: bool = True, post_removal: bool = True
    ):
        optional = []

        if isinstance(port, list):
            for p in port:
                p = portcheck(p)
                optional.extend(["-p", f"0.0.0.0:{p[0]}:{p[1]}"])
        else:
            port = portcheck(port)
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


def exec_or_run(image_name: str, container_name: str, host_dir: str, 
        cmd: list[str], container_dir: str = None, port: list[tuple] | tuple = (None, None), 
        interactive: bool = True, post_removal: bool = True
    ):
    # If the container is already running, just execute the command in it
    if is_container_running(container_name):
        print(f"Container {container_name} already exists. Executing \"{cmd}\" in it.")
        subprocess.run(["docker", "exec", "-it", container_name, *cmd])
    elif does_container_exist(container_name):
        # TODO: Restart with new command either by rebuilding from image or by using docker commit
        print(f"Container {container_name} already exists, but is not running. Starting it and executing \"{cmd}\"")
        subprocess.run(["docker", "start", container_name], capture_output=True).stdout.decode()
        subprocess.run(["docker", "exec", "-it", container_name, *cmd])
    else:
        container_run(image_name, container_name, host_dir, cmd, container_dir, port, interactive, post_removal)


def shutdown_container(container_name: str):
    subprocess.run(["docker", "stop", container_name])
  

def is_container_running(container_name: str):
    if subprocess.run(["docker", "ps"], 
                        capture_output=True).stdout.decode().split().count(container_name) == 1:
        return True
    else:
        return False


def does_container_exist(container_name: str):
    if subprocess.run(["docker", "ps", "-a"], 
                        capture_output=True).stdout.decode().split().count(container_name) == 1:
        return True
    else:
        return False


def get_container_id(container_name: str):
    # TODO: presumes only one container with the same name exists
    return subprocess.run(["docker", "ps", "-a", "--filter", f"name={container_name}", "--format", "{{.ID}}"],
                            capture_output=True).stdout.decode().strip()


def commit_stopped_container(container_name: str):
    # TODO: presumes only one container with the same name exists
    container_id = get_container_id(container_name)
    subprocess.run(["docker", "commit", container_id, container_name])


def remove_container(container_name: str):
    # remove by id
    subprocess.run(["docker", "rm", get_container_id(container_name)])


def cmd_new_container(image_name: str, container_name: str, host_dir: str,
        cmd: list[str], container_dir: str = None, port: list[tuple] | tuple = (None, None),
        interactive: bool = True, post_removal: bool = True):
    # https://stackoverflow.com/questions/32353055/how-to-start-a-stopped-docker-container-with-a-different-command
    # https://www.thorsten-hans.com/how-to-run-commands-in-stopped-docker-containers/

    if does_container_exist(container_name):
        if is_container_running(container_name):
            shutdown_container(container_name)

        remove_container(container_name)
    
    container_run(image_name, container_name, host_dir, cmd, container_dir, port, interactive, True)


