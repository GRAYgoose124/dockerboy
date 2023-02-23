# image management
import subprocess


def build(image_name, dockerfile_path="."):
    # build the docker image and get the results
    results = subprocess.run(["docker", "build", "-t", image_name, dockerfile_path],
                            capture_output=True).stdout.decode()
    
    # if the image was built successfully, return True
    if "Successfully built" in results:
        return True
    else:
        return False