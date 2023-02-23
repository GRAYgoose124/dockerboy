import subprocess
import logging

from typing import Literal

from dockerboy.dockwrap.utils.misc import image_to_container_name, update_version


logger = logging.getLogger(__name__)


# container management
class DockerWrapper:
    # get statics from class without instantiating
    @staticmethod
    def get_commands():
        # [method for method in dir(DockerWrapper)
        #     if callable(getattr(DockerWrapper, method))
        # and not (method.startswith("__") or method == "get_methods" or method
        # == "run_method")]

        # get methods and their cmd from docstring
        method_cmds = {}
        for method in dir(DockerWrapper):
            m = getattr(DockerWrapper, method)
            if callable(m) and not (method.startswith("__")
                                    or method == "get_commands" or method == "run_method"):
                method_cmds[method] = m.__doc__.strip()

        return method_cmds

    @staticmethod
    def run_method(method_name: str, *args, **kwargs):
        method = getattr(DockerWrapper, method_name)
        return method(*args, **kwargs)

    @staticmethod
    def shutdown_container(container_name: str):
        """sd"""
        subprocess.run(["docker", "stop", container_name])

    @staticmethod
    def remove_container(container_name: str):
        """rc"""
        subprocess.run(
            ["docker", "rm", DockerWrapper.get_container_id(container_name)])

    @staticmethod
    def remove_image(image_name: str):
        """ri"""
        subprocess.run(["docker", "rmi", image_name])

    # container state

    @staticmethod
    def get_running_containers() -> list[str]:
        """grc"""
        return subprocess.run(["docker", "ps"],
                              capture_output=True).stdout.decode().split()[1::]

    @staticmethod
    def get_all_containers() -> list[str]:
        """gac"""
        return subprocess.run(["docker", "ps", "-a"],
                              capture_output=True).stdout.decode().split()[1::]

    @staticmethod
    def is_container_running(container_name: str):
        """icr"""
        return container_name in DockerWrapper.get_running_containers()

    @staticmethod
    def does_container_exist(container_name: str):
        """dce"""
        return container_name in DockerWrapper.get_all_containers()

    def get_container_name_from_id(container_id: str):
        """gcnfi"""
        return subprocess.run(["docker", "ps", "-a", "--filter", f"id={container_id}", "--format", "{{.Names}}"],
                              capture_output=True).stdout.decode().strip()

    def is_image_ready(image_name: str):
        """iir"""
        images = subprocess.run(
            ["docker", "images", "-a"], capture_output=True).stdout.decode().split()
        if images.count(image_name) >= 1:
            return True
        else:
            return False

    @staticmethod
    def get_container_id(container_name: str):
        """gci"""
        # TODO: presumes only one container with the same name exists
        ids = subprocess.run(["docker", "ps", "-a", "--filter", f"name={container_name}", "--format", "{{.ID}}"],
                             capture_output=True).stdout.decode().strip()
        # check if there are multiple ids separated by a newline
        if "\n" in ids:
            ids = ids.split("\n")
            logger.warning(
                f"Multiple containers matching {container_name} exist: {ids}")
            return ids[0]
        else:
            return ids

    @staticmethod
    def get_container_ps_format(
            container_name: str, format_type: Literal["ID", "Image", "Command", "Created", "Status", "Ports", "Names"]):
        """gcf"""
        return subprocess.run(["docker", "ps", "-a", "--filter", f"name={container_name}", "--format", f"{{.{format_type}}}"],
                              capture_output=True).stdout.decode().strip()

    @staticmethod
    def commit_stopped_container(container_name: str):
        """csc"""
        # TODO: presumes only one container with the same name exists
        container_id = DockerWrapper.get_container_id(container_name)
        if not isinstance(container_id, str):
            raise ValueError(
                f"Multiple containers matching {container_name} exist: {container_id}")

        # Update the container_name by appending a version number
        container_name = update_version(container_name)

        subprocess.run(["docker", "commit", container_id, container_name])

        return container_name

    @staticmethod
    def update_and_rebuild_container(container_name: str):
        """uarc"""
        # Does the container exist?
        if not DockerWrapper.does_container_exist(container_name):
            raise ValueError(f"Container {container_name} does not exist")

        # Ensure container is stopped
        if DockerWrapper.is_container_running(container_name):
            DockerWrapper.shutdown_container(container_name)

        # First, commit the container
        new_container_name = DockerWrapper.commit_stopped_container(
            container_name)

        # Then, remove the old container
        DockerWrapper.remove_container(container_name)

        return new_container_name

    @staticmethod
    def get_built_images(container_name: str):
        """gbi"""
        image_name = image_to_container_name(container_name)
        return subprocess.run(["docker", "images", "--filter", f"reference={image_name}", "--format", "{{.Repository}}"],
                              capture_output=True).stdout.decode().strip()

    @staticmethod
    def kill_container(container_name: str):
        """kc"""
        subprocess.run(["docker", "kill", container_name])
