#!/usr/bin/env python

import click

import sys
import os

curpath = os.path.dirname(__file__)
if(curpath not in sys.path):
    sys.path.append(curpath)

from util import getIngredientRepo
from util import getDispenser

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
    repo = getIngredientRepo()

    ings = repo.getAll(avail)

    echoIngredients(ings)

@main.command()
@click.option('--jar/--id', default=False, help="find by jar or ID")
@click.argument('ing', required=True)
def describe(jar, ing):
    """
    Describe an ingrediant by ID, jar, or name
    """

    repo = getIngredientRepo()

    ingredient = repo.getIngredient(ing, jar)
    if ingredient is None:
        click.echo("Not found.")
    else:
        echoIngredients([ingredient])

@main.command()
@click.option('--flow', type=(int), help="ms per oz, 0 for default")
@click.option('--jar', type=(int), help="jar postion, 0 to remove postion")
@click.option('--mixer', type=(bool), help="denotes if available on the side as a mixer")
@click.option('--name', type=(str), help="name of ingredient (duh)")
@click.argument('id', type=(int), required=True)
@click.pass_context
def update(ctx, flow, jar, mixer, name, id):
    """
    Update an ingrediant by ID
    """
    repo = getIngredientRepo()

    updateArgs = {}
    if flow is not None:
        updateArgs["flow"] = flow

    if jar is not None:
        updateArgs["jar_pos"] = jar

    if mixer is not None:
        updateArgs["mixer"] = mixer

    if name is not None and name != "":
        updateArgs["name"] = name

    success = False if len(updateArgs) <= 0 else repo.updateIngredient(id, **updateArgs)

    if success:
        ctx.invoke(describe, ing=id)
    else:
        click.echo("Unable to update ingredient. Make sure the ID is right.")

@main.command()
@click.option('--flow', type=(int), help="override ms per oz")
@click.option('--jar/--id', default=False, help="find by jar or ID")
@click.argument('ing', required=True)
def test(flow, jar, ing):
    """
    Dispense 1 oz of the ingredient specified by jar or ID
    """

    repo = getIngredientRepo()

    ingredient = repo.getIngredient(ing, jar)
    if ingredient is None:
        click.echo("Not found.")
        return

    if ingredient["jar_pos"] is None:
        click.echo(ingredient["name"] + " is not assigned a jar.")
        return

    flow = flow if flow is not None and flow > 0 else ingredient["flow"]

    recipeIng = {
        "id": ingredient["id"],
        "name": ingredient["name"],
        "jar_pos": ingredient["jar_pos"],
        "oz": 1,
        "flow": flow
    }

    dispenser = getDispenser()

    sizeFactor = dispenser.getSizeFactor()
    if sizeFactor != 1:
        click.echo("Please set the dispense size switch to \"single\"")
        click.echo("Current size factor: " + str(sizeFactor))
        return

    dispenser.dispenseDrink([recipeIng])

    click.echo("Test complete for "+ ingredient["name"])

if __name__ == "__main__":
    main()