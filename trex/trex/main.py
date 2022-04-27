import os
import typer
from tabulate import tabulate
from typing import Optional
from distutils.dir_util import copy_tree

# local imports
from trex import utils

# app configuration
app = typer.Typer()
APP_NAME = utils.APP_NAME
APP_VERSION = utils.APP_VERSION


@app.command()
def version():
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

    typer.echo(logo_text+logo_line+more_info+path_info)


@app.command()
def create(name: str):
    location = str(os.getcwd())
    typer.secho("\n" + "🚧 Creating template...", fg=typer.colors.BRIGHT_YELLOW)
    res = utils.add_template(name, {"location": location})

    if res:
        typer.secho(f"✅ {name} created!" + "\n", fg=typer.colors.BRIGHT_GREEN)
    else:
        typer.secho("⚠️ A template with this name already exists" + "\n", fg=typer.colors.YELLOW)
    utils.show_tip(f"Use 'trex make {name}' to create a new directory from the template")


@app.command()
def remove(name: str):
    typer.secho("\n" + "🚧 Removing template...", fg=typer.colors.BRIGHT_YELLOW)
    if utils.remove_template(name) is True:
        typer.secho(f"✅ {name} was removed!" + "\n", fg=typer.colors.BRIGHT_GREEN)
    else:
        typer.secho(f"⚠️ {name} doesn't exist" + "\n", fg=typer.colors.YELLOW)


@app.command()
def make(name: str, target: Optional[str] = typer.Argument(None)):
    typer.secho("\n" + " 🦖 Rooaaar! I'm ready!", fg=typer.colors.BRIGHT_GREEN)
    typer.secho(" 🚧 Making from template", fg=typer.colors.BRIGHT_YELLOW)

    typer.secho("    Fetching template data...", fg=typer.colors.BRIGHT_YELLOW)
    res = utils.get_template(name)

    typer.secho("    Moving files around...", fg=typer.colors.BRIGHT_YELLOW)
    if target:
        destination = str(os.getcwd()) + "/" + target
        typer.secho("    Creating target directory...", fg=typer.colors.BRIGHT_YELLOW)
        os.mkdir(destination)
    else:
        destination = str(os.getcwd())

    copy_tree(res["location"], destination)
    typer.secho(f"✅ Created from {name}!" + "\n", fg=typer.colors.BRIGHT_GREEN)

@app.command()
def all():
    typer.secho("\n" + "All available templates:", fg=typer.colors.BRIGHT_GREEN)
    res = utils.get_template(name=None)
    head = ["Name", "Location"]
    data = []
    key_list = list(res.keys())
    values_list = list(res.values())

    if len(key_list) == 0:
        typer.secho(f"⚠️ Create a template first" + "\n", fg=typer.colors.YELLOW)
        return

    for i in range(len(key_list)):
        data.append([key_list[i], values_list[i]["location"]])

    typer.echo(tabulate(data, headers=head, tablefmt="grid") + "\n")
    utils.show_tip(f"Use 'trex make <template name>' to create a new directory from the template")


@app.command()
def reset(force: bool = typer.Option(False)):
    if force is False:
        warning = typer.style(" ⚠️ WARNING ", fg=typer.colors.WHITE, bg=typer.colors.YELLOW, bold=True)
        typer.confirm("\n" + warning + " Do you really want to reset trex and delete all its data?", abort=True)

    dir_path, config_path, templates_path = utils.get_app_dir()
    try:
        os.remove(config_path)
        os.remove(templates_path)
        os.rmdir(dir_path)
    except FileNotFoundError or NotADirectoryError:
        pass
    typer.secho(f"✅ Reset complete" + "\n", fg=typer.colors.BRIGHT_GREEN)



@app.command()
def config(name: str, enable: bool = typer.Option(False), disable: bool = typer.Option(False)):
    if enable:
        value = True
    elif disable:
        value = False
    else:
        typer.secho("\n" + "🛑️ You need to provide --enable or --disable" + "\n", fg=typer.colors.RED)
        return

    typer.secho("\n" + "🚧️ Updating config", fg=typer.colors.BRIGHT_YELLOW)
    utils.add_config(name, data=value)
    typer.secho(f"✅ {name} set to {value}!" + "\n", fg=typer.colors.BRIGHT_GREEN)