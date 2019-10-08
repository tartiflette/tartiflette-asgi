# Contributing guidelines

Thank you for your interest in contributing to this project! Here are some tips to get you started.

1. Consider [opening an issue](https://github.com/tartiflette/tartiflette-starlette/issues/new) if the change you're proposing is not trivial. :+1:
2. Fork this repo and clone it to your machine.
3. Create a virtual environment and install development dependencies:

```bash
python -m venv venv
. venv/bin/activate
pip install -r requirements.txt
```

4. Work on a separate branch, e.g. `fix-some-bug`.
5. Make sure tests pass before pushing your code. To run the test suite, use:

```bash
pytest
```

6. Once the feature or bug fix is ready enough to be reviewed, [open a pull request!](https://github.com/tartiflette/tartiflette-starlette/compare) :rocket:

## Notes to maintainers

To make a new release:

- Bump the version in `__init__.py`.
- Edit the changelog with the set of changes since the last release.
- Create a release commit: `$ git commit -m "Release x.y.z"`.
- Publish to PyPI: `$ scripts/publish`.
- Create a tag: `$ git tag x.y.z`.
- Push to remote: `$ git push --tags`.
