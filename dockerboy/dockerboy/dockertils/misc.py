# misc util helpers
import os


def portcheck(port: tuple[int, int]):
    """ Ports can be malformed: (a,a) (a,) (,b) (a,b) """
    if isinstance(port[0], int) or isinstance(port[1], int):
        if port[0] is None:
            port = (port[1], port[1])
        elif port[1] is None:
            port = (port[0], port[0])

    return port


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


def update_version(container_name: str):
    # parse the version number
    name, version = container_name.split(":")
    version = int(version[1:])
    return f"{name}:v{version}"


def image_to_container_name(image_name: str):
    """Dockerboy API always defines a container name as the image name with "image" replaced by "container".
    The image name always ends with "image" and the container name always ends with "container".
    """
    return image_name.replace("image", "container")