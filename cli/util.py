import click
from configparser import ConfigParser

import sys
import os

curDir = os.path.abspath(os.path.join(__file__, os.pardir))
parentpath = os.path.abspath(os.path.join(curDir, os.pardir))

if(parentpath not in sys.path):
    sys.path.append(parentpath)

from repository import IngredientRepository
from dispenser import Dispenser

def getRepo():
    config = ConfigParser()
    config.read('../config.ini')

    db_path = config['Database'].get('Path', 'data.db')

    if not os.path.isabs(db_path):
        db_path = os.path.join(parentpath, db_path)

    return IngredientRepository(db_path)

def getDispenser():
    config = ConfigParser()
    config.read('../config.ini')

    addr = int(config['Dispenser'].get('Address', '0x00'), 16)
    mspoz = int(config['Dispenser'].get('MsPerOz', '2000'))

    single = int(config['Hardware'].get('SwitchSingle'))
    double = int(config['Hardware'].get('SwitchDouble'))

    return Dispenser(addr, mspoz=mspoz, spin=single, dpin=double)