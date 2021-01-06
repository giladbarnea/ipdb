"""This file is evalulated just before ipdb3.set_trace() is called (ipdb fork)"""
print(f'in ipdb prebreak file')
import builtins
import sys
import rich
from rich import inspect
import os
from rich.pretty import pprint as ppr
from IPython import start_ipython, get_ipython

from rich.console import Console
import pyinspect as pi

con = Console()
if sys.exc_info()[0]:
    print(f'prebreak: building fancy trace... ({sys.exc_info()[0] = })')
    con.print_exception(show_locals=True)


def mm(topic, subtopic=''):
    os.system(f'bash -c "/usr/bin/python3.8 -m mytool.myman {topic} {subtopic}"')


def what(*args, **kwargs):
    inspect(*args, **kwargs, methods=True, help=True, value=True)


def what_(*args, **kwargs):
    inspect(*args, **kwargs, methods=True, help=True, private=True, value=True)


def what__(*args, **kwargs):
    inspect(*args, **kwargs, methods=True, help=True, private=True, dunder=True, value=True)


builtins.sys = sys
builtins.rich = rich
builtins.mm = mm
builtins.what = what
builtins.inspect = inspect
builtins.start_ipy = start_ipython
builtins.get_ipy = get_ipython
builtins.ppr = ppr
builtins.con = con
builtins.pi = pi
