from dataclasses import dataclass, field
from dataclasses import dataclass

from .wrapper import DockerWrapper
from dockerboy.dockwrap.utils.build import build
from dockerboy.dockwrap.utils.run import exec_or_run

@dataclass
class MyContainerSpec:
    name: str
    dockerfile: str
    host_dir: str
    ports: list[tuple[int, int]]

    interactive: bool
    post_removal: bool
    rebuild: bool

    # TODO: Maybe spec shouldn't know about MyContainer and MyImage
    def into_container(self, build=False):
        image = self.into_image()

        cls = MyContainer.from_image(image)
        cls.configure(
            self.host_dir,
            self.ports,
            self.interactive,
            self.post_removal)

        if build:
            cls.build_image()

        return cls

    def into_image(self):
        return MyImage(self.name, self.dockerfile)


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
        print("Starting build...")
        status = build(self.name, self.dockerfile)
        print(
            f"image `{self.name}` {'built!' if status else 'failed to build!'}")
        self._build_status = status
        return status

    def is_ready(self):
        """ Returns True if the image was built successfully.

        """
        if self._build_status is None:
            self._build_status = DockerWrapper.is_image_ready(self.name)

        return self._build_status

    @staticmethod
    def from_spec(spec: MyContainerSpec):
        return spec.into_image()


@dataclass
class MyContainer(MyContainerSpec):
    _image: MyImage = field(init=False)
    _alive: bool = field(init=False)
    # TODO: If we decide to standardize the directory structure, we can remove
    # this
    container_dir: str
    # this was passed to image, but it's not used here
    dockerfile: str = field(init=False)

    def __post_init__(self):
        self._image = None
        self._alive = DockerWrapper.is_container_running(self.name)
        self._configured = False

    def run(self, cmd: list[str], build=False,
            interactive=None, post_removal=None):
        if isinstance(cmd, str):
            cmd = cmd.split()

        if not self._configured:
            raise ValueError("Container not configured!")

        if build and not self._image._build_status:
            self._image.build()

        if self._image.is_ready():
            if interactive is None:
                interactive = self.interactive
            if post_removal is None:
                post_removal = self.post_removal

            new_name = exec_or_run(self._image.name, self.name, self.host_dir, cmd,
                                   container_dir=self.container_dir, interactive=interactive,
                                   post_removal=post_removal, port=self.ports, rebuild=self.rebuild)

            if new_name != self.name:
                # exec_or_run returns the new container name if it was rebuilt
                # Because it was already rebuilt, we shouldn't use .rebuild()
                self.name = new_name
                self._image.name = self.name.replace("container", "image")

            self._alive = DockerWrapper.is_container_running(self.name)
        else:
            print(
                f"Image {self._image.name} failed to execute, check build status!")

    def shutdown(self):
        if self._alive:
            DockerWrapper.shutdown_container(self.name)
            self._alive = DockerWrapper.is_container_running(self.name)

            print(f"Shutdown status: {not self._alive}")

    def remove(self):
        if self._alive:
            self.shutdown()

        DockerWrapper.remove_container(self.name)

    def build_image(self):
        return self._image.build()

    def rebuild(self):
        self.name = DockerWrapper.update_and_rebuild_container(self.name)
        self._image = MyImage(self.name, self._image.dockerfile)

        self.build_image()

    @staticmethod
    def from_image(image: MyImage, build=False):
        cls = MyContainer(
            name=image.name.replace("image", "container"),
            host_dir=None,
            container_dir=None,
            ports=[(None, None)],
            interactive=True,
            post_removal=True,
            rebuild=True
        )

        cls._image = image

        return cls

    @staticmethod
    def from_spec(spec: MyContainerSpec, build=False):
        container = spec.into_container()
        if build:
            container.build_image()

        return

    def configure(self, host_dir: str = None,
                  ports: list[tuple[int, int]] = None, interactive: bool = True, post_removal: bool = True):
        if host_dir is not None:
            self.host_dir = host_dir

        self.container_dir = "/" + host_dir.split("/")[-1]

        if ports is not None:
            self.ports = ports
        else:
            self.ports = [(6006, 6006)]

        self.interactive = interactive
        self.post_removal = post_removal

        self._configured = True

        return self
