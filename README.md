# Anvil

A sandbox repository for Claude Code sessions. Each project under `projects/` is a self-contained experiment, prototype, or debugging exercise.

## Structure

```
projects/
  haystack-rag/    # RAG pipeline framework via Haystack
  <your-idea>/     # Add your own
```

## Getting Started

```bash
# Start a new project
mkdir -p projects/my-project
cd projects/my-project

# For Python projects
uv init
uv venv
```

See `CLAUDE.md` for conventions and guidance.
