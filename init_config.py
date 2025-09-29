"""Sets up the application and configuration."""

from pathlib import Path


class DefaultConfig:
    """Default configuration values."""

    def __init__(self, file_path: str, example_file_path: str) -> None:
        """Initialize the DefaultConfig."""
        self.file_name = file_path
        self.example_file_name = example_file_path


def main() -> None:
    """Create initial configuration files."""
    Path("config").mkdir(exist_ok=True)

    # create empty config files if they don't exist
    configs = [
        DefaultConfig("config/models.yaml", "config_example/models.yaml"),
        DefaultConfig("config/vector.yaml", "config_example/vector.yaml"),
    ]
    for config in configs:
        file_path = Path(config.file_name)
        if not file_path.exists():
            with Path.open(file_path, "w") as f:
                example_path = Path(config.example_file_name)
                if example_path.exists():
                    with Path.open(example_path, "r") as ef:
                        f.write(ef.read())
                else:
                    f.write("# Add your configuration here\n")
            print(f"Created {config.file_name}")  # noqa: T201
        else:
            print(f"{config.file_name} already exists, skipping.")  # noqa: T201

    print("Initialization complete.")  # noqa: T201


if __name__ == "__main__":
    main()
