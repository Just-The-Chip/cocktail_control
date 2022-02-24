import click
from configparser import ConfigParser

import sys
import os

curDir = os.path.abspath(os.path.join(__file__, os.pardir))
parentpath = os.path.abspath(os.path.join(curDir, os.pardir))

if(parentpath not in sys.path):
    sys.path.append(parentpath)

from repository import IngredientRepository
from repository import DrinkRepository
from dispenser import Dispenser

def configPath():
    return parentpath + '/config.ini'

def getConfig():
    config = ConfigParser()
    config.read(configPath())
    return config

def getDBPath():
    config = getConfig()

    db_path = config['Database'].get('Path', 'data.db')

    if not os.path.isabs(db_path):
        db_path = os.path.join(parentpath, db_path)

    return db_path

def getIngredientRepo():
    return IngredientRepository(getDBPath())

def getDrinkRepo():
    return DrinkRepository(getDBPath())

def getDispenser(**kwargs):
    config = getConfig()

    addr = int(config['Dispenser'].get('Address', '0x00'), 16)
    mspoz = int(config['Dispenser'].get('MsPerOz', '2000'))

    single = int(config['Hardware'].get('SwitchSingle'))
    double = int(config['Hardware'].get('SwitchDouble'))

    prime = kwargs.get('prime', config['Prime'])

    return Dispenser(addr, mspoz=mspoz, prime=prime, spin=single, dpin=double)