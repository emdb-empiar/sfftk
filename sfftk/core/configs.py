# -*- coding: utf-8 -*-
"""
configs.py
===========

This module defines classes and functions to correctly process persistent
configurations. Please see the :doc:`guide to miscellaneous operations <misc>`
for a complete description of working with configs.
"""
from collections import OrderedDict
import os.path
import sys

from .. import BASE_DIR
from .print_tools import print_date

__author__ = 'Paul K. Korir, PhD'
__email__ = 'pkorir@ebi.ac.uk, paul.korir@gmail.com'
__date__ = '2016-08-23'
__updated__ = '2018-02-27'


class Configs(OrderedDict):
    """Class defining configs
    
    Configurations are stored in a subclass of ``OrderedDict`` with 
    appended methods for reading (``read()``), writing (``write``) and 
    clearing (``clear()``) configs.
    
    Printing an object of this class displays all configs.
    
    This class is used an argument to ``load_configs()``.
    """
    shipped_configs = os.path.join(BASE_DIR, 'sff.conf')

    def __init__(self, config_fn, *args, **kwargs):
        self.config_fn = config_fn
        super(Configs, self).__init__(*args, **kwargs)

    def clear(self):
        """Clear configs"""
        for item in self:
            del self[item]

    def read(self):
        """Read configs from file"""
        with open(self.config_fn, 'r') as f:
            for row in f:
                if row[0] == '#':  # comments
                    continue
                if row.strip() == '':  # blank lines
                    continue
                name, value = row.strip().split('=')
                self[name.strip()] = value.strip()

    def write(self):
        """Write configs to file"""
        # you can't write to shipped configs
        if self.config_fn == self.shipped_configs:
            print_date("Unable to set configs to shipped configs.")
            print_date("Please do not save configs into shipped configs. Use user or custom config files.")
            return 1

        with open(self.config_fn, 'w') as f:
            for name, value in self.iteritems():
                f.write('{}={}\n'.format(name, value))

        return 0

    def __str__(self):
        string = ""
        for name, value in self.iteritems():
            string += "{:<20} = {:<20}\n".format(name, value)
        return string[:-1]


def load_configs(args, user_folder='.sfftk', conf_fn='sff.conf', config_class=Configs):
    """Load sfftk configs (persistent arguments)
    
    It is called in ``sfftk.core.parser.py`` to get configs for the current
    command.
    
    :param args: parsed arguments
    :type args: ``argparse.Namespace``
    :param str user_folder: name of the user folder; default is *.sfftk*
    :param str conf_fn: name of the config file; default is *sff.conf*
    :param class Configs: the class defining configs
    :return dict configs: dictionary of configs
    """
    """
    :TODO: add individual args to 'if args.config_path' as an OR condition
    """
    # path to user folder
    user_folder_path = os.path.join("~", user_folder)
    # path to user config file
    user_conf_path = os.path.join(user_folder_path, conf_fn)
    # 1 - custom config path
    if args.config_path:
        # if it exists
        if os.path.exists(os.path.dirname(args.config_path)):
            config_fn = args.config_path
        # otherwise create it
        else:
            os.mkdir(os.path.dirname(args.config_path))
            config_fn = args.config_path
    else:
        # 2 - shipped configs if specified
        if args.shipped_configs:
            config_fn = config_class.shipped_configs
        # 3 - user configs
        else:
            # if it exists
            if os.path.exists(os.path.expanduser(user_folder_path)):
                config_path = os.path.expanduser(user_conf_path)
                if not os.path.exists(config_path):
                    with open(config_path, 'w') as _:
                        pass
                config_fn = config_path
            # otherwise create it
            else:
                config_path = os.path.expanduser(user_conf_path)
                # create the folder
                os.mkdir(os.path.dirname(config_path))
                # create an empty file
                with open(config_path, 'w') as _:
                    pass
                # create the config file
                config_fn = config_path

    if hasattr(args, 'verbose'):
        if args.verbose:
            print_date("Reading configs from {}".format(config_fn))

    configs = config_class(config_fn)
    configs.read()
    return configs

def list_configs(args, configs):
    """List configs in terminal
    
    :param args: parsed arguments
    :type args: `argparse.Namespace`
    :param dict configs: configuration options
    :return int status: status
    """
    print_date("Listing all {} configs...".format(len(configs)))
    # view the config object
    print >> sys.stderr, configs
    return 0

def get_configs(args, configs):
    """Get the value of the named config
    
    :param args: parsed arguments
    :type args: `argparse.Namespace`
    :param dict configs: configuration options
    :return int status: status
    """
    print_date("Getting config {}...".format(args.name))
    # obtain the named config
    try:
        config = configs[args.name]
    except KeyError:
        print_date("No config with name {}".format(args.name))
        return 1
    # view the config
    print config
    return 0

def set_configs(args, configs):
    """Set the config of the given name to have the given value
    
    :param args: parsed arguments
    :type args: `argparse.Namespace`
    :param dict configs: configuration options
    :return int status: status
    """
    print_date("Setting config {} to value {}...".format(args.name, args.value))
    # add the new config
    configs[args.name] = args.value
    # save the configs
    return configs.write()

def del_configs(args, configs):
    """Delete the named config
    
    :param args: parsed arguments
    :type args: `argparse.Namespace`
    :param dict configs: configuration options
    :return int status: status
    """
    # del the named config
    print_date("Deleting config {} having value {}...".format(args.name, configs[args.name]))
    del configs[args.name]
    # save the config
    return configs.write()

def clear_configs(args, configs):
    """Clear all configs
    
    :param args: parsed arguments
    :type args: `argparse.Namespace`
    :param dict configs: configuration options
    :return int status: status
    """
    print_date("Clearing all {} configs...".format(len(configs)))
    # empty all values
    configs.clear()
    print >> sys.stderr, configs
    # save the configs
    return configs.write()
