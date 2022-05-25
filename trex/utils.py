import os
from pathlib import Path
import typer
import json
import random

# local imports
from trex import meta

APP_NAME = meta.APP_NAME
APP_VERSION = meta.APP_VERSION

terminal_width, terminal_height = os.get_terminal_size()


"""
=============================================================
                   DIRECTORY HANDLING
=============================================================
"""

def get_app_dir():
    app_dir = typer.get_app_dir(APP_NAME)
    config_path: Path = Path(app_dir) / "config.json"
    templates_path: Path = Path(app_dir) / "templates.json"
    return Path(app_dir), config_path, templates_path

def check_app_dir():
    dir_path, config_path, templates_path = get_app_dir()
    try:
        os.mkdir(dir_path)
    except FileExistsError:
        pass
    return


"""
=============================================================
                TEMPLATE CONFIG HANDLING
=============================================================
"""

def add_template(name: str, data: dict):
    dir_path, config_path, templates_path = get_app_dir()
    check_app_dir()

    try:
        with open(templates_path, "r") as f:
            stored_config = f.read()
        stored_config = json.loads(stored_config)
    except FileNotFoundError:
        stored_config = {}

    try:
        test_exists = stored_config[name]
        return False
    except KeyError:
        pass

    stored_config[name] = data
    with open(templates_path, "w") as f:
        f.write(json.dumps(stored_config))

    return True


def get_template(name):
    dir_path, config_path, templates_path = get_app_dir()
    check_app_dir()

    try:
        with open(templates_path, "r") as f:
            stored_config = json.loads(f.read())

        if name is None:
            return stored_config
        else:
            return stored_config[name]
    except FileNotFoundError:
        return None
    except KeyError:
        return None


def remove_template(name: str):
    dir_path, config_path, templates_path = get_app_dir()
    check_app_dir()

    try:
        with open(templates_path, "r") as f:
            stored_config = json.loads(f.read())
        stored_config.pop(name)
    except FileNotFoundError:
        return None
    except KeyError:
        return None

    with open(templates_path, "w") as f:
        f.write(json.dumps(stored_config))

    return True




"""
=============================================================
                      CONFIG HANDLING
=============================================================
"""

def add_config(key: str, data):
    dir_path, config_path, templates_path = get_app_dir()
    check_app_dir()

    if key not in meta.config_options:
        return None

    try:
        with open(config_path, "r") as f:
            stored_config = f.read()
        stored_config = json.loads(stored_config)
    except FileNotFoundError:
        stored_config = {}

    stored_config[key] = data
    with open(config_path, "w") as f:
        f.write(json.dumps(stored_config))

    return True


def get_config(key: str):
    dir_path, config_path, templates_path = get_app_dir()
    check_app_dir()

    try:
        with open(config_path, "r") as f:
            stored_config = json.loads(f.read())
        return stored_config[key]
    except FileNotFoundError:
        return None
    except KeyError:
        return None


"""
=============================================================
                      TIP HANDLING
=============================================================
"""

def show_tip(msg: str):
    # only show tips when show_tips is True or doesn't exist
    show_tips = get_config("tips")
    if show_tips is not None and show_tips is False:
        return

    tip_title = typer.style(" TIP ", fg=typer.colors.BLACK, bg=typer.colors.WHITE, bold=True)
    tip = "\n" + tip_title + f" {msg}\n" + "Disable tips with 'trex config tips --disable'\n"
    typer.echo(tip)


"""
=============================================================
                      PRINT HANDLING
=============================================================
"""

def print_start():
    show_intro = get_config("intro")
    if show_intro is not None and show_intro is False:
        return
    working = random.choice(meta.working_strings)
    typer.secho("🦖 " + working, fg=typer.colors.BRIGHT_GREEN)

def print_warn(msg: str):
    warn_title = typer.style(" WARN! ", fg=typer.colors.BRIGHT_YELLOW, bold=True)
    typer.echo(warn_title + " " + msg)

def print_error(msg: str):
    warn_title = typer.style(" ERROR ", fg=typer.colors.BRIGHT_RED, bold=True)
    typer.echo(warn_title + " " + msg)

def print_working(msg: str):
    warn_title = typer.style(" ..... ", fg=typer.colors.BRIGHT_CYAN, bold=True)
    typer.echo(warn_title + " " + msg)

def print_done(msg: str):
    warn_title = typer.style(" DONE! ", fg=typer.colors.BRIGHT_GREEN, bold=True)
    typer.echo(warn_title + " " + msg)
