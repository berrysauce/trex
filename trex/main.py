import os
import io
import shutil
import venv as venvpython
from distutils.errors import DistutilsFileError
from distutils.dir_util import copy_tree
import json
import git as gitpython
import typer
from tabulate import tabulate
import requests
import zipfile
import pathlib

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
        
        Use trex --help to see all commands
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
def support():
    """
    Report issues or request features for trex
    """
    typer.launch("https://github.com/berrysauce/trex/issues/new/choose")


@app.command()
def new(name: str):
    """
    Create a new trex template from the folder you're in
    """

    utils.print_start()

    utils.print_working("Getting template location")
    location = str(os.getcwd())

    utils.print_working("Adding template to storage")
    res = utils.add_template(name, {"location": location, "type": "local"})

    if res:
        utils.print_done(f"Added '{name}' as template")
    else:
        utils.print_warn("A template with this name already exists")
    utils.show_tip(f"Use 'trex make {name}' to create a new directory from the template")


@app.command()
def remote(name: str, url: str):
    """
    Create a new trex template from a GitHub Repository
    """

    utils.print_start()

    # when regex is to complicated...
    utils.print_working("Checking URL")
    if not url.startswith("https://github.com/") and url.count("/") != 4:
        # these checks check for this format: https://github.com/username/repo
        utils.print_error(
        """URL Format does not comply with the GitHub Repository URL format.
        It has to comply with this format: https://github.com/username/repo""")
        return

    res = requests.get(url)
    if res.status_code != 200:
        utils.print_error(f"Got status code {res.status_code} from {url}")
        return

    utils.print_working("Adding template to storage")
    res = utils.add_template(name, {"location": url, "type": "remote"})

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
    location = res["location"]
    if res is None:
        utils.print_error("Template not found")
        return

    try:
        destination = str(os.getcwd()) + "/" + target
        if not git:
            utils.print_working("Creating target directory")
            os.mkdir(destination)
    except FileExistsError:
        utils.print_error("File or directory already exists")
        return

    if res["type"] == "local":
        utils.print_working("Moving files around")
        try:
            copy_tree(location, destination)
        except DistutilsFileError:
            utils.print_error("Template directory doesn't seem to exist anymore")
            utils.print_working("Removing template")
            utils.print_working("Removing target directory")

            os.rmdir(destination)
            if utils.remove_template(name) is True:
                utils.print_done(f"{name} was removed")
            return
    elif res["type"] == "remote":
        utils.print_working(f"Downloading {location} from GitHub (this might take a bit)")

        path = pathlib.Path(destination)
        temp_destination = path.parent

        request = requests.get(location + "/archive/master.zip")

        # this header has the file name
        file_header = request.headers.get("Content-Disposition")
        # split file name from attachment; filename=******.zip
        file_name = file_header.split("filename=", 1)[1]
        # split dir name from ******.zip
        dir_name = file_name.split(".", 1)[0]

        if os.path.exists(str(temp_destination) + "/" + dir_name):
            utils.print_error(str(temp_destination) + "/" + dir_name + " already exists!")
            return

        if os.path.exists(destination):
            utils.print_error(destination + " already exists!")
            return

        if request.status_code != 200:
            utils.print_error(f"Request error: {request.status_code}")
            os.rmdir(destination)
            return

        try:
            utils.print_working("Extracting repo from memory")
            with zipfile.ZipFile(io.BytesIO(request.content)) as z:
                z.extractall(temp_destination)
                os.rename(str(temp_destination) + "/" + dir_name, destination)
        except zipfile.BadZipfile:
            utils.print_error("Invalid zip file")
            os.rmdir(str(temp_destination) + "/" + file_name)
            return

        utils.print_done("Repo downloaded")
    else:
        utils.print_error(f"Unknown template type ({res['type']})")
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
def set(path: str):
    """
    Set template directory path. All folders created or moved in here will automatically be available as templates.
    """

    if not os.path.isdir(path):
        utils.print_warn(f"{path} is not a directory")
        return

    utils.print_working("Updating config")
    utils.add_config("path", data=path)
    utils.print_done(
        f"""trex's templates directory is now set to {path}
Folders you put into this directory will automatically be added to trex as templates.""")


@app.command()
def all(open: bool = typer.Option(False)):
    """
    List all trex templates
    """

    trex_path = utils.get_config("path")
    if trex_path is None:
        utils.print_warn("trex's templates path is not set. Set it with 'trex set PATH'")
        return

    if open:
        typer.secho(f"Opening templates directory at {trex_path}", fg=typer.colors.BRIGHT_GREEN)
        typer.launch(trex_path)
        return

    res = utils.get_template(name=None)
    if res is None:
        utils.print_warn("Create a template first")
        return

    typer.secho("All available templates:", fg=typer.colors.BRIGHT_GREEN)
    head = ["Name", "Location", "Type"]
    data = []
    key_list = list(res.keys())
    values_list = list(res.values())

    for i, value in enumerate(key_list):
        data.append([value, values_list[i]["location"], values_list[i]["type"]])

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
