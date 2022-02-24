#!/usr/bin/env python

from multiprocessing.dummy import Array
from typing import List
import click

import sys
import os
import json

curpath = os.path.dirname(__file__)
if(curpath not in sys.path):
    sys.path.append(curpath)

from util import getDrinkRepo

class IngredientList(click.ParamType):
    name = "json ingredient list"

    def convert(self, value, param, ctx):
        try:
            jsonVal = json.loads(value)
            if not isinstance(jsonVal, list):
                raise ValueError

            return jsonVal
            
        except json.JSONDecodeError:
            self.fail(f"{value!r} is not a valid JSON list", param, ctx)
        except ValueError:
            self.fail(f"{value!r} is not a list", param, ctx)
        except BaseException as err:
            self.fail(f"Unexpected {err=}, {type(err)=}", param, ctx)

INGREDIENT_LIST = IngredientList()

def echoDrinks(drinks):
    cols = {
        "id": len("id") + 2,
        "name": len("name") + 2,
        "available": len("available") + 2,
        "image": len("image") + 2
    }

    for drink in drinks:
        idLen = len(str(drink["id"]))
        if idLen > cols["id"]:
            cols["id"] = idLen

        nameLen = len(str(drink["name"]))
        if nameLen > cols["name"]:
            cols["name"] = nameLen

        imageLen = len(str(drink["image"]))
        if imageLen > cols["image"]:
            cols["image"] = imageLen

    fmtStr = "| {:<"+str(cols["id"])+"} | {:<"+str(cols["name"])+"} | {:<"+str(cols["available"])+"} | {:<"+str(cols["image"])+"} |"

    header = fmtStr.format("id", "name", "available", "image")
    click.echo(header)
    click.echo(('-' * len(header))[:len(header)])

    for drink in drinks:
        click.echo(fmtStr.format(str(drink["id"]), str(drink["name"]), drink["available"], str(drink["image"])))

    click.echo(('-' * len(header))[:len(header)])

def echoIngredients(ingredients, outpuJson):
    if(outpuJson):
        jsonIngredients = []

        for ing in ingredients:
            jsonIngredients.append({
                "id": ing["id"],
                "oz": ing["oz"]
            })
        click.echo(json.dumps(jsonIngredients))
        return 

    cols = {
        "jar_pos": len("jar_pos") + 2,
        "oz": len("oz") + 2,
        "name": len("name") + 2,
        "id": len("id") + 2
    }

    for ing in ingredients:
        idLen = len(str(ing["id"]))
        if idLen > cols["id"]:
            cols["id"] = idLen

        nameLen = len(str(ing["name"]))
        if nameLen > cols["name"]:
            cols["name"] = nameLen

        ozLen = len(str(ing["oz"]))
        if ozLen > cols["oz"]:
            cols["oz"] = ozLen

    fmtStr = "| {:<"+str(cols["jar_pos"])+"} | {:<"+str(cols["oz"])+"} | {:<"+str(cols["name"])+"} | {:<"+str(cols["id"])+"} |"

    header = fmtStr.format("jar_pos", "oz", "name", "id")
    click.echo(header)
    click.echo(('-' * len(header))[:len(header)])

    for ing in ingredients:
        click.echo(fmtStr.format(str(ing["jar_pos"]), str(ing["oz"]), ing["name"], str(ing["id"])))
    
    click.echo(('-' * len(header))[:len(header)])

@click.group()
def main():
    """
    CLI for calibrating ingredients
    """
    pass

@main.command(name="list")
@click.option('--avail', is_flag=True, help="only include drinks with available ingredients")
def listDrink(avail):
    """
    Lists all drinks
    """
    repo = getDrinkRepo()

    if(avail): 
        drinks = repo.getAvailableDrinks()
    else:
        drinks = repo.getAllDrinks()

    echoDrinks(drinks)

@main.command()
@click.option('--json', is_flag=True, help="output ingredients in JSON")
@click.argument('drink', required=True)
def describe(json, drink):
    """
    Describe an ingrediant by ID or name
    """

    repo = getDrinkRepo()

    drink = repo.getDrink(drink)
    if drink is None:
        click.echo("Not found.")
    else:
        echoDrinks([drink])
        echoIngredients(repo.getDrinkRecipe(drink["id"]), json)

@main.command()
@click.option('--name', type=(str), required=True, help="name of drink (duh)")
@click.option('--image', type=(str), help="image file for drink")
@click.option('--ingredients', type=(INGREDIENT_LIST), required=True, help="JSON list of ingredients")
@click.pass_context
def create(ctx, name, image, ingredients):
    """
    Create a new drink
    """
    repo = getDrinkRepo()

    drinkID = repo.insertDrink(name, image, ingredients)

    if drinkID:
        ctx.invoke(describe, drink=drinkID)
    else:
        click.echo("Unable to update ingredient. Make sure the ID is right.")

@main.command()
@click.option('--name', type=(str), help="name of drink (duh)")
@click.option('--image', type=(str), help="image file for drink")
@click.option('--ingredients', type=(INGREDIENT_LIST), help="full JSON list of ingredients")
@click.argument('id', type=(int), required=True)
@click.pass_context
def update(ctx, name, image, ingredients, id):
    """
    Update an ingrediant by ID
    """
    repo = getDrinkRepo()

    updateArgs = {}
    if image is not None:
        updateArgs["image"] = image

    if ingredients is not None:
        updateArgs["ingredients"] = ingredients

    if name is not None and name != "":
        updateArgs["name"] = name

    success = False if len(updateArgs) <= 0 else repo.updateDrink(id, **updateArgs)

    if success:
        ctx.invoke(describe, drink=id)
    else:
        click.echo("Unable to update drink. Make sure the ID is right.")

if __name__ == "__main__":
    main()