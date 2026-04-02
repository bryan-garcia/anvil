# Haystack RAG

A lightweight framework for experimenting with Retrieval-Augmented Generation (RAG) pipelines via Haystack.

## Overview

- **Pipeline Registry**: Central registry for discovering and managing pipelines
- **Config-Driven Execution**: Run pipelines from YAML configurations
- **Serialization**: Convert built pipelines to YAML for easy modification
- **CLI Interface**: Command-line tool for pipeline management

## Setup

```bash
uv venv
uv pip install -e .
```

## Usage

```bash
anvil registry list
anvil run <pipeline-name> --config <path-to-yaml>
anvil serialize <pipeline-name> --out <path>
```

## Structure

- `src/anvil/cli/` - CLI framework (Typer-based)
- `src/anvil/registry/` - Pipeline registry management
- `src/anvil/pipelines/` - Pipeline utilities
- `src/anvil/loaders.py` - YAML/pipeline loading
- `examples/` - Example pipeline YAML configs
