:::{important}
Opening this repository in VSCode may run a setup script on folder open if you trust the workspace (see [detailed automatic task conditions](#conditions-in-which-vscode-automatic-tasks-run)). You may [disable this behavior](#disable-automatic-tasks-in-vscode) or choose to [contribute from a Dev Container or Codespace](#contribute-from-a-dev-container-or-codespace) instead.
:::

# Contributing

Thank you for considering contributing to `keithley_daq`! No contribution is too small, even if you are just submitting a Pull Request through the GitHub UI to fix some typos or clarify our language! Before attempting larger changes, please [discuss it with us](<https://github.com/nminaian/keithley_daq/discussions/new?category=q-a>) or participate in the relevant [issue](<https://github.com/search?q=repo%3Anminaian/keithley_daq&type=issues>) topic.

This guide gives the high-level details needed for you to jump right in, but links to more detail throughout. And remember, [we're always learning](#were-always-learning)!

## Overview

This guide consists of the following:

- [We're always learning](#were-always-learning): Some context for new and experienced contributors alike.
- [Workflow](#workflow): A high-level overview of the contribution process.
- [Checks](#checks): Checks applied during `pre-commit` and in continuous integration (CI).
- [Code](#code): This project's code style and the tools that help you to maintain it.
- [Tests](#tests): Guidance on running, writing, and adding tests.
- [Documentation](#documentation): Details on documentation.
- [First-time setup](#first-time-setup): Instructions for setting up a brand new machine from scratch.
- [Appendix](#appendix): More detail on concepts and terminology linked to throughout this guide.

## We're always learning

You already know that no contribution is too small, but also, no question is too small! We are here to help you contribute, so feel free to reach out with [questions](<https://github.com/nminaian/keithley_daq/discussions/new?category=q-a>) or submit your Pull Request as a "Draft" and mention (`@`) one of us if you need help along the way.

If you want to contribute but aren't sure where to start, chime in on any [good first issues](<https://github.com/nminaian/keithley_daq/?q=is%3Aissue+is%3Aopen+sort%3Aupdated-desc+label%3A%22good+first+issue%22>) (or any issue) that interests you and we'll point you in the right direction! And remember that it's natural to experience some anxiety or or discomfort during this process. If you're new to contributing, you may be learning all of these things at once:

- How to interact with maintainers (strangers?!).
- How to write Python code.
- How to work with tooling (What are all these squiggly underlines?).
- How to test your code (Wait, you write Python code to test Python code?).
- How to write documentation (I've got to learn Markdown as well?).
- How to set up your machine.
- And more...

This project and its guide are set up to smooth out that learning curve for you a little bit, but if you get lost somewhere along the way, remember that no question is too small!

## Workflow

> [!IMPORTANT]
> Project tooling requires installation of [cross-platform PowerShell](#cross-platform-powershell). This guide also features VSCode-specific instruction, but you are not required to use VSCode to contribute. The decision to organize around a single IDE and shell enables the cross-platform, beginner-friendly contributing experience.

To make a new contribution, fork this repository, clone it, switch to a new branch (please don't commit directly to `main`), run [`scripts/Sync-Py.ps1`](<https://github.com/nminaian/keithley_daq/blob/main/scripts/Sync-Py.ps1>), make changes, commit and push them, and open a Pull Request targeting `main`. You may also open a draft Pull Request if you want feedback before your branch is ready to merge, but remember to mention (`@`) us. In more detail:

- Perform first-time setup, including installing [cross-platform PowerShell](#cross-platform-powershell) and Python 3.11 [(details)](#first-time-setup).
- Fork the repository by selecting "Fork" near the top-right corner of the project page on GitHub. Clone your fork and open it locally, e.g. in VSCode [(details)](#fork-and-clone).
- If using VSCode, consider installing the recommended extensions when prompted [(details)](#installing-recommended-extensions-in-vscode).
- Create a new branch and switch to it, e.g. `git checkout -b my-new-feature` or in VSCode or select `+` in the GitLens branches view ([Palette: `GitLens: Show Branches View`](#vscode-command-palette)).
- If not already run automatically, run [`scripts/Sync-Py.ps1`](<https://github.com/nminaian/keithley_daq/blob/main/scripts/Sync-Py.ps1>) to [set up your contribution environment](#contribution-environment-sync).
- If using VSCode, respond `Yes` when prompted to select the virtual environment for your workspace, or select it later [(details)](#set-your-python-interpreter).
- Make changes, commit, and push them. [(details)](#making-changes).
  - Follow [code](#code) style and ensure changes pass [checks](#checks).
  - Write [tests](#tests) for all code changes.
  - Update [documentation](#documentation) for all code changes.
- Consider updating [the changelog](changelog.md) for any changes that are relevant to those using this library.
- Open a Pull Request targeting `main`. Feel free to open a Draft Pull Request if needed, mentioning (`@`) someone with any questions.
- Ensure CI [checks](#checks) pass.

## Checks

Code and documentation style is checked with `pre-commit` and in continuous integration (CI) when you submit a Pull Request. Please ask [a question](<https://github.com/nminaian/keithley_daq/discussions/new?category=q-a>) if you are having trouble passing local `pre-commit` checks. `pyright` checks Python type annotations, `ruff` checks and formats code, `markdownlint-cli2` chcks and formats Markdown, and `fawltydeps` checks dependencies. VSCode is configured to auto-format on save, and certain tools will automatically apply fixes on save. See the [contributor tools guide](#contributor-tools-guide) for more detail on interactive tool usage in VSCode.

> [!IMPORTANT]
> If `pre-commit` fails while committing with the VSCode UI, it will throw up a dialog with a scary red "X" and an unhelpful message. Always select `Show Command Output` in this dialog and search for `failed` in the resulting window with `Ctrl+F`. Alternatively, run the [`pre-commit` VSCode Task](#run-a-vscode-task) to get color-coded feedback in the terminal instead.

While `pre-commit` will run all necessary checks, manual checks for individual tools may be run from the command-line interface (CLI) and have the following VSCode interactions:

- `pre-commit` and the [`pre-commit` VSCode Task](#run-a-vscode-task).
- `pyright` and in the VSCode problems pane.
- `ruff check .; ruff format .` and in the VSCode problems pane and the [`task: Run ruff` VSCode Task](#run-a-vscode-task).
- `markdownlint-cli2` and in the VSCode problems pane.
- `fawltydeps` or e.g. `fawltydeps --config-file docs/pyproject.toml`.
- `sourcery review --fix --diff 'git diff main'` and VSCode problems pane [(optional)](#sourcery).

## Code

To be continued...

## Tests

This project uses `pytest` to test the `keithley_daq` code in `src`.

## Documentation

This project mostly follows the [`numpydoc` docstring standard](https://numpydoc.readthedocs.io/en/latest/format.html#docstring-standard), with minor variations enforced by `ruff`. Notable deviations are:

- Use the imperative mood in the one-line summary, and you can usually omit the article ("a", "an", "the") on nouns in the one-line summary.
- Simple functions may only need a one-line summary, or a one-line summary and an extended summary.
- Don't include types in parameters sections.
- Never include an "Other Parameters" section.
- Outside of `numpydoc`-styled sections, write simple paragraphs and use [MyST Markdown](https://myst-parser.readthedocs.io/en/stable/index.html) sparingly as needed.
- Avoid too much fancy formatting in the docstring, it should read well in plain text.

```Python
def say_hello(name: str, family: bool = False) -> str:
    """Greet guest.

    If the guest is a family member, greet them warmly.

    Parameters
    ----------
    name
      The name of the guest.
    family
      Whether the guest is a family member.
    """
    ...
```

## Contributor tools guide

This guide details VSCode-specific tool usage. The following technqiuqes are facilitated by project tools:

<!-- no toc -->
- [Learn gradually from immediate feedback](#learn-gradually-from-immediate-feedback)
- [Check dependencies with `fawltydeps`](#check-dependencies-with-fawltydeps)
- [Keep track of expected data types](#keep-track-of-expected-data-types)
- [Check and format Markdown documentation](#check-and-format-markdown-documentation)
- [Automate tedium every time you save the file](#automate-tedium-every-time-you-save-the-file)
- [Debug your code with VSCode debug configurations](#debug-your-code-with-vscode-debug-configurations)
- [Reduce friction and typos with refactoring](#reduce-friction-and-typos-with-refactoring)

### Learn gradually from immediate feedback

If you're editing files in VSCode, certain tools give feedback by placing squiggly underlines under problem areas. These are also shown in the Problems pane ([Palette: `View: Focus Problems`](#vscode-command-palette)). Interact with these warnings clicking the lightbulb that appears near your cursor or by pressing `Ctrl+.`. You can often click links in the Problems pane for more details.

Tools like `ruff`, `pyright`, `markdownlint-cli2`, and [`sourcery`](#sourcery) gently nudge us towards writing better code by bringing up things we might not have even known to search for. In VSCode, we can press `Ctrl+.` (or select the floating lightbulb) and interact with such warnings. You may invoke `pyright` at the command line or use [Pylance](https://marketplace.visualstudio.com/items?itemName=ms-python.vscode-pylance) in VSCode, which uses `pyright` to provide squiggly underlines for incorrect type annotations in code.

#### Sourcery

The `sourcery` tool is only applied in CI. You may optionally use it locally, but since it requires a (free) individual account, you are not required to do so. This tool is recommended for Python learners, as it rewrites code in logically-equivalent but usually shorter or more idiomatic ways, giving a rationale for the change.

> [!IMPORTANT]
> If you optionally choose to use `sourcery` in VSCode, you do not need to click `Opt-In` during on-boarding step. This project disables the generative AI-powered features of `sourcery`, and instead uses only its basic refactoring rules.

[back](#contributor-tools-guide)

### Check dependencies with `fawltydeps`

The `fawltydeps` tool ensures that all Python dependencies in use are declared, and that all declared dependencies are used. The various `pyproject.toml` files in this project correspond to the package itself (the root `pyproject.toml`) as well as documentation, scripts/tooling, and testing packages defined in the `docs`, `scripts`, `tests` subfolders, respectively. If your changes modify dependencies, add the appropriate dependencies to the appropriate `pyproject.toml` file.

[back](#contributor-tools-guide)

### Keep track of expected data types

Pylance uses `pyright` to look for issues with the "types" of variables passing through code. But how does Pylance know what "type" a certain variable should be? We can use "type annotations" to tell it what type we *want* a variable to have. For instance the first parameter in the `do_something_fancy` function signature is `an_argument: int`, where `an_argument` is the name of that first argument, and `int` is the type that we *want* it to be.

Python won't *guarantee* that `an_argument` is an `int`, but Pylance will warn us if we try to pass something else in. Try passing a non-integer to `do_something_fancy`. This is useful for catching bugs early, and for documenting our code. We also see from the `-> float` annotation that `do_something_fancy` should return a `float`.

We can even "reveal" the expected types of things by holding down the `Ctrl+Alt` keys. We can see a ghostly `: float` appear next to the `result` variable in the `main()` function body. This tells us that Pylance has inferred `result` to be a floating point number.

You can interact with Pylance underlines much in the same way as you do with Ruff, the lightbulb or `Ctrl+.` will let you interact with them.

[back](#contributor-tools-guide)

### Check and format Markdown documentation

This template configures the [Markdownlint](https://marketplace.visualstudio.com/items?itemName=DavidAnson.vscode-markdownlint) and [Markdown All-in-One](https://marketplace.visualstudio.com/items?itemName=yzhang.markdown-all-in-one) extensions to help you in writing [Markdown](https://www.markdownguide.org/) documentation. It's a simple text format that automatically renders to HTML in Gists and elsewhere. Select the preview icon in the tab bar when modifying a Markdown document to get a live preview, formatted to look like GitHub Markdown by [this extension](https://marketplace.visualstudio.com/items?itemName=bierner.markdown-preview-github-styles).

[back](#contributor-tools-guide)

### Automate tedium every time you save the file

You may have noticed some spacing changes whenver you save the file. This is happening because we have enabled auto-formatting on save in `.vscode/settings.json`. This is also the case in notebooks. Whenever you save a Python file, `ruff` will automatically format it, check for stylistic issues, and fix some of them automatically. With auto-formatting, you'll find yourself writing longer bits of code that may run long, but a quick `Ctrl+S` will format it neatly. Still, try to avoid packing *too much* code into one statement.

[back](#contributor-tools-guide)

### Debug your code with VSCode debug configurations

The configurations in `.vscode/launch.json` enable you to run your code in debug mode, that is, to freeze in the middle of executing your code and analyze local state. See VSCode's [Python debugging guide](https://code.visualstudio.com/docs/python/debugging) for details, but in short, you can debug your code by clicking in the "gutter" (to the left of the line number) to place a breakpoint, then press `F5` or select the drop-down arrow next to the "play button" in the tab strip and select `Debug Python file`. The bundled debug configuration redirects output to the `Debug Console` pane, so all commands run there will receive input there, as opposed to the default configuration where output is echoed to the `Terminal` pane.
[back](#contributor-tools-guide)

### Reduce friction and typos with refactoring

It is easy to make mistakes whenever you copy/paste/modify. We can use our IDE's "refactoring" tools instead, like Pylance in VSCode, to reduce the frequency of error-prone copy/paste/modify operations. Renaming functions or variables (collectively called "symbols"), bundling related bits of code into functions, or moving logic across files is part of a process called "refactoring". In VSCode, these tools are accessible via a contextual floating lightbulb that appears near your cursor which can be triggered by selecting it or pressing `Ctrl+.`. Consider trying out some of these tools next time you're writing code:

#### Import symbols automatically when you need them

In order to use `pi` from Python's `math` module, you need to type `from math import pi` at the top of the file, then use `pi` in your code. Instead, just start typing `pi` the first time you want to use it, then select the appropriate entry from the drop-down menu and press `Tab` to insert it. Pylance will automatically add the necessary `import` statement at the top of the file. You can bring up this drop-down menu with `Ctrl+Space` ([Palette: `Trigger suggest`](#vscode-command-palette)) or see similar import suggestions in the lightbulb menu. This "just works" for most symbols, but you may still need to manually import some things.

#### Move code to other files

Place your cursor in any symbol, click the lightbulb or press `Ctrl+.`, then select `Move symbol to ...` to move it to another file.

#### Rename symbols

Place your cursor in any symbol and click the lightbulb or press `F2` to rename it. You can do this wherever a symbol is defined or used and Pylance will rename it everywhere.

#### Extract code into its own function

As you write code, you may find that certain blocks of code deal only with a few short-lived variables that are not used later on. This block may be a candidate for extraction into its own function. Try highlighting these lines (press `Ctrl+L` repeatedly to select entire lines at a time), click the lightbulb, then click `Extract method...` and name it `do_related_things`.

#### Extract constants

You may find yourself hard-coding a "magic number", e.g. `65535`. It may have some special meaning to you, but the intent is not clear to others. Try renaming `65535`. Highlight it, click the lightbulb, click `Extract variable...`, and name it `MAX_16_BIT_INTEGER`. You may now move this to the top of the file (you'll have to manually cut/paste from here).

[back](#contributor-tools-guide)

## First-time setup

Some basics need installing on a new computer, also useful if you're new to Python and contributing altogether!

If you're on Windows, paste the script detailed in the [first-time setup script for Windows](#first-time-setup-script-for-windows) into a local Windows PowerShell terminal (right-click and select `Run as administrator`). Once Windows Terminal (`wt`) is installed, you may also want to open it from the start menu, click the drop-down arrow, select `Settings`, select `PowerShell` (not `Windows PowerShell`) as your default profile, and consider setting the "default terminal application" to Windows Terminal.

[Workflow](#workflow)

### Create a GitHub account and configure git

Modify the following terminal commands with your GitHub username/email to populate `.gitconfig` in your user folder (e.g. `%USERPROFILE%/.gitconfig` on Windows, `~/.gitconfig` otherwise), so that you can commit changes in VSCode using your GitHub identity.

```PowerShell
git config --global user.name 'yourGitHubUsername'
git config --global user.email 'yourGitHubAssociatedEmail@email.com'
```

- If done correctly, VSCode will prompt you to log in to your GitHub account before pushing changes (a later step in the overall process above).

[back](#first-time-setup)

### Fork and clone

These steps outline the process for cloning your fork locally and opening it in VSCode. In the web UI of your fork, click the green button labelled "Code", select "Local" and "HTTPS". and click the copy icon to copy the resulting URL. Use it to clone your fork locally by clicking `Clone Repository` in a new VSCode window ([Palette: `View: Show Source Control`](#vscode-command-palette)) or ([Palette: `Git: Clone`](#vscode-command-palette))or at the command line. For example:

```PowerShell
git clone '<URL you copied>' '<destination>'
```

If done via the VSCode UI, click `Open` when prompted to open your newly-created Gist in VSCode, or navigate to it in your file explorer and open it in VSCode.

[Workflow](#workflow)

### Set your Python interpreter

If you missed your chance on initial setup, you can still set the Python interpreter at any point. This will select the [virtual environment](#virtual-environment) for the workspace folder, and allow your Python scripts to leverage the packages we have installed from `requirements.txt`.

- Open the main script in your Gist, e.g. `example.py`
- Check for `venv` in the bottom-right corner of VSCode, e.g. `3.11.# 64-bit (.venv: venv)`
- If you don't see `venv`, click the version number to select the option with `.venv` in it

[Workflow](#workflow)

## Appendix

### Conditions in which VSCode automatic tasks run

If you have trusted this folder in VSCode or have `security.workspace.trust.enabled` set to `false` in your User `settings.json` and have `task.allowAutomaticTasks` set to `on` in your User `settings.json`, the VSCode Task `setup: Sync contributor environment` automatically runs on folder open and invokes [`scripts/Sync-Py.ps1`](<https://github.com/nminaian/keithley_daq/blob/main/scripts/Sync-Py.ps1>).

### Disable automatic tasks in VSCode

You may disable this behavior by pressing`Ctrl+Shift+P` typing to find the command `Tasks: Manage Automatic Tasks`, selecting it, and selecting `Disallow Automatic Tasks`.

```JSON
"task.allowAutomaticTasks": "on"
```

It should only trigger if you have allowed VSCode Tasks to run automatically and have marked your forked clone of this repository as trusted. If you prefer to contribute with further.

### Cross-platform PowerShell

PowerShell, once a Windows-only system shell, is now supported on Windows, MacOS, and Linux alike. This repository features tooling that sets up the environment with [`scripts/Sync-Py.ps1`](<https://github.com/nminaian/keithley_daq/blob/main/scripts/Sync-Py.ps1>), to be run on cross-platform PowerShell. The contents of [`scripts/Initialize-Shell.ps1`](<https://github.com/nminaian/keithley_daq/blob/main/scripts/Initialize-Shell.ps1>) represents a sort of "profile" for your PowerShell terminal sessions. But you are not required to add it to your user shell profile. Instead, it is explicitly invoked whenever needed, including in other shell scripts, local `pre-commit` hooks and in VSCode Tasks.

However, if you do want to add it to your user shell profile, you may do so by running `code $PROFILE` in `pwsh` after you have installed it, which will open your `pwsh` user profile in VSCode. You may then copy the contents of [`scripts/Initialize-Shell.ps1`](<https://github.com/nminaian/keithley_daq/blob/main/scripts/Initialize-Shell.ps1>) into a conditional statement that checks whether you are in this project's directory (e.g. `keithley_daq`), like so:

```PowerShell
if ((Get-Item '.' | Select-Object -ExpandProperty 'Name') -eq 'keithley_daq') {
  # Paste the contents of `scripts/Initialize-Shell.ps1` here
}
```

[Contributing](#contributing)

### Contribute from a Dev Container or Codespace

This project also supports contributions from a [dev container](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers
) ([Palette: `Dev Containers: Open Folder in Container`](#vscode-command-palette)) or as a [Codespace](https://docs.github.com/en/codespaces/getting-started/quickstart).

### Installing recommended extensions in VSCode

To install workspace-recommended extensions in VSCode, restart ([Palette: `Developer: Reload Window`](#vscode-command-palette)) and click `Yes` when prompted to install recommended extensions when prompted. Otherwise, navigate to Extensions ([Palette: `View: Show Extensions`](#vscode-command-palette)), search for `@recommended`, and click the cloud icon next to `Workspace Recommendations` to install them.

### Making changes

See [this video segment](https://www.youtube.com/watch?v=i_23KUAEtUM&t=76s) for making changes in VSCode, as well as a [brief outline](https://code.visualstudio.com/docs/introvideos/versioncontrol#_video-outline) and [more detail](https://code.visualstudio.com/docs/sourcecontrol/overview).

[Workflow](#workflow)

### Pinning dependencies

If `keithley_daq` depends on `pandas` (for example), it helps if I write down the specific version of `pandas` that this package works with. If I `pip install pandas`, then a specific version of Pandas will be installed, for instance version `2.2.1` at the time of writing. When `import pandas` runs in this package, it uses `pandas` version `2.2.1`. But like any package, `pandas` changes over time, and `pandas` version `2.2.1` installed at the time of writing behaves differently from the version of `pandas` released a year ago or to be released a year from now. I can only guarantee that this package works with the version of `pandas` I'm running right now, so I keep track of that by writing `pandas==2.2.1` in `lock.json`. This is called dependency pinning, which can be done for every dependency of this project, including [transitive dependencies](#transitive-dependency), for different operating systems and different versions of Python! These exact version pins above are good for recreating the exact environment needed by you, a potential contributor to this project!

However, these exact version pins are overly restrictive to those who just want to use `keithley_daq` in their own code. Python environments cannot have multiple versions of `pandas` installed at once. If I install `keithley_daq` using `pip install keithley_daq` with no other qualifiers, it is retrieved from [PyPI](https://pypi.org/) and the the version metadata defined in `pyproject.toml` is used to decide which packages to install alongside it. If `keithley_daq` depends on `pandas==2.2.1` as specified in `pyproject.toml`, and I try to install something else alongside it that doesn't support `pandas` version `2.2.1`, Python will refuse to install it! I want `keithley_daq` to coexist to the greatest degree possible with other projects, so I list `pandas>=2.2.1` in `pyproject.toml` instead.

Specifying `>=` may be seen as a promise that this version of `keithley_daq` will work with any new release of `pandas`, which I couldn't possibly know for sure. But it's a better alternative to specifying `pandas>=2.2.1,<3`, because the `<3` upper-bound will not allow this package to coexist in any Python environment with another package in that requires `pandas>=3.0.0` in the future. Upper-bound restrictions like `<3` would make `keithley_daq` eventually hostile to usage alongside other packages. This is because a project that depends on this package inherits `pandas>=2.2.1,<3` as a [transitive dependency](#transitive-dependency) specification, and there is no recourse for overriding it. If a new version of `pandas` must be restricted in the course of development of this package, it should be specified like `pandas>=2.2.1,!=3.0.0` at the time of breakage, and changes should be made to allow removing the `!=3.0.0` restriction as soon as possible.

In short, in Python dependency specifications, `<3` doesn't have the same heart-shaped connotation it might have as an emoji! I pin exact dependencies to ensure working environments for potential contributors across operating systems, but specify only lower bounds with short-lived `!=` exclusions in the distribution of this package to PyPI.

[Workflow](#workflow)

### System Python environment

Depending on my OS, I use "system Python environment" or just "system Python" to refer to the version of Python already installed on my machine and the set of packages installed and usable by that Python installation. I also use "system Python" to refer to versions of Python manually installed, for instance from <https://www.python.org/>. This differentiates Python environments installed and expected to be used across the entire machine from [virtual environments](#virtual-environment) to be used for specific projects.

[Workflow](#workflow)

### Contribution environment sync

This repository features tooling that bootstraps the entire development environment with [`scripts/Sync-Py.ps1`](<https://github.com/nminaian/keithley_daq/blob/main/scripts/Sync-Py.ps1>), to be run on [cross-platform PowerShell](#cross-platform-powershell), and the contribution workflow is tested on Windows, Ubuntu, and MacOS 13. If on Windows, you may need to complete `Task 1` in [this guide](https://denisecase.github.io/windows-setup/) to allow scripts to run. [`scripts/Sync-Py.ps1`](<https://github.com/nminaian/keithley_daq/blob/main/scripts/Sync-Py.ps1>) ([Task: `setup: Sync contributor environment`](#run-a-vscode-task)). The [`scripts/Sync-Py.ps1`](<https://github.com/nminaian/keithley_daq/blob/main/scripts/Sync-Py.ps1>) script essentially does the following:

- Sets some environment variables and error handling.
- Installs [`uv`](https://github.com/astral-sh/uv).
- Creates a virtual environment.
- Syncs submodules.
- Syncs a Python [virtual environment](#virtual-environment) to platform-specific dependencies in `lock.json`.
- Installs pre-commit hooks.
- Conditionally runs setup specific to CI or Dev Containers.

[Workflow](#workflow)

### Run a VSCode task

This project defines VSCode Tasks ([Palette: `Tasks: Run task`](#vscode-command-palette)) defined in `.vscode/tasks.json` that run some common actions:

- `setup: Sync contributor environment`: Run the [contribution environment sync](#contribution-environment-sync) script.
- `pre-commit`: Trigger `pre-commit` on your staged changes.
- `git: Rebase back to fork`: Trigger an interactive rebase of commits made to a feature branch
- `task: Run pytest with coverage`: Generates a local coverage report for review with `coverage report` or for local gutter highlights with the [Coverage Gutters VSCode extension](https://marketplace.visualstudio.com/items?itemName=ryanluker.vscode-coverage-gutters).
- `task: sphinx-autobuild docs (preview)`: Build and serve the documentation locally for previewing. `Ctrl+click` on the displayed IP `http://127.0.0.1:8000` (points to `localhost`) in the terminal to preview documentation live as you make changes.
- `task: profile this file`: Profile the currently open Python file with `cProfile`.
- `task: view profile results with snakeviz`: View the results of the latest profiling run.

You may choose to bind `Tasks: Run task` command to a keyboard shortcut of your choice ([Palette: `Preferences: Open Keyboard Shortcuts`](#vscode-command-palette)) or modify `keybindings.json` directly with the similar `(JSON)`-suffixed command. For example, consider the following entries in `keybindings.json`:

```JSON
{
  // ...
  // Bind `Ctrl+Shift+Z` to `Tasks: Run task`
  {
    "key": "ctrl+shift+z",
    "command": "workbench.action.tasks.runTask"
  },
  // Unbind conflicting key for "redo" (it's already on Ctrl+Y)
  {
    "key": "ctrl+shift+z",
    "command": "-redo"
  },
  // ...
}
```

### Some less-common tasks

The following tasks are less-commonly needed, used mostly by maintainers, or can otherwise be disruptive by triggering lots of changes across the project:

- `pre-commit: all`: Trigger `pre-commit` on all tracked files. Run this if making rule changes in tooling or when tool behavior changes (e.g. `ruff`, `markdownlint-cli2`).
- `task: Run ruff`: Check and format all files with `ruff`. Run this whenever an update to `ruff` or its rules causes a behavior change.
- `setup: Sync with template`: Sync the project with its template, generally only used by maintainers and when bumping versions.
- `setup: Perform first-time setup`: Usually only run after the very first commits of a project.
- `setup: Remove *.rej`: Clean up `.rej` files sometimes left behind by template sync.

### Transitive dependency

[back](#first-time-setup)

### Virtual environment

In the context of Python development, a [virtual environment](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments) represents an isolated installation of Python, usually in a `.venv` folder in the working directory.

Say you have installed `pandas` with some variation of `pip install pandas`. `pandas` It is important to use a virtual environment because if you use a Python package (e.g. `import pandas`) that you have installed (e.g. ), your code implicitly depends on the version of `pandas`

It is important to create and use a virtual environment for each of your Python projects

[back](#first-time-setup)

### VSCode command palette

A searchable list of commands in VSCode, by default accessible by pressing `Ctrl+Shift+P` and beginning to type the desired command. Command search is case-insensitive and fairly forgiving.

[back](#first-time-setup)

### Inspiration for this contributing guide

I've gradually built up the tooling and documentation for this project and others in the [`blakeNaccarato/copier-python`](https://github.com/blakeNaccarato/copier-python) project template. In a push to finish up this guide, I've also reviewed other contributing guides to integrate some more best practices. If you're looking for a modern, slim, effective contribution guide, it's a safe bet that Hynek's [latest project](https://github.com/hynek/svcs) represents the latest best practices! Since the goals of this project's contributor experience is to bundle lots of helpful resources to accelerate learning, this guide is somewhat more verbose. Also, this project's templates are inspired by those over at [`obsidian-tasks-group/obsidian-tasks`](https://github.com/obsidian-tasks-group/obsidian-tasks).

[back](#first-time-setup)

### First-time setup script for Windows

This script invokes [Windows package manager](https://apps.microsoft.com/store/detail/app-installer/9NBLGGH4NNS1) (`winget`) from your system's built-in PowerShell to install [cross-platform PowerShell](#cross-platform-powershell) and other tools needed for contribution to this project. Run your system's built-in PowerShell (not ISE) as administrator by searching for it in Start, right-clicking and selecting `Run as administrator`. Copy-paste the following script into the terminal window and run it. This script runs a series of `winget` commands and ensures Windows Terminal is installed.

[back](#first-time-setup)

```PowerShell
<#.SYNOPSIS
One-time setup for Python dev tools on Windows. Installs Python, VSCode, Windows Terminal, PowerShell, and Git.
#>

# Install Python
winget install --id 'Python.Python.3.11' --override '/quiet PrependPath=0'
# Install VSCode
winget install --id 'Microsoft.VisualStudioCode'
# Install Windows Terminal
winget install --id 'Microsoft.WindowsTerminal'

# Install cross-platform PowerShell
winget install --id 'Microsoft.PowerShell' --override '/quiet ADD_EXPLORER_CONTEXT_MENU_OPENPOWERSHELL=1 ADD_FILE_CONTEXT_MENU_RUNPOWERSHELL=1 ADD_PATH=1 ENABLE_MU=1 ENABLE_PSREMOTING=1 REGISTER_MANIFEST=1 USE_MU=1'

# Install git
@'
[Setup]
Lang=default
Dir=C:/Program Files/Git
Group=Git
NoIcons=0
SetupType=default
Components=ext,ext\shellhere,ext\guihere,gitlfs,assoc,assoc_sh,autoupdate,windowsterminal,scalar
Tasks=
EditorOption=VisualStudioCode
CustomEditorPath=
DefaultBranchOption=main
PathOption=Cmd
SSHOption=OpenSSH
TortoiseOption=false
CURLOption=OpenSSL
CRLFOption=CRLFAlways
BashTerminalOption=MinTTY
GitPullBehaviorOption=Merge
UseCredentialManager=Enabled
PerformanceTweaksFSCache=Enabled
EnableSymlinks=Disabled
EnablePseudoConsoleSupport=Disabled
EnableFSMonitor=Enabled
'@ | Out-File ($inf = New-TemporaryFile)
winget install --id 'Git.Git' --override "/SILENT /LOADINF=$inf"

```

[back](#first-time-setup)
