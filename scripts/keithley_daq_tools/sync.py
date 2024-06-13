"""Sync tools."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from json import dumps, loads
from pathlib import Path
from platform import platform
from re import finditer
from shlex import quote, split
from subprocess import run
from sys import version_info
from typing import Self

from keithley_daq_tools.types import (
    Lock,
    Op,
    Platform,
    PythonVersion,
    SubmoduleInfoKind,
    ops,
)


@dataclass
class Dep:
    """Dependency."""

    op: Op
    """Operator."""
    rev: str
    """Revision."""


# ! For local dev config tooling
PYTEST = Path("pytest.ini")
"""Resulting pytest configuration file."""

# ! Dependencies
COPIER_ANSWERS = Path(".copier-answers.yml")
"""Copier answers file."""
PYTHON_VERSIONS_FILE = Path(".python-versions")
"""File containing supported Python versions."""
REQS = Path("requirements")
"""Requirements."""
UV = REQS / "uv.in"
"""UV requirement."""
DEV = REQS / "dev.in"
"""Other development tools and editable local dependencies."""
OVERRIDES = REQS / "override.txt"
"""Overrides to satisfy otherwise incompatible combinations."""
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
NODEPS = REQS / "nodeps.in"
"""Path to dependencies which should not have their transitive dependencies compiled."""

# ! Platforms and Python versions
SYS_PLATFORM: Platform = platform(terse=True).casefold().split("-")[0]  # pyright: ignore[reportAssignmentType] 1.1.356
"""Platform identifier."""
SYS_PYTHON_VERSION: PythonVersion = ".".join([str(v) for v in version_info[:2]])  # pyright: ignore[reportAssignmentType] 1.1.356
"""Python version associated with this platform."""
PROJECT_PLATFORM: Platform = "linux"
"""This project's default compilation platform."""
PROJECT_PYTHON_VERSION: PythonVersion = "3.11"
"""This project's default Python version."""
PLATFORMS: tuple[Platform, ...] = ("linux", "macos", "windows")
"""Supported platforms."""
PYTHON_VERSIONS: tuple[PythonVersion, ...] = (
    tuple(PYTHON_VERSIONS_FILE.read_text("utf-8").splitlines())  # pyright: ignore[reportArgumentType] 1.1.356
    if PYTHON_VERSIONS_FILE.exists()
    else ("3.9", "3.10", "3.11", "3.12")
)
"""Supported Python versions."""


def check_compilation(high: bool = False) -> str:
    """Check compilation, re-lock if incompatible, and return the requirements."""
    if (
        high
        or not get_lockfile(high).exists()
        or not loads(get_lockfile(high).read_text("utf-8"))
    ):
        return lock(high)
    old_compiler = Compiler.from_lock()
    if Compiler() != old_compiler:
        return lock()
    old_proj_compilation = Compilation.from_lock()
    proj_compilation = Compiler(high=high, no_deps=True).compile()
    if proj_compilation.directs != old_proj_compilation.directs:
        return lock()
    return Compilation.from_lock(
        platform=SYS_PLATFORM, python_version=SYS_PYTHON_VERSION
    ).requirements


def lock(high: bool = False) -> str:
    """Lock."""
    proj_compiler = Compiler(
        platform=PROJECT_PLATFORM, python_version=PROJECT_PYTHON_VERSION, high=high
    )
    proj_compilation = proj_compiler.compile()
    sys_compiler = Compiler(
        platform=SYS_PLATFORM, python_version=SYS_PYTHON_VERSION, high=high
    )
    sys_compilation = (
        proj_compilation
        if proj_compiler == sys_compiler
        else sys_compiler.compile(directs=proj_compilation.directs)
    )
    contents: Lock = {}
    contents["direct"] = {}
    contents["direct"]["time"] = proj_compilation.time.isoformat()
    contents["direct"]["uv"] = proj_compiler.uv
    contents["direct"]["project_platform"] = proj_compiler.platform
    contents["direct"]["project_python_version"] = proj_compiler.python_version
    contents["direct"]["no_deps"] = proj_compiler.no_deps
    contents["direct"]["high"] = proj_compiler.high
    contents["direct"]["paths"] = tuple(p.as_posix() for p in proj_compiler.paths)
    contents["direct"]["overrides"] = proj_compiler.overrides.as_posix()
    contents["direct"]["directs"] = {
        k: asdict(v) for k, v in proj_compilation.directs.items()
    }
    contents["direct"]["requirements"] = "\n".join([
        f"{name}{dep.op}{dep.rev}" for name, dep in proj_compilation.directs.items()
    ])
    for plat in sorted(PLATFORMS):
        for python_version in sorted(PYTHON_VERSIONS):
            compiler = Compiler(platform=plat, python_version=python_version, high=high)
            compilation = compiler.compile(directs=proj_compilation.directs)
            key = compiler.get_lockfile_key()
            contents[key] = {}
            contents[key]["time"] = compilation.time.isoformat()
            contents[key]["requirements"] = compilation.requirements
    get_lockfile(high).write_text(
        encoding="utf-8", data=dumps(indent=2, obj=contents) + "\n"
    )
    return sys_compilation.requirements


def get_lockfile_key(platform: Platform, python_version: PythonVersion) -> str:
    """Get the name of a dependency compilation.

    Parameters
    ----------
    platform
        Platform to compile for.
    python_version
        Python version to compile for.
    high
        Highest dependencies.
    """
    return "_".join([platform, python_version])


def get_lockfile(high: bool) -> Path:
    """Get lockfile path."""
    return Path(f"lock{'-high' if high else ''}.json")


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
    platform: Platform = PROJECT_PLATFORM
    """Platform compiled for."""
    python_version: PythonVersion = PROJECT_PYTHON_VERSION
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
            "--exclude-newer",
            time.isoformat().replace("+00:00", "Z"),
            "--python-platform",
            self.platform,
            "--python-version",
            self.python_version,
            "--resolution",
            "highest" if self.high else "lowest-direct",
            "--override",
            escape(self.overrides),
            "--all-extras",
            *(["--no-deps"] if self.no_deps else []),
            *[escape(path) for path in self.paths],
        ]

    def get_lockfile_key(self) -> str:
        """Get lockfile key."""
        return get_lockfile_key(self.platform, self.python_version)

    def compile(
        self, time: datetime = datetime.min, directs: dict[str, Dep] | None = None
    ) -> Compilation:
        """Compile dependencies."""
        return Compilation(compiler=self, time=time, directs=directs or get_directs())

    @classmethod
    def from_lock(
        cls,
        platform: Platform | None = None,
        python_version: PythonVersion | None = None,
        high: bool = False,
    ) -> Self:
        """Get locked project compiler."""
        contents = loads(get_lockfile(high).read_text("utf-8"))
        return cls(
            uv=contents["direct"]["uv"],
            platform=platform or contents["direct"]["project_platform"],
            python_version=(
                python_version or contents["direct"]["project_python_version"]
            ),
            high=contents["direct"]["high"],
            no_deps=(
                contents["direct"]["no_deps"] if platform and python_version else False
            ),
            overrides=Path(contents["direct"]["overrides"]),
            paths=tuple(Path(p) for p in contents["direct"]["paths"]),
        )


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

    @classmethod
    def from_lock(
        cls,
        platform: Platform | None = None,
        python_version: PythonVersion | None = None,
        high: bool = False,
    ) -> Self:
        """Get locked project compiler."""
        contents = loads(get_lockfile(high).read_text("utf-8"))
        if platform and python_version:
            compiler = Compiler.from_lock(
                platform=platform, python_version=python_version, high=high
            )
            key = compiler.get_lockfile_key()
        else:
            key = "direct"
            compiler = Compiler.from_lock()
        return cls(
            compiler=compiler,
            time=contents[key]["time"],
            requirements=(reqs := contents[key]["requirements"]),
            directs=get_directs(reqs),
        )


def compile(compiler: Compiler) -> tuple[datetime, str]:  # noqa: A001
    """Compile dependencies."""
    time, cmd = compiler.get_command()
    result = run(args=cmd, capture_output=True, check=False, text=True)
    if result.returncode:
        raise RuntimeError(result.stderr)
    requirements = (
        "\n".join([
            "# nodeps",
            *[line.strip() for line in NODEPS.read_text("utf-8").splitlines()],
            "# compilation",
            result.stdout,
        ])
        + "\n"
    )
    return time, requirements


def get_subs() -> dict[str, Dep]:
    """Get submodules."""
    subs = dict(
        zip(get_submodule_info("paths"), get_submodule_info("urls"), strict=True)
    )
    revs = {
        item[1]: item[0]
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
