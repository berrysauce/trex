from typer.testing import CliRunner

# local imports
from trex.main import app
from trex.meta import APP_VERSION

runner = CliRunner()
test_template = "pytest-test"
test_config = "tips"


"""
MISSING
- make
"""


def test_version():
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert APP_VERSION in result.stdout

def test_create():
    result = runner.invoke(app, ["create", test_template])
    assert result.exit_code == 0
    assert f"Added '{test_template}' as template" in result.stdout

def test_all():
    result = runner.invoke(app, ["all"])
    assert result.exit_code == 0
    assert "All available templates:" in result.stdout
    assert test_template in result.stdout

def test_remove():
    result = runner.invoke(app, ["remove", test_template])
    assert result.exit_code == 0
    assert f"{test_template} template was removed" in result.stdout

def test_config_disable():
    result = runner.invoke(app, ["config", test_config, "--disable"])
    assert result.exit_code == 0
    assert f"{test_config} set to False" in result.stdout

def test_config_enable():
    result = runner.invoke(app, ["config", test_config, "--enable"])
    assert result.exit_code == 0
    assert f"{test_config} set to True" in result.stdout

def test_reset():
    result = runner.invoke(app, ["reset", "--force"])
    assert result.exit_code == 0
    assert "Reset complete" in result.stdout