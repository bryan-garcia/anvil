from pathlib import Path

import typer

from anvil.cli.commands.base import BaseCommand
from anvil.registry.utils import resolve_builder
from anvil.utils import _echo_err


class SerializeCommand(BaseCommand):
    group = None

    def _register(self, app: typer.Typer):
        app.command("serialize")(self.cmd_serialize)

    def cmd_serialize(
        self,
        name: str = typer.Argument(..., help="Registered pipeline name"),
        out: Path = typer.Option(..., "--out", "-o", help="Output YAML path"),
        force: bool = typer.Option(False, "--force", "-f", help="Overwrite if exists"),
    ) -> None:
        """
        Build a pipeline and write its YAML if supported.
        """
        if out.exists() and not force:
            _echo_err(f"Refusing to overwrite existing file: {out}. Use --force.")

        try:
            builder = resolve_builder(name)
            pipeline = builder()
        except Exception as e:
            _echo_err(f"Failed to build '{name}': {e}")

        # Try common serialization hooks
        yaml_text = None
        if hasattr(pipeline, "to_yaml") and callable(getattr(pipeline, "to_yaml")):
            try:
                yaml_text = pipeline.to_yaml()  # type: ignore[attr-defined]
            except Exception as e:
                _echo_err(f"to_yaml() failed: {e}")
        else:
            # Fallback: try a loader utility if present
            try:
                from anvil.loaders import to_yaml  # optional helper

                yaml_text = to_yaml(pipeline)  # type: ignore[assignment]
            except Exception:
                pass

        if not yaml_text:
            _echo_err(
                "Pipeline does not support YAML serialization. Provide a to_yaml() or an anvil.loaders.to_yaml helper."
            )

        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(yaml_text)
        typer.echo(f"Wrote {out}")
