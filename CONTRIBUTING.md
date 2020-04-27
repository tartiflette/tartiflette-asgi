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

- Bump the version in `__init__.py`.
- Edit the changelog with the set of changes since the last release.
- Create a release commit: `$ git commit -m "Release x.y.z"`.
- Run `$ scripts/publish` to push a new release to PyPI and deploy the docs to GitHub Pages.
