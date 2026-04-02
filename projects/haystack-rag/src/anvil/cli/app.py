import typer

from anvil.cli.commands.registry import RegistryCommand
from anvil.cli.commands.run import RunCommand
from anvil.cli.commands.serialize import SerializeCommand

app = typer.Typer(help="Anvil – simple RAG pipeline registration and execution")
RegistryCommand().register(app)
RunCommand().register(app)
SerializeCommand().register(app)


def main() -> None:
    app()


if __name__ == "__main__":
    main()
