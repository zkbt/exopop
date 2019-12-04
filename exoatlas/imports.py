# imports that are need by many exoatlas subsections
import os, sys, time, shutil, warnings
from unittest import mock
from tqdm import tqdm


import numpy as np, matplotlib.pyplot as plt, matplotlib.animation as animation
from matplotlib.ticker import ScalarFormatter, FormatStrFormatter, LogLocator


from astropy.utils.exceptions import AstropyDeprecationWarning
warnings.simplefilter('ignore', category=AstropyDeprecationWarning)

# this function downloads a file and returns its filepath
from astropy.utils.data import download_file
from astropy.io import ascii
from astropy.table import Table, vstack, join
from astropy.visualization import quantity_support
quantity_support()

# some general custom utilities from Zach
from .talker import Talker

# units and constants from astropy
import astropy.units as u, astropy.constants as con
from astropy.time import Time




def mkdir(path):
	'''A mkdir that doesn't complain if it fails.'''
	try:
		os.mkdir(path)
	except:
		pass

import matplotlib.colors as co
def name2color(name):
    """Return the 3-element RGB array of a given color name."""
    if '#' in name:
        h = name
    else:
        h = co.cnames[name].lower()
    return co.hex2color(h)

# create a directory structure ()
try:
	# search for an environment variable
	base = os.getenv('EXOATLAS_DATA')
	assert(base is not None)
except AssertionError:
	# otherwise put it in the local directory
	cwd = os.getcwd()
	base = os.path.join(cwd, 'exoatlas-downloads')
mkdir(base)

directories = dict(data=os.path.join(base, 'data/'))
for k in directories.keys():
    mkdir(directories[k])

def reset_local_data():
	if 'y' in input('Are you sure you want to wipe all'
					'local exoplanet-atlas data files? [y/N]'):
		shutil.rmtree(directories['data'])
		mkdir(directories['data'])
		print(f"Removed all local data from {directories['data']}")

from pkg_resources import resource_filename


# some kludge for dealing with Python 3 vs 2?
try:
    FileNotFoundError
except NameError:
    FileNotFoundError = IOError

def clean(s):
    '''
    A wrapper function to clean up complicated strings.
    '''
    bad = ' !@#$%^&*()-,./<>?'
    cleaned = s + ''
    for c in bad:
        cleaned = cleaned.replace(c, '')
    return cleaned

def time_from_modified(filename):
    '''
    How long ago was this file last modified?
    '''
    try:
        dt = Time.now().unix - os.path.getmtime(filename)
        return dt/60/60/24
    except FileNotFoundError:
        return np.inf


def check_if_needs_updating(filename, maximum_age=1.0):
    '''
    Do a (possibly interactive) check to see if this file
    is so old that it needs to be updated.

    Returns
    -------
    old : bool
        True if the file is so old it needs updating
        False if the file doesn't need updating
    '''

    # how long ago was the data updated?
    dt = time_from_modified(filename)

    old = False
    if dt == np.inf:
        old = True
    elif dt > maximum_age:
        print(f'{filename} is {dt:.3f} days old.')
        old = 'y' in input('Should it be updated? [y/N]').lower()

    return old


def one2another(bottom='white', top='red', alphabottom=1.0, alphatop=1.0, N=256):
	'''
	Create a cmap that goes smoothly (linearly in RGBA) from "bottom" to "top".
	'''
	rgb_bottom, rgb_top = name2color(bottom), name2color(top)
	r = np.linspace(rgb_bottom[0],rgb_top[0],N)
	g = np.linspace(rgb_bottom[1],rgb_top[1],N)
	b = np.linspace(rgb_bottom[2],rgb_top[2],N)
	a = np.linspace(alphabottom, alphatop,N)
	colors = np.transpose(np.vstack([r,g,b,a]))
	cmap = co.ListedColormap(colors, name='{bottom}2{top}'.format(**locals()))
	return cmap
