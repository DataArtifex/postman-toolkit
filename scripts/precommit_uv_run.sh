#!/usr/bin/env bash
# A wrapper to run pre-commit commands with `uv run`
# - If VIRTUAL_ENV is set, run `uv run --active ...` (monorepo / active virtualenv mode)
# - If VIRTUAL_ENV is not set, run `uv run ...` (standalone mode)

if [ -n "$VIRTUAL_ENV" ]; then
    exec uv run --active "$@"
else
    exec uv run "$@"
fi
