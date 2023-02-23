```python
my_container = config.into_container()

match args.cmd:
    case "b":
        my_container.build_image()
    case "r":
        my_container.run(args.run_cmd)
    case "tb":
        my_container.run("tensorboard --logdir tb_logs")
    case "cg":
        with open(args.config_file, "w") as f:
            yaml.dump(default_config(), f)
    case _:
        raise ValueError(f"Invalid command: {args.cmd}")
```

# Installing dockerboy
    cd dockerboy/
    poetry install

    dboy -h

# Running
You should create a shared dir and a Dockerfile first.
## Generate config
    dboy cfg -i

## Build and run some command

    dboy b [--rebuild]
    dboy r <command>

    # especially while something is already running
    dboy tb 

# Container management
This is a passthrough for DockerWrapper - you can run anything there. Rudimentary.

    dboy cm -h

This works on the currently managed container:

    dboy sd
    dboy rm