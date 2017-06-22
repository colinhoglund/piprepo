import os
import re


def normalize(filename):
    ''' get PEP-503 normalized project name from package filename'''
    return re.sub(r"[-_.]+", "-", os.path.basename(filename).split('-')[0]).lower()
