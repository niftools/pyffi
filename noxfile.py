import nox

PYTHON_VERSIONS = ["3.10", "3.11", "3.12", "3.13", "3.14"]

nox.options.default_venv_backend = "uv|virtualenv"


@nox.session(python=PYTHON_VERSIONS)
def tests(session):
    """Run all tests."""
    session.run("pytest")