"""Sync tools."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from json import dumps, loads
from pathlib import Path
from re import finditer
from shlex import quote, split
from subprocess import run
from sys import version_info
from typing import TYPE_CHECKING

from keithley_daq_tools.types import Dep, PythonVersion, SubmoduleInfoKind, ops

if version_info >= (3, 11):  # noqa: UP036, RUF100
    from datetime import UTC  # pyright: ignore[reportAttributeAccessIssue]
else:
    from datetime import timezone  # pyright: ignore[reportPossiblyUnboundVariable]

    UTC = timezone.utc  # noqa: UP017, RUF100

if TYPE_CHECKING:
    UTC: timezone

MINIMUM_PYTHON = "3.11"
"""This project's default Python version."""

# ! Dependencies
REQS = Path("requirements")
"""Requirements."""
DEV = REQS / "dev.in"
"""Other development tools and editable local dependencies."""
DEPS = (
    DEV,
    *[
        Path(editable["path"]) / "pyproject.toml"
        for editable in finditer(
            r"(?m)^(?:-e|--editable)\s(?P<path>.+)$", DEV.read_text("utf-8")
        )
    ],
)
"""Paths to compile dependencies for."""
OVERRIDES = REQS / "override.txt"
"""Overrides to satisfy otherwise incompatible combinations."""
NODEPS = REQS / "nodeps.in"
"""Path to dependencies which should not have their transitive dependencies compiled."""
REQUIREMENTS = REQS / "requirements.txt"
"""Requirements."""


@dataclass
class Lock:
    """Lockfile."""

    time: str
    uv: str
    minimum_python: PythonVersion
    paths: tuple[str, ...]
    overrides: str
    directs: dict[str, Dep]
    direct_requirements: str
    requirements: str


def check_compilation(high: bool = False) -> str:
    """Check compilation, re-lock if incompatible, and return the requirements."""
    if high:
        return lock(high=high)
    lockfile = get_lockfile()
    if not lockfile.exists():
        return lock()
    contents = loads(lockfile.read_text("utf-8"))
    if not contents:
        return lock()
    locked = Lock(**contents)
    if Compiler() != Compiler(
        uv=locked.uv,
        overrides=Path(locked.overrides),
        paths=tuple(Path(p) for p in locked.paths),
    ):
        return lock()
    if (new_directs := get_directs()) != locked.directs:
        return lock(directs=new_directs)
    return locked.requirements


def lock(directs: dict[str, Dep] | None = None, high: bool = False) -> str:
    """Lock."""
    compiler = Compiler(high=high)
    compilation = compiler.compile(directs=directs or {})
    contents = Lock(
        time=compilation.time.isoformat(),
        uv=compiler.uv,
        minimum_python=compiler.python_version,
        paths=tuple(p.as_posix() for p in compiler.paths),
        overrides=compiler.overrides.as_posix(),
        directs=compilation.directs,
        direct_requirements="\n".join([
            f"{name}{dep['op']}{dep['rev']}"
            for name, dep in compilation.directs.items()
        ]),
        requirements=compilation.requirements,
    )
    get_lockfile(high).write_text(
        encoding="utf-8", data=dumps(indent=2, obj=asdict(contents)) + "\n"
    )
    if not high:
        REQUIREMENTS.write_text(encoding="utf-8", data=contents.requirements)
    return compilation.requirements


def get_uv_version() -> str:
    """Get version of `uv` at `bin/uv`."""
    result = run(
        args=split("bin/uv --version"), capture_output=True, check=False, text=True
    )
    if result.returncode:
        raise RuntimeError(result.stderr)
    return result.stdout.strip().split(" ")[1]


@dataclass
class Compiler:
    """Compiler."""

    uv: str = field(default_factory=get_uv_version)
    """Version of `uv` used to compile."""
    python_version: PythonVersion = MINIMUM_PYTHON
    """Python version compiled for."""
    high: bool = False
    """Highest dependencies."""
    no_deps: bool = False
    """Without transitive dependencies."""
    overrides: Path = OVERRIDES
    """Overrides."""
    paths: tuple[Path, ...] = DEPS
    """Paths compiled from, such as `requirements.in` or `pyproject.toml`."""

    def get_command(self) -> tuple[datetime, list[str]]:
        """Command to reproduce compilation requirements."""
        time = datetime.now(UTC)
        return time, [
            "bin/uv",
            "pip",
            "compile",
            "--universal",
            "--all-extras",
            "--exclude-newer",
            time.isoformat().replace("+00:00", "Z"),
            "--python-version",
            self.python_version,
            "--resolution",
            "highest" if self.high else "lowest-direct",
            "--override",
            escape(self.overrides),
            *(["--no-deps"] if self.no_deps else []),
            *[escape(path) for path in self.paths],
        ]

    def compile(
        self, time: datetime = datetime.min, directs: dict[str, Dep] | None = None
    ) -> Compilation:
        """Compile dependencies."""
        return Compilation(compiler=self, time=time, directs=directs or get_directs())


NAME_PAT = r"[A-Za-z0-9]|[A-Za-z0-9][A-Za-z0-9._-]*[A-Za-z0-9]"
"""Regular expression for a legal Python package name.

See: https://packaging.python.org/en/latest/specifications/name-normalization/#name-format
"""
OP_PAT = "|".join(ops)
"""Regular expression for valid version separators."""


def get_directs(requirements: str | None = None) -> dict[str, Dep]:
    """Get directs."""
    directs: dict[str, Dep] = {}
    if not requirements:
        _, requirements = compile(Compiler(no_deps=True))
    for direct in finditer(
        rf"(?m)^(?P<name>{NAME_PAT})(?P<op>{OP_PAT})(?P<rev>.+)$", requirements
    ):
        op = direct["op"]
        if not isinstance(op, str) or op not in ops:
            raise ValueError(f"Invalid operator in {direct.groups()}")
        directs[direct["name"]] = Dep(op=op, rev=direct["rev"])
    return get_subs() | directs


@dataclass
class Compilation:
    """Compilation."""

    compiler: Compiler = field(default_factory=Compiler)
    """Compiler used to compile."""
    time: datetime = datetime.min
    """Time of compilation."""
    requirements: str = ""
    """Result of compilation."""
    directs: dict[str, Dep] = field(default_factory=get_directs)
    """Direct dependencies and their revisions."""

    def __post_init__(self):
        if self.time == datetime.min or not self.requirements:
            time, requirements = compile(self.compiler)
            self.time = time
            self.requirements = requirements


def get_lockfile(high: bool = False) -> Path:
    """Get lockfile path."""
    return Path(f"lock{'-high' if high else ''}.json")


def compile(compiler: Compiler) -> tuple[datetime, str]:  # noqa: A001
    """Compile dependencies."""
    time, cmd = compiler.get_command()
    result = run(args=cmd, capture_output=True, check=False, text=True)
    if result.returncode:
        raise RuntimeError(result.stderr)
    nodeps = NODEPS.read_text("utf-8").splitlines()
    requirements = "\n".join([
        *(
            ["# nodeps", *[line.strip() for line in nodeps], "# compilation"]
            if nodeps
            else []
        ),
        result.stdout,
    ])
    return time, requirements


def get_subs() -> dict[str, Dep]:
    """Get submodules."""
    subs = dict(
        zip(get_submodule_info("paths"), get_submodule_info("urls"), strict=True)
    )
    revs = {
        item[1]: item[0].removeprefix("+")  # ? Remove `+` in case it's not staged
        for item in (
            item.split()
            for item in run(
                args=split("git submodule"), capture_output=True, check=True, text=True
            ).stdout.splitlines()
        )
    }
    return {
        path.removeprefix("submodules/"): Dep(
            op=" @ ", rev=f"git+{subs[path]}@{revs[path]}"
        )
        for path in subs
        if path not in {"submodules/template", "submodules/typings"}
    }


def get_submodule_info(kind: SubmoduleInfoKind) -> list[str]:
    """Get submodule info."""
    return [
        item.split()[1].removesuffix(".git")
        for item in run(
            args=split(
                f"git config --file .gitmodules --get-regexp {kind.removesuffix('s')}"
            ),
            capture_output=True,
            check=True,
            text=True,
        ).stdout.splitlines()
    ]


def escape(path: str | Path) -> str:
    """Escape a path, suitable for passing to e.g. {func}`~subprocess.run`."""
    return quote(Path(path).as_posix())
