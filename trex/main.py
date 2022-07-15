import os
import shutil
import venv as venvpython
from distutils.errors import DistutilsFileError
from distutils.dir_util import copy_tree
import json
import git as gitpython
import typer
from tabulate import tabulate
import requests

# local imports
from trex import utils, meta

# app configuration
app = typer.Typer()
APP_NAME = meta.APP_NAME
APP_VERSION = meta.APP_VERSION


# ======================================================================================
# TREX TODOS

# yaaay, it's empty!

# ======================================================================================

@app.command()
def version():
    """
    Show the current version of trex and check for new ones
    """

    dir_path, config_path, templates_path = utils.get_app_dir()
    logo_text = typer.style("""
                 _
                | |_ _ __ _____  __
                | __| '__/ _ \ \/ /
                | |_| | |  __/>  <
                 \__|_|  \___/_/\_\ 
    """, fg=typer.colors.GREEN, bold=True)

    logo_line = typer.style(f"""
    ----------------------------------------------
        Version {APP_VERSION}    🦖    by berrysauce
    ----------------------------------------------
    """, fg=typer.colors.BRIGHT_GREEN, bold=True)

    more_info = typer.style("""
        Honey, it's the Templatosaurus Rex!
        Docs and more at berrysauce.me/trex
    """, fg=typer.colors.WHITE, bold=False)

    path_info = typer.style(f"""
    trex is located at:
    {dir_path}
    """, fg=typer.colors.BRIGHT_BLACK, bold=False)

    version_info = """
    ⚠️ A new version of trex is available
    Upgrade with 'pip install trex --upgrade'
    """

    try:
        res = requests.get("https://pypi.org/pypi/trex/json")
        latest_version = json.loads(res.text)["info"]["version"]
        if meta.APP_VERSION != latest_version:
            update_notice = typer.style(version_info, fg=typer.colors.BRIGHT_YELLOW, bold=True)
        else:
            # do not remove - referenced before assignment
            update_notice = """"""
    except requests.exceptions.RequestException:
        # do not remove - referenced before assignment
        update_notice = """"""

    typer.echo(logo_text+logo_line+more_info+path_info+update_notice)


@app.command()
def create(name: str):
    """
    Create a new trex template from the folder you're in
    """

    utils.print_start()

    utils.print_working("Getting template location")
    location = str(os.getcwd())

    utils.print_working("Adding template to storage")
    res = utils.add_template(name, {"location": location})

    if res:
        utils.print_done(f"Added '{name}' as template")
    else:
        utils.print_warn("A template with this name already exists")
    utils.show_tip(f"Use 'trex make {name}' to create a new directory from the template")


@app.command()
def remove(name: str):
    """
    Remove a template from trexs
    """

    utils.print_start()
    utils.print_working("Removing template")

    if utils.remove_template(name) is True:
        utils.print_done(f"{name} template was removed")
    else:
        utils.print_warn(f"{name} template doesn't exist")


@app.command()
def make(name: str,
         target: str,
         git: bool = typer.Option(False),
         venv: bool = typer.Option(False),
         installdeps: bool = typer.Option(False)):
    """
    Make a project from a trex template
    """

    utils.print_start()
    utils.print_working(f"Making directory from {name} template")

    utils.print_working("Fetching template data")
    res = utils.get_template(name)
    if res is None:
        utils.print_error("Template not found")
        return

    utils.print_working("Moving files around")
    try:
        destination = str(os.getcwd()) + "/" + target
        utils.print_working("Creating target directory")
        os.mkdir(destination)
    except FileExistsError:
        utils.print_error("File or directory already exists")
        return

    try:
        copy_tree(res["location"], destination)
    except DistutilsFileError:
        utils.print_error("Template directory doesn't seem to exist anymore")
        utils.print_working("Removing template")
        utils.print_working("Removing target directory")

        os.rmdir(destination)
        if utils.remove_template(name) is True:
            utils.print_done(f"{name} was removed")
        return

    if venv is True:
        # for documentation: https://docs.python.org/3/library/venv.html#venv.create
        # and: https://docs.python.org/3/library/venv.html#venv.EnvBuilder
        utils.print_working("Initializing virtual environment (venv) as .venv")
        # upgrade_deps=False since Python 3.9
        try:
            venvpython.create(
                destination+"/.venv",
                system_site_packages=False,
                clear=False,
                symlinks=False,
                with_pip=True,
                prompt=None,
                upgrade_deps=False
            )
        except Exception as exception:
            utils.print_error("Exception while initializing venv as .venv: \n" + str(exception))
            utils.print_working("Removing target directory")
            shutil.rmtree(destination)
            utils.print_done("Removed target directory")
            return

    if installdeps is True:
        utils.print_working("Installing dependencies from requirements.txt (might take a bit)")

        if os.path.isfile(destination + "/requirements.txt"):
            try:
                typer.echo(utils.terminal_width * "-")
                os.chdir(destination)
                if os.system(f"cd {destination}/.venv/bin && ./pip install -r {destination}/requirements.txt") == 0:
                    typer.echo(utils.terminal_width * "-")
                    utils.print_done("Requirements installed")
                else:
                    typer.echo(utils.terminal_width * "-")
                    raise OSError("Error installing requirements")
            except OSError:
                utils.print_warn("Requirement installation error - skipping")
        else:
            utils.print_warn(f"requirements.txt not found at {destination} - skipped")


    if git is True:
        utils.print_working("Initializing git repo")
        gitpython.Repo.init(destination)

    utils.print_done(f"Created {target} from {name}")


@app.command()
def show():
    """
    List all trex templates
    """

    res = utils.get_template(name=None)
    if res is None:
        utils.print_warn("Create a template first")
        return

    typer.secho("All available templates:", fg=typer.colors.BRIGHT_GREEN)
    head = ["Name", "Location"]
    data = []
    key_list = list(res.keys())
    values_list = list(res.values())

    for i, value in enumerate(key_list):
        data.append([value, values_list[i]["location"]])

    typer.echo(tabulate(data, headers=head, tablefmt="grid"))
    utils.show_tip("Use 'trex make <template name>' to create a new directory from the template")


@app.command()
def reset(force: bool = typer.Option(False)):
    """
    Reset trex's data, configuration, and templates
    """

    if force is False:
        warning = typer.style(" ⚠️ WARNING ", fg=typer.colors.BRIGHT_YELLOW, bold=True)
        typer.confirm(warning + " Do you really want to reset trex and delete all its data?", abort=True)

    dir_path, config_path, templates_path = utils.get_app_dir()
    try:
        utils.print_working("Deleting config storage")
        os.remove(config_path)
    except FileNotFoundError or NotADirectoryError:
        pass

    try:
        utils.print_working("Deleting templates storage")
        os.remove(templates_path)
    except FileNotFoundError or NotADirectoryError:
        pass

    try:
        utils.print_working("Deleting trex storage directory")
        os.rmdir(dir_path)
    except FileNotFoundError or NotADirectoryError:
        pass
    utils.print_done("Reset complete")


@app.command()
def config(key: str, enable: bool = typer.Option(False), disable: bool = typer.Option(False)):
    """
    Change trex's configuration
    """

    if key not in meta.config_options:
        utils.print_warn(f"{key} is not a valid config option")
        return

    if enable:
        value = True
    elif disable:
        value = False
    else:
        utils.print_warn("You need to provide --enable or --disable")
        return

    utils.print_working("Updating config")
    utils.add_config(key, data=value)
    utils.print_done(f"{key} set to {value}")
