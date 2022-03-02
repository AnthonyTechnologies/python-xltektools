"""Command-line interface."""
import click


@click.command()
@click.version_option()
def main() -> None:
    """xltektools."""


if __name__ == "__main__":
    main(prog_name="python-xltektools")  # pragma: no cover
