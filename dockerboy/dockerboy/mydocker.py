import subprocess
from dataclasses import dataclass, field

from .dockerutils import build, run


@dataclass
class MyImage:
    _build_status: bool = field(init=False)
    name: str = field()
    dockerfile_path: str

    def __post_init__(self):
        self.name = self.name + "-image"
        self._build_status = None

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
        if self._build_status is None:
            images = subprocess.run(["docker", "images", "-a"], capture_output=True).stdout.decode().split()
            if images.count(self.name) >= 1:
                self._build_status = True
            else:
                self._build_status = False

        return self._build_status

@dataclass
class MyContainer:
    _image: MyImage = field(init=False)
    name: str
    host_dir: str
    container_dir: str
    ports: list[tuple[int, int]]

    interactive: bool
    post_removal: bool

    def __post_init__(self):
        self._configured = False

    def run(self, cmd: list[str], build=False):
        if not self._configured:
            raise ValueError("Container not configured!")

        if build and not self._image._build_status:
            self._image.build()

        if self._image.is_ready():
            run(self._image.name, self.name, self.host_dir, cmd, 
                container_dir=self.container_dir, interactive=self.interactive, 
                post_removal=self.post_removal, port=self.ports)
        else:
            print(f"Image {self._image.name} failed to execute, check build status!")

    @staticmethod
    def from_image(image: MyImage): 
        cls = MyContainer(
            name=image.name.replace("image", "container"),
            host_dir=None,
            container_dir=None,
            ports=[(None, None)],
            interactive=True,
            post_removal=True
        )
        
        cls._image = image
    
        return cls

    def configure(self, host_dir: str, ports: list[tuple[int, int]]):
        self.host_dir = host_dir
        self.container_dir = "/" + host_dir.split("/")[-1]
        self.ports = ports

        self._configured = True

        return self

