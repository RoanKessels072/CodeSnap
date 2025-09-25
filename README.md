# Xoko Python Project Template

This template uses [uv](https://github.com/astral-sh/uv), [ruff](https://github.com/astral-sh/ruff) and [pytest](https://docs.pytest.org) to bootstrap python projects. Also uses [pre-commit](https://pre-commit.com) for more consistency when committing code and managing Git hook scripts.

I tried to keep the template minimal but added `src`, `tests` and `docs` directories to provide guidance for setting up a project code structure.

Also review `LICENSE` (use your own user handle) to see if it fits your purpose.


## Install

First make sure that `uv` is installed.

Install the Git hook scripts.

```console
uv run pre-commit install
```

## Usage

```console
uv run foo
```

Adapt as needed (don't forget to also review `pyproject.toml`).

See [uv documentation](https://docs.astral.sh/uv).


## Test

```console
uv run pytest
```

See [pytest documentation](https://docs.pytest.org).


## Code Formatting and linting

```console
uv run ruff check
uv run ruff format
```

Instead of running this yourself, set up your IDE to perform auto formatting. Ensure that the autoformatting matches the configuration set up for `ruff` as it will be run automatically before committing by the `pre-commit` hooks.

See [ruff documentation](https://docs.astral.sh/ruff).


## Type checking

```console
uv run ty check
```

Note that this will produce an error. I did this to illustrate how `ty` spots issues that may not always be caught with `pytest`.

Although [ty](https://github.com/astral-sh/ty) is not flagged safe for production yet. It does do it's job quite well already. If this doesn't suit you feel free to replace with [mypy](https://mypy-lang.org).

See [ty documentation](https://docs.astral.sh/ty).


## Environment variables

Use a `.env` file for adding variables and secrets such as API tokens. This file will not be committed (see `.env.example`).
