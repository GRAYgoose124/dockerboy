import subprocess
import logging


logger = logging.getLogger(__name__)


# exe funcs

# image management
def build(image_name, dockerfile_path="."):
    # build the docker image and get the results
    results = subprocess.run(["docker", "build", "-t", image_name, dockerfile_path],
                            capture_output=True).stdout.decode()
    
    # if the image was built successfully, return True
    if "Successfully built" in results:
        return True
    else:
        return False


# container management
class DockerWrapper:
    # get statics from class without instantiating
    @staticmethod
    def get_commands():
        # [method for method in dir(DockerWrapper) 
        #     if callable(getattr(DockerWrapper, method)) 
        #     and not (method.startswith("__") or method == "get_methods" or method == "run_method")]

        # get methods and their cmd from docstring
        method_cmds = {}
        for method in dir(DockerWrapper):
            m = getattr(DockerWrapper, method)
            if callable(m) and not (method.startswith("__") or method == "get_commands" or method == "run_method"):
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
        subprocess.run(["docker", "rm", DockerWrapper.get_container_id(container_name)])

    @staticmethod
    def remove_image(image_name: str):
        """ri"""
        subprocess.run(["docker", "rmi", image_name])

    @staticmethod
    def is_container_running(container_name: str):
        """icr"""
        if subprocess.run(["docker", "ps"], 
                            capture_output=True).stdout.decode().split().count(container_name) == 1:
            return True
        else:
            return False

    @staticmethod
    def does_container_exist(container_name: str):
        """dce"""
        if subprocess.run(["docker", "ps", "-a"], 
                            capture_output=True).stdout.decode().split().count(container_name) == 1:
            return True
        else:
            return False

    @staticmethod
    def get_container_id(container_name: str):
        """gci"""
        # TODO: presumes only one container with the same name exists
        return subprocess.run(["docker", "ps", "-a", "--filter", f"name={container_name}", "--format", "{{.ID}}"],
                                capture_output=True).stdout.decode().strip()

    @staticmethod
    def commit_stopped_container(container_name: str):
        """csc"""
        # TODO: presumes only one container with the same name exists
        container_id = DockerWrapper.get_container_id(container_name)
        subprocess.run(["docker", "commit", container_id, container_name])

    @staticmethod
    def image_to_container_name(image_name: str):
        """itcn"""
        """Dockerboy API always defines a container name as the image name with "image" replaced by "container".
        The image name always ends with "image" and the container name always ends with "container".
        """
        return image_name.replace("image", "container")

    @staticmethod
    def get_built_images(container_name: str):
        """gbi"""
        image_name = DockerWrapper.image_to_container_name(container_name)
        return subprocess.run(["docker", "images", "--filter", f"reference={image_name}", "--format", "{{.Repository}}"],
                                capture_output=True).stdout.decode().strip()

    @staticmethod
    def kill_container(container_name: str):
        """kc"""
        subprocess.run(["docker", "kill", container_name])