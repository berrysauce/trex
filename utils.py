import os
from pathlib import Path
import typer
import json

# local imports
from main import APP_NAME


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


def get_template(name: str):
    dir_path, config_path, templates_path = get_app_dir()
    check_app_dir()

    try:
        with open(templates_path, "r") as f:
            stored_config = json.loads(f.read())
        return stored_config[name]
    except FileNotFoundError or KeyError:
        return None


"""
=============================================================
                      CONFIG HANDLING
=============================================================
"""

def add_config(key: str, data):
    dir_path, config_path, templates_path = get_app_dir()
    check_app_dir()

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
    except FileNotFoundError or KeyError:
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

    tip_title = typer.style(" TIP ", fg=typer.colors.WHITE, bg=typer.colors.GREEN, bold=True)
    tip = 100 * "-" + "\n" + tip_title + f" {msg}\n" + "Disable tips with 'trex config tips --disable'\n" + 100 * "-" + "\n"
    typer.echo(tip)