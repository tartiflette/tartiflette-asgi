# Contributing guidelines

Want to contribute to this project? Awesome news! Here are some guidelines to get you started.

**Note**: before writing any code, be sure to [open an issue](https://github.com/florimondmanca/tartiflette-starlette/issues/new) if the change you're proposing is not trivial.

1. Fork this repo and clone it to your machine.
2. Create a virtual environment and install development dependencies:

```bash
python -m venv venv
. venv/bin/activate
pip install -r requirements.txt
```

3. Work on a separate branch, e.g. `fix-some-bug`.
4. Make sure tests pass before pushing your code. To run the test suite, use:

```bash
pytest
```

5. Once the feature or bug fix is ready enough to be reviewed, [open a pull request!](https://github.com/florimondmanca/tartiflette-starlette/compare)
