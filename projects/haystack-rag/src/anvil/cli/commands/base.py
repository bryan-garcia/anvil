from abc import ABC, abstractmethod
import typer

class BaseCommand(ABC):
    """
    Base class for all commands.
    """
    group: str | None

    def register(self, app: typer.Typer):
        target = app
        if self.group is not None:
            subcommand = typer.Typer(help=f"{self.group} subcommands")
            app.add_typer(subcommand, name=self.group)
            target = subcommand
        self._register(target)

    @abstractmethod
    def _register(self, app: typer.Typer):
        """
        Register the command with the typer app.
        """
        pass