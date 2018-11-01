
import click
from configparser import ConfigParser

import sys
import os

curpath = os.path.dirname(__file__)
if(curpath not in sys.path):
    sys.path.append(curpath)

from util import getConfig
from util import configPath
from util import getDispenser

@click.group()
def main():
    """
    CLI for calibrating jar prime time
    """
    pass

@main.command(name="list")
def listJars():
    """
    Lists all prime times
    """
    config = getConfig()

    fmtStr = "Jar {:<2} = {}ms"

    for key, value in config['Prime'].items():
        click.echo(fmtStr.format(key, value))

@main.command()
@click.argument('jar', type=click.IntRange(1, 21), required=True)
@click.argument('time', type=click.IntRange(0, 60000))
def update(jar, time):
    """
    Update the prime time (in ms) for a jar (max 60 seconds)
    """
    config = getConfig()
    if 'Prime' not in config:
        config['Prime'] = {}

    config['Prime'][str(jar)] = str(time)

    with open(configPath(), 'w') as configfile:
        config.write(configfile)
        click.echo("Jar #" + str(jar) + " updated to " + str(time) + "ms")

@main.command()
@click.option('--time', type=click.IntRange(0, 60000), help="override prime time in ms (max 60 seconds)")
@click.argument('jar', type=(int), required=True)
def test(time, jar):
    """
    Tests priming the jar without dispensing anything (i.e. 0 oz)
    """

    mockIng = {
        "jar_pos": jar,
        "oz": 0
    }

    if time is not None and time > 0:
        dispenser = getDispenser(prime={str(jar): time})
    else:
        dispenser = getDispenser()

    dispenser.dispenseDrink([mockIng])

    click.echo("Test complete for jar #"+ jar)


if __name__ == "__main__":
    main()