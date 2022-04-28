## This is trex 🦖

trex is template manager in the form of a CLI app. You can creat, organise, and clone-from template directories. It doesn't matter if the template is a directory on your machine or a GitHub repository: with trex you only need a few seconds to actually get to coding. Not only that, but trex is really easy to use.

## Why you should use trex

Getting started with a new project? trex helps you out by initialising a project directory with a virtual environment and all packages installed in one command. This makes creating a new FastAPI project, for example, even easier.

## Features & Roadmap

- [x] Organise templates (create, remove, list)
- [x] Make project from local directory template
- [ ] Make project from GitHub template
- [ ] Run scripts automatically on creation
- [ ] Create virtualenv automatically and import requirements on creation

## How to install trex

Open your terminal and run the following line:
```
pip install trex
```
trex should be downloaded and installed automatically. To test if trex has been added to your path correctly, use:
```
trex version
```
You can also install the autocompletion bindings for trex with:
```
trex --install-completion [bash|zsh|etc.]
```

## Available Commands

#### `trex version`
Show trex's installed version and location on your system.

#### `trex create [name]`
Create a template from the directory you're currently in.

#### `trex remove [name]`
Remove the template from trex's storage.

#### `trex make [name] [target]`
Make a project directory from template in the current directory.

#### `trex all`
Show all templates and their path in trex's storage.

#### `trex reset [--force]`
Reset trex's data.

## Support or Contact

If you need any help, I'm available via email at trex[at]berrysauce[dot]com. If you find any security issues please also send them to the mentioned email address. If you find any bugs or would like to have a certain feature, make a pull request yourself, or create an issue [here](https://github.com/berrysauce/trex/issues).
