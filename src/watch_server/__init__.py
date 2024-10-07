import click

from .plot_data import make_data as _make_data
from .plot_data import plot_data as _plot_data
from .server import server as _server


@click.group()
def cli():
    pass


@cli.command()
def make_data() -> None:
    _make_data()


@cli.command()
def plot_data() -> None:
    _plot_data()


@cli.command()
def server() -> None:
    try:
        _server()
    except KeyboardInterrupt:
        exit(0)
