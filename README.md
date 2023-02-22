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

If you somehow configure `.dboy.yaml` generated from `dboy -cg` properly, then you can try:

    dboy b
    dboy r <command>

    # especially while something is already running
    dboy tb 