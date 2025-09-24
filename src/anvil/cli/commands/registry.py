from anvil.cli.commands.base import BaseCommand
import typer
from anvil.utils import _echo_err, _normalize_name, dumps_json
from anvil.registry.utils import list_entries, show_entry, register_yaml, del_entry
from pathlib import Path


class RegistryCommand(BaseCommand):
    """
    Command for the registry.
    """

    group = "registry"

    def _register(self, app: typer.Typer):
        """
        Register the command with the typer app.
        """
        app.command("list")(self.cmd_list)
        app.command("show")(self.cmd_show)
        app.command("add")(self.cmd_add_yaml)
        app.command("remove")(self.cmd_remove_yaml)

    def cmd_list(
        self,
        json_out: bool = typer.Option(False, "--json", help="Emit JSON"),
    ) -> None:
        """
        List registered pipelines.
        """
        try:
            entries = list_entries()  # dict[name] = ref
        except Exception as e:
            _echo_err(f"Failed to load registry: {e}")

        if json_out:
            typer.echo(message=dumps_json(data=entries))
            return

        if not entries:
            typer.echo("No pipelines registered.")
            return

        width = max(len("NAME"), *(len(n) for n in entries))
        typer.echo(f"{'NAME'.ljust(width)}  REF")
        typer.echo(f"{'-' * width}  {'-' * 40}")
        for name, ref in entries.items():
            typer.echo(f"{name.ljust(width)}  {ref}")

    def cmd_show(self, name: str) -> None:
        """
        Show details for a registered pipeline.
        """
        try:
            info = show_entry(name)  # {name, kind, ref}
        except KeyError as e:
            _echo_err(str(e))
        except Exception as e:
            _echo_err(f"Error: {e}")

        typer.echo(dumps_json(info))

    def cmd_add_yaml(
        self,
        name: str = typer.Argument(..., help="Registry name"),
        path: Path = typer.Argument(..., help="Path to pipeline YAML"),
    ) -> None:
        """
        Register a serialized pipeline YAML file under a name.
        """
        try:
            name = _normalize_name(name)
            if not name:
                raise ValueError("Registry names cannot be empty.")
            register_yaml(name, str(path))
            typer.echo(f"Registered '{name}' -> {path}")
        except Exception as e:
            _echo_err(f"Failed to register '{name}': {e}")

    def cmd_remove_yaml(
        self,
        name: str = typer.Argument(..., help="Pipeline name"),
    ) -> None:
        """
        Remove a user-registered serialized pipeline YAML file under a name.
        """
        try:
            del_entry(name)
            typer.echo(f"Removed '{name}'")
        except Exception as e:
            _echo_err(f"Failed to remove '{name}': {e}")
