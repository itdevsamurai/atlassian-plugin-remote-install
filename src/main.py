import click


@click.group()
def cli():
    pass


@click.command(help="Install plugin on instance")
def install():
    click.echo("Installing plugin")


@click.command(help="Remove plugin on instance")
def remove():
    click.echo("Removing plugin")


cli.add_command(install)
cli.add_command(remove)

if __name__ == "__main__":
    cli()
