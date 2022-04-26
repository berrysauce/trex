import typer

# trex-o imports
import utils

# app configuration
app = typer.Typer()
APP_NAME = "trex"
APP_VERSION = "0.1.0"

"""
def main():
    typer.echo(storage.get_app_dir())
"""

@app.command()
def version():
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
    {utils.get_app_dir()}
    """, fg=typer.colors.BRIGHT_BLACK, bold=False)

    typer.echo(logo_text+logo_line+more_info+path_info)

@app.command()
def path():
    typer.secho("[...] Creating config directory and file", fg=typer.colors.YELLOW)
    res = utils.init_app_dir()
    if res is True:
        typer.secho("[ X ] Config directory and file already exist", fg=typer.colors.RED)
    else:
        typer.secho("[ ✓ ] Config directory and file created", fg=typer.colors.GREEN)

@app.command()
def create(name: str, location: str):
    typer.secho("\n" + "🚧 Creating template...", fg=typer.colors.BRIGHT_YELLOW)
    res = utils.add_template(name, {"location": location})

    if res:
        typer.secho(f"✅ {name} created!", fg=typer.colors.BRIGHT_GREEN)
    else:
        typer.secho("🛑 A template with this name already exists", fg=typer.colors.RED)
    utils.show_tip(f"Use 'trex make {name}' to create a new directory from the template")

@app.command()
def config(name: str, enable: bool = typer.Option(False), disable: bool = typer.Option(False)):
    if enable:
        value = True
    elif disable:
        value = False
    else:
        typer.secho("\n" + "🛑️ You need to provide --enable or --disable", fg=typer.colors.RED)
        return

    typer.secho("\n" + "🚧️ Updating config", fg=typer.colors.BRIGHT_YELLOW)
    utils.add_config(name, data=value)
    typer.secho(f"✅ {name} set to {value}!", fg=typer.colors.BRIGHT_GREEN)



if __name__ == "__main__":
    app()