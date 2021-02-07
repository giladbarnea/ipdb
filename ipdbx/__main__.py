# Copyright (c) 2011-2016 Godefroid Chapelle and ipdb development team
#
# This file is part of ipdb-extended.
# GNU package is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 2 of the License, or (at your option)
# any later version.
#
# GNU package is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License
# for more details.


import os
import sys

from contextlib import contextmanager

__version__ = '1.0.4'

from IPython import get_ipython
from IPython.core.debugger import BdbQuit_excepthook
from IPython.terminal.ipapp import TerminalIPythonApp
from IPython.terminal.embed import InteractiveShellEmbed
from IPython.terminal.debugger import Pdb

import configparser

shell = get_ipython()
if shell is None:
    # Not inside IPython
    # Build a terminal app in order to force ipython to load the
    # configuration
    ipapp = TerminalIPythonApp()
    # Avoid output (banner, prints)
    ipapp.interact = False
    ipapp.initialize(['--no-term-title'])
    shell = ipapp.shell
else:
    # Running inside IPython
    
    # Detect if embed shell or not and display a message
    if isinstance(shell, InteractiveShellEmbed):
        sys.stderr.write(
                "\nYou are currently into an embedded ipython shell,\n"
                "the configuration will not be loaded.\n\n"
                )

# Let IPython decide about which debugger class to use
# This is especially important for tools that fiddle with stdout
debugger_cls = shell.debugger_cls


def _init_pdb(context=None, prebreak=None, commands=[]) -> Pdb:
    if context is None:
        context = os.getenv("IPDB_CONTEXT_SIZE", get_context_from_config())
    
    try:
        p = debugger_cls(context=context)
    except TypeError:
        p = debugger_cls()
    p: Pdb  # probably TerminalPdb
    
    # Interesting:
    # p.postcmd(stop, line) # Hook method executed just after a command dispatch is finished.
    # p.preloop(): Hook method executed once when the cmdloop() method is called.
    # commands += [f"from rich.console import Console; con = Console(); con.print_exception(show_locals=True)"]
    p.rcLines.extend(commands)
    # TODO: use p.run() | p.runcall() | p.runeval().
    #  also checkout pdb.preloop, pdb._runscript
    #  support passing e.g. `function, arg0, arg1, kwarg='foo'` ?
    _exec_prebreak(prebreak)
    return p


def wrap_sys_excepthook():
    # make sure we wrap it only once or we would end up with a cycle
    #  BdbQuit_excepthook.excepthook_ori == BdbQuit_excepthook
    if sys.excepthook != BdbQuit_excepthook:
        BdbQuit_excepthook.excepthook_ori = sys.excepthook
        sys.excepthook = BdbQuit_excepthook


def wrap_sys_breakpointhook(*set_trace_args, **set_trace_kwargs):
    if sys.breakpointhook.__module__ == 'sys':
        if set_trace_args or set_trace_kwargs:
            from functools import partial
            set_trace_fn = partial(set_trace, *set_trace_args, **set_trace_kwargs)
        else:
            set_trace_fn = set_trace
        sys.breakpointhook = set_trace_fn


def set_trace(frame=None, context=None, cond=True, prebreak=None):
    if not cond:
        return
    wrap_sys_excepthook()
    if frame is None:
        frame = sys._getframe().f_back
    
    p = _init_pdb(context, prebreak).set_trace(frame)
    if p and hasattr(p, 'shell'):
        p.shell.restore_sys_module_state()


def _exec_prebreak(prebreak=None):
    """Can handle a python file path, string representing a python statement, or a code object"""
    # todo: support executing .ipy files
    print('ipdbx _exec_prebreak(%s)' % repr(prebreak))
    prebreak = prebreak or os.getenv("IPDB_PREBREAK", get_prebreak_from_config())
    if prebreak is None:
        return
    try:
        with open(prebreak, 'rb') as f:
            exec(compile(f.read(), prebreak, 'exec'))
    except FileNotFoundError:
        try:
            # either a string or a code object
            exec(prebreak)
        except TypeError:
            print('ipdbx _exec_prebreak(): prebreak is not None but failed compilation and execution: ', repr(prebreak))


def get_prebreak_from_config():
    """`prebreak` field can be a python file path, or string representing a python statement"""
    # todo: support multiple statements (list of strings?)
    parser = get_config()
    try:
        prebreak = parser.get('ipdb', 'prebreak')
        print(f'ipdbx get_prebreak_from_config(): prebreak from {parser.filepath}: ', prebreak)
        return prebreak
    except (configparser.NoSectionError, configparser.NoOptionError):
        print('ipdbx get_prebreak_from_config(): NO prebreak from ', getattr(parser, 'filepath', None))
        return None


def get_context_from_config():
    parser = get_config()
    try:
        return parser.getint("ipdb", "context")
    except (configparser.NoSectionError, configparser.NoOptionError):
        return 10
    except ValueError:
        value = parser.get("ipdb", "context")
        raise ValueError(f"In {parser.filepath},  context value [{value}] cannot be converted into an integer.")


class ConfigFile(object):
    """
    Filehandle wrapper that adds a "[ipdb]" section to the start of a config
    file so that users don't actually have to manually add a [ipdb] section.
    Works with configparser versions from both Python 2 and 3
    """
    
    def __init__(self, filepath):
        self.first = True
        with open(filepath) as f:
            self.lines = f.readlines()
    
    def __iter__(self):
        return self
    
    def __next__(self):
        if self.first:
            self.first = False
            return "[ipdb]\n"
        if self.lines:
            return self.lines.pop(0)
        raise StopIteration


def get_config():
    """
    Get ipdbx config file settings.
    All available config files are read.  If settings are in multiple configs,
    the last value encountered wins.  Values specified on the command-line take
    precedence over all config file settings.
    Returns: A ConfigParser object.
    """
    parser = configparser.ConfigParser()
    
    filepaths = []
    
    # Low priority goes first in the list
    for cfg_file in ("setup.cfg", ".ipdb"):
        cwd_filepath = os.path.join(os.getcwd(), cfg_file)
        if os.path.isfile(cwd_filepath):
            filepaths.append(cwd_filepath)
    
    # Medium priority (whenever user wants to set a specific path to config file)
    home = os.getenv("HOME")
    if home:
        default_filepath = os.path.join(home, ".ipdb")
        if os.path.isfile(default_filepath):
            filepaths.append(default_filepath)
    
    # High priority (default files)
    env_filepath = os.getenv("IPDB_CONFIG")
    if env_filepath and os.path.isfile(env_filepath):
        filepaths.append(env_filepath)
    
    if filepaths:
        for filepath in filepaths:
            parser.filepath = filepath
            # Users are expected to put an [ipdb] section
            # only if they use setup.cfg
            if filepath.endswith('setup.cfg'):
                with open(filepath) as f:
                    parser.read_file(f)
            else:
                parser.read_file(ConfigFile(filepath))
    return parser


def post_mortem(tb=None):
    wrap_sys_excepthook()
    p = _init_pdb()
    p.reset()
    if tb is None:
        # sys.exc_info() returns (type, value, traceback) if an exception is
        # being handled, otherwise it returns None
        tb = sys.exc_info()[2]
    if tb:
        p.interaction(None, tb)


def pm():
    post_mortem(sys.last_traceback)


def run(statement, globals=None, locals=None):
    _init_pdb().run(statement, globals, locals)


def runcall(*args, **kwargs):
    return _init_pdb().runcall(*args, **kwargs)


def runeval(expression, globals=None, locals=None):
    return _init_pdb().runeval(expression, globals, locals)


@contextmanager
def launch_ipdb_on_exception():
    try:
        yield
    except Exception:
        e, m, tb = sys.exc_info()
        print(m.__repr__(), file=sys.stderr)
        post_mortem(tb)
    finally:
        pass


_usage = """\
usage: python -m ipdbx [-m] [-c COMMAND] [-h, --help] [-V, --version] [-p, --prebreak PREBREAK] pyfile [arg] ...

Debug the Python program given by pyfile.

Initial commands are read from .pdbrc files in your home directory
and in the current directory, if they exist.  Commands supplied with
-c are executed after commands from .pdbrc files.

To let the script run until an exception occurs, use "-c continue".
To let the script run up to a given line X in the debugged file, use
"-c 'until X'"

Option -m is available only in Python 3.7 and later.

ipdbx version %s.""" % __version__


def main():
    import traceback
    import sys
    import getopt
    
    try:
        from pdb import Restart
    except ImportError:
        class Restart(Exception):
            pass
    
    if sys.version_info >= (3, 7):
        opts, args = getopt.getopt(sys.argv[1:], 'mhVp:c:', ['help', 'version', 'prebreak=', 'command='])
    else:
        opts, args = getopt.getopt(sys.argv[1:], 'hVp:c:', ['help', 'version', 'prebreak=', 'command='])
    
    commands = []
    prebreak = None
    run_as_module = False
    for opt, optarg in opts:
        if opt in ['-h', '--help']:
            print(_usage)
            sys.exit()
        elif opt in ['-c', '--command']:
            breakpoint()
            commands.append(optarg)
        elif opt in ['-p', '--prebreak']:
            prebreak = optarg
        elif opt in ['-V', '--version']:
            print(f"ipdbx version: {__version__}")
            sys.exit()
        elif opt in ['-m']:
            run_as_module = True
    
    if not args:
        print(_usage)
        sys.exit(2)
    
    mainpyfile = args[0]  # Get script filename
    if not run_as_module and not os.path.exists(mainpyfile):
        print('Error:', mainpyfile, 'does not exist')
        sys.exit(1)
    
    sys.argv = args  # Hide "pdb.py" from argument list
    
    # Replace pdb's dir with script's dir in front of module search path.
    if not run_as_module:
        sys.path[0] = os.path.dirname(mainpyfile)
    
    # Note on saving/restoring sys.argv: it's a good idea when sys.argv was
    # modified by the script being debugged. It's a bad idea when it was
    # changed by the user from the command line. There is a "restart" command
    # which allows explicit specification of command line arguments.
    pdb = _init_pdb(prebreak=prebreak, commands=commands)
    while 1:
        try:
            if run_as_module:
                pdb._runmodule(mainpyfile)
            else:
                pdb._runscript(mainpyfile)
            if pdb._user_requested_quit:
                break
            print("The program finished and will be restarted")
        except Restart:
            print("Restarting", mainpyfile, "with arguments:")
            print("\t" + " ".join(sys.argv[1:]))
        except SystemExit:
            # In most cases SystemExit does not warrant a post-mortem session.
            print("The program exited via sys.exit(). Exit status: ", end='')
            print(sys.exc_info()[1])
        except:
            traceback.print_exc()
            print("Uncaught exception. Entering post mortem debugging")
            print("Running 'cont' or 'step' will restart the program")
            t = sys.exc_info()[2]
            pdb.interaction(None, t)
            print("Post mortem debugger finished. The " + mainpyfile +
                  " will be restarted")


if __name__ == '__main__':
    main()
