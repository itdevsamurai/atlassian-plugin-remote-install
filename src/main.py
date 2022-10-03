import logging

import click
from rich.logging import RichHandler
from rich.traceback import install as rich_traceback_install

from config import Config
from install_plugin import install_plugin_server
from remove_plugin import remove_plugin_server

logging.basicConfig(
    level=Config.LOG_LEVEL,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler()],
)
# only show locals if the log level is smaller than INFO level
rich_traceback_install(show_locals=logging.getLogger().level < logging.INFO)


@click.group()
def cli():
    pass


cli.add_command(install_plugin_server)
cli.add_command(remove_plugin_server)

if __name__ == "__main__":
    cli()
