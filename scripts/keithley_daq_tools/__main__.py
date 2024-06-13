"""CLI for tools."""

from collections.abc import Collection
from pathlib import Path
from re import finditer

from cyclopts import App

from keithley_daq_tools.sync import check_compilation, escape

APP = App(help_format="markdown")
"""CLI."""


def main():  # noqa: D103
    APP()


@APP.command
def compile(high: bool = False):  # noqa: A001
    """Compile."""
    log(check_compilation(high))


@APP.command
def get_actions():
    """Get actions used by this repository.

    For additional security, select "Allow <user> and select non-<user>, actions and
    reusable workflows" in the General section of your Actions repository settings, and
    paste the output of this command into the "Allow specified actions and reusable
    workflows" block.

    Parameters
    ----------
    high
        Highest dependencies.
    """
    actions: list[str] = []
    for contents in [
        path.read_text("utf-8") for path in Path(".github/workflows").iterdir()
    ]:
        actions.extend([
            f"{match['action']}@*,"
            for match in finditer(r'uses:\s?"?(?P<action>.+)@', contents)
        ])
    log(sorted(set(actions)))


def log(obj):
    """Send object to `stdout`."""
    match obj:
        case str():
            print(obj)
        case Collection():
            for o in obj:
                log(o)
        case Path():
            log(escape(obj))
        case _:
            print(obj)


if __name__ == "__main__":
    main()
