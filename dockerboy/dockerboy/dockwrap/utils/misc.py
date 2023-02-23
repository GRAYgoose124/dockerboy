# misc util helpers
import os


def format_port(port: tuple[int, int]):
    """ Ports can be malformed: (a,a) (a,) (,b) (a,b) """
    if isinstance(port[0], int) or isinstance(port[1], int):
        if port[0] is None:
            port = (port[1], port[1])
        elif port[1] is None:
            port = (port[0], port[0])
    else:
        port = None

    return port


def format_ports(ports: list[tuple[int, int]]):
    """ Ports can be malformed: (a,a) (a,) (,b) (a,b) """
    # filter out Nones and format the ports
    ports = [format_port(port) for port in ports if port is not None]
    if len(ports) == 0:
        ports = None
    elif len(ports) == 1:
        ports = ports[0]
    else:
        return ports


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
