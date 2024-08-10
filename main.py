from enum import Enum

import click
from line_provider.main import main as line_provider_main

from bet_maker.main import main as bet_maker_main


class ServiceType(str, Enum):
    bet_maker = "bet_maker"
    line_provider = "line_provider"


SERVICE_TYPES = [pt.value for pt in ServiceType]


@click.command()
@click.option(
    '--name',
    type=click.Choice(SERVICE_TYPES),
    required=True,
    help='Service name'
)
def run(name: ServiceType) -> None:
    if name == ServiceType.bet_maker:
        bet_maker_main()

    if name == ServiceType.line_provider:
        line_provider_main()
