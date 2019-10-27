import pytest


def test_exits_interpreter_with_error_on_import(capsys):
    with pytest.raises(SystemExit) as ctx:
        import tartiflette_starlette  # noqa: F401
    exc = ctx.value
    assert exc.code > 0

    result = capsys.readouterr()
    assert "tartiflette-asgi" in result.out
