import click


@click.command()
def version():
    """Display the current version."""
    click.echo("0.0.1")
