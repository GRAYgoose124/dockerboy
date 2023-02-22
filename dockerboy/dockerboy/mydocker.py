import yaml
import subprocess

from dataclasses import dataclass, field
from dataclasses import dataclass

from .dockerutils import build, run

@dataclass
class MyContainerSpec:
    image_name: str
    dockerfile_path: str
    host_dir: str
    ports: list[tuple[int, int]]
    interactive: bool
    post_removal: bool

    def into_container(self):
        image = self.into_image()

        cls = image.into_container()
        cls.configure(self.host_dir, self.ports, self.interactive, self.post_removal)

        return cls
    
    def into_image(self):
        return MyImage(self.image_name, self.dockerfile_path)


@dataclass
class MyImage:
    _build_status: bool = field(init=False)
    name: str = field()
    dockerfile: str

    def __post_init__(self):
        self.name = self.name + "-image"
        self._build_status = None
        self.is_ready()

    def build(self):
        status = build(self.name, self.dockerfile)
        print(f"image `{self.name}` {'built!' if status else 'failed to build!'}")
        self._build_status = status
        return status

    def is_ready(self):
        """ Returns True if the image was built successfully. 
        
        """
        if self._build_status is None:
            images = subprocess.run(["docker", "images", "-a"], capture_output=True).stdout.decode().split()
            if images.count(self.name) >= 1:
                self._build_status = True
            else:
                self._build_status = False

        return self._build_status

    @staticmethod
    def from_spec(spec: MyContainerSpec):
        return spec.into_image()

    def into_container(self):
        return MyContainer.from_image(self)


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
        if isinstance(cmd, str):
            cmd = cmd.split()

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

    def build_image(self):
        return self._image.build()

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
    
    @staticmethod
    def from_spec(spec: MyContainerSpec):
        return spec.into_container()

    def configure(self, host_dir: str, ports: list[tuple[int, int]] = [(6006,)], interactive: bool = True, post_removal: bool = True):
        self.host_dir = host_dir
        self.container_dir = "/" + host_dir.split("/")[-1]
        self.ports = ports
        self.interactive = interactive
        self.post_removal = post_removal

        self._configured = True

        return self

