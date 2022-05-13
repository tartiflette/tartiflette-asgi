# Contributing guidelines

Thank you for your interest in contributing to this project! Here are some tips to get you started.

## Getting started

- Consider [opening an issue](https://github.com/tartiflette/tartiflette-asgi/issues/new) if the change you are proposing is not trivial. :+1:
- Fork this repo on GitHub, then clone it to your machine.
- Install dependencies:

```bash
scripts/install
```

- When you're ready to have your work reviewed, [open a pull request!](https://github.com/tartiflette/tartiflette-asgi/compare) :rocket:

## Testing and linting

You can run code auto-formatting using:

```shell
scripts/lint
```

To run the test suite and code checks, run:

```shell
scripts/test
```

If this step passes, you should be on track to pass CI.

You can run code checks separately using:

```shell
scripts/check
```

## Documentation

Documentation pages are located in the `docs/` directory.

If you'd like to preview changes, you can run the documentation site locally using:

```shell
scripts/serve
```

## Notes to maintainers

To make a new release:

- Create a PR with the following:
  - Bump the package version by editing `__version__` in `__init__.py`.
  - Update the changelog with any relevant PRs merged since the last version: bug fixes, new features, changes, deprecations, removals.
- Get the PR reviewed and merged.
- Once the release PR is reviewed and merged, create a new release on the GitHub UI, including:
  - Tag version, like `0.11.0`.
  - Release title, `Version 0.11.0`.
  - Description copied from the changelog.
- Once created, the release tag will trigger a 'publish' job on CI, automatically pushing the new version to PyPI.
