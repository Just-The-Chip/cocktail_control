import click
from configparser import ConfigParser

import sys
import os

curDir = os.path.abspath(os.path.join(__file__, os.pardir))
parentpath = os.path.abspath(os.path.join(curDir, os.pardir))

if(parentpath not in sys.path):
    sys.path.append(parentpath)

from repository import IngredientRepository
#from dispenser import Dispenser

def getRepo():
    config = ConfigParser()
    config.read('config.ini')

    db_path = config['Database'].get('Path', 'data.db')

    if not os.path.isabs(db_path):
        db_path = os.path.join(parentpath, db_path)

    return IngredientRepository(db_path)

def echoIngredients(ingredients):
    cols = {
        "jar_pos": len("jar_pos") + 2,
        "mixer": len("mixer") + 2, 
        "name": len("name") + 2, 
        "flow": len("flow") + 2,
        "id": len("id") + 2
    }

    for ing in ingredients:
        idLen = len(str(ing["id"]))
        if idLen > cols["id"]:
            cols["id"] = idLen

        nameLen = len(str(ing["name"]))
        if nameLen > cols["name"]:
            cols["name"] = nameLen

    fmtStr = "| {:<"+str(cols["jar_pos"])+"} | {:<"+str(cols["mixer"])+"} | {:<"+str(cols["name"])+"} | {:<"+str(cols["flow"])+"} | {:<"+str(cols["id"])+"} |"

    header = fmtStr.format("jar_pos", "mixer", "name", "flow", "id")
    click.echo(header)
    click.echo(('-' * len(header))[:len(header)])

    for ing in ingredients: 
        click.echo(fmtStr.format(str(ing["jar_pos"]), str(ing["mixer"]), ing["name"], str(ing["flow"]), str(ing["id"])))

@click.group()
def main():
    """
    CLI for calibrating ingredients
    """
    pass

@main.command(name="list")
@click.option('--avail', is_flag=True, help="only include ingredients that are mixers or are assigned a jar")
def listIng(avail):
    """
    Lists all ingredients
    """
    repo = getRepo()

    ings = repo.getAll(avail)

    echoIngredients(ings)

@main.command()
@click.option('--jar/--id', default=False, help="find by jar or ID")
@click.argument('ing', required=True)
def describe(jar, ing):
    """
    Describe an ingrediant by ID, jar, or name
    """

    repo = getRepo()

    ingredient = repo.getIngredient(ing, jar)
    if ingredient is None:
        click.echo("Not found.")
    else:     
        echoIngredients([ingredient])

# @main.command()
# @click.option('--flow', )
def update():
    pass

def testIngredient():
    pass

def updateJarPrime():
    pass    

if __name__ == "__main__":
    main()