"""Command-line interface for LinkP."""

import click
import sys
from pathlib import Path

from linkp.init import init_config
from linkp.runner import run_daily_post


@click.group()
def main():
    """LinkP - AI-powered Daily LinkedIn Developer Progress Poster."""
    pass


@main.command()
def init():
    """Initialize LinkP configuration files."""
    try:
        init_config()
        click.echo("\n✅ LinkP initialized successfully!")
        click.echo("\nNext steps:")
        click.echo("1. Edit linkp.env and fill in your API keys")
        click.echo("2. Run 'linkp run' to post your first update")
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@main.command()
def run():
    """Run daily LinkedIn post generation and posting."""
    try:
        run_daily_post()
        click.echo("\n✅ LinkedIn post created and posted successfully!")
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
