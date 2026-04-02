from anvil.cli.commands.base import BaseCommand
import typer
from anvil.utils import _echo_err, dumps_json, load_yaml
from anvil.pipelines.utils import _pipeline_heads
from anvil.registry.utils import resolve_builder
from rich.pretty import pprint
from haystack import Pipeline

class RunCommand(BaseCommand):
    """
    Command for running a pipeline.
    """
    group = None

    def _register(self, app: typer.Typer):
        """
        Register the command with the typer app.
        """
        app.command("run")(self.cmd_run)

    def cmd_run(
        self,
        name: str = typer.Argument(..., help="Registered pipeline name"),
        config_path: str = typer.Option(
            ...,
            "--config",
            "-c",
            help="Inputs to pipeline entry-points",
        ),
        dry: bool = typer.Option(False, "--dry", help="Build only; do not call .run()"),
        ) -> None:
        """
        Build the pipeline and execute `.run()` if available.
        """

        try:
            builder = resolve_builder(name)
        except Exception as e:
            _echo_err(f"Failed to resolve '{name}': {e}")

        try:
            pipeline: Pipeline = builder()
        except Exception as e:
            _echo_err(f"Builder for '{name}' failed: {e}")

        typer.echo(f"Built pipeline '{name}'")
        typer.echo(pipeline)

        pipeline_inputs = pipeline.inputs()
        pipeline_heads = {
            head: pipeline_inputs[head] for head in _pipeline_heads(pipeline=pipeline)
        }

        typer.echo(f"Pipeline '{name}' heads: ")
        for component_name, component_inputs in pipeline_heads.items():
            typer.echo(f"-> {component_name} ")
            pprint(component_inputs)

        typer.echo("Loading inputs for Pipeline heads")
        data = load_yaml(fpath=config_path)
        typer.echo("-> Loaded the following: ")
        pprint(data)

        if dry:
            return

        # Execute if it looks like a Haystack Pipeline
        if hasattr(pipeline, "run") and callable(getattr(pipeline, "run")):
            try:
                result = pipeline.run(data=data)
            except Exception as e:
                _echo_err(f"Pipeline run failed: {e}")
            # Pretty print result if JSON-serializable; else repr
            try:
                typer.echo(message=dumps_json(data))
            except Exception:
                typer.echo(repr(result))
        else:
            _echo_err(
                "The built object has no .run(). Use --dry to only build, or ensure your builder returns a runnable Pipeline."
            )
