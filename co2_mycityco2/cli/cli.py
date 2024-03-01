import sys

import typer
from loguru import logger

from co2_mycityco2.const import settings

from .format import cli as format_cli

cli = typer.Typer(no_args_is_help=True)

cli.add_typer(format_cli, name="format")

logger.remove(0)
logger.level("FTRACE", no=3, color="<blue>")

logger.add(
    sys.stdout,
    enqueue=True,
    backtrace=True,
    diagnose=True,
    colorize=True,
    format=settings.LOGORU_FORMAT,
    level=settings.LOGURU_LEVEL,
)


@cli.command()
def hello():
    logger.info("Hello from mycityco2 plugins")


@cli.command()
def goodbye():
    logger.info("Goodbye from mycityco2 plugins")
