"""Tests for main CLI."""

import pytest
from click.testing import CliRunner
from testTool.main import cli


def test_cli_help():
    """Test CLI help command."""
    runner = CliRunner()
    result = runner.invoke(cli, ['--help'])
    
    assert result.exit_code == 0
    assert 'Browser-Based Automated Testing Builder' in result.output


def test_cli_version():
    """Test CLI version command."""
    runner = CliRunner()
    result = runner.invoke(cli, ['--version'])
    
    assert result.exit_code == 0


def test_list_scripts_empty():
    """Test listing scripts when none exist."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(cli, ['list-scripts'])
        
        # Should succeed even with no scripts
        assert result.exit_code == 0


def test_interpret_command():
    """Test interpret command."""
    runner = CliRunner()
    result = runner.invoke(cli, ['interpret', 'click the button'])
    
    assert result.exit_code == 0
    assert 'Instruction:' in result.output

