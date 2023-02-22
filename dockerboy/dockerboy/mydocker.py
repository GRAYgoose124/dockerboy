import subprocess
from dataclasses import dataclass, field

from .dockerutils import build, run


@dataclass
class MyTFImage:
    _build_status: bool = field(init=False)
    name: str
    dockerfile_path: str

    def build(self):
        status = build(self.name, self.dockerfile_path)
        print(f"image `{self.name}` {'built!' if status else 'failed to build!'}")
        self._build_status = status
        return status

    def is_ready(self):
        """ Returns True if the image was built successfully. 
        
            TODO: Check docker to see if an image with the same name exists.
        """
        # use docker to see if the image exists
        if not hasattr(self, "_build_status"):
            images = subprocess.run(["docker", "images", "-a"], capture_output=True).stdout.decode().split()
            if images.count(self.name) >= 1:
                self._build_status = True

        return hasattr(self, "_build_status") and self._build_status

@dataclass
class MyTfContainer:
    _image: MyTFImage = field(init=False)
    name: str
    host_dir: str
    container_dir: str
    ports: list[tuple[int, int]]

    interactive: bool
    post_removal: bool

    def run(self, cmd: list[str], build=False):
        if build and not hasattr(self._image, "_build_status"):
            self._image.build()

        if self._image.is_ready():
            run(self._image.name, self.name, self.host_dir, cmd, 
                container_dir=self.container_dir, interactive=self.interactive, 
                post_removal=self.post_removal, port=self.ports)
        else:
            print(f"Image {self._image.name} failed to execute, check build status!")

    @staticmethod
    def from_image(image: MyTFImage, build=False): 
        cls = MyTfContainer(
            name=image.name.replace("image", "container"),
            host_dir=None,
            container_dir=None,
            ports=[(None, None)],
            interactive=True,
            post_removal=True
        )
        
        cls._image = image

        if build:
            image.build()
        
        return cls

    def configure(self, host_dir: str, ports: list[tuple[int, int]]):
        self.host_dir = host_dir
        self.container_dir = "/" + host_dir.split("/")[-1]
        self.ports = ports

        return self

