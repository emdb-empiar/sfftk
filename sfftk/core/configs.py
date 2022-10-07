"""
``sfftk.core.configs``
======================

This module defines classes and functions to correctly process persistent
configurations. Please see the :doc:`guide to miscellaneous operations <misc>`
for a complete description of working with configs.
"""
import os
import shutil
import sys

from sfftkrw.core.print_tools import print_date

from .. import BASE_DIR

__author__ = 'Paul K. Korir, PhD'
__email__ = 'pkorir@ebi.ac.uk, paul.korir@gmail.com'
__date__ = '2016-08-23'
__updated__ = '2018-02-27'


class Configs(dict):
    """Class defining configs

    Configurations are stored in a subclass of :py:class:`OrderedDict` (normal :py:class:`dict` for Python 3.7+) with
    appended methods for reading (:py:meth:`.Configs.read()`), writing (:py:meth:`.Configs.write`) and
    clearing (:py:meth:`.Configs.clear`) configs.

    Printing an object of this class displays all configs.

    This class is used an argument to :py:func:`.configs.load_configs`.
    """
    shipped_configs = os.path.join(BASE_DIR, 'sff.conf')

    def __init__(self, config_fn, *args, **kwargs):
        self.config_fn = config_fn
        super(Configs, self).__init__(*args, **kwargs)

    def clear(self):
        """Clear configs"""
        items_to_clear = [item for item in self]
        for item in items_to_clear:
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
            for name, value in self.items():
                f.write('{}={}\n'.format(name, value))

        return 0

    def __str__(self):
        string = ""
        for name, value in self.items():
            string += "{:<20} = {:<20}\n".format(name, value)
        return string[:-1]


def get_config_file_path(args, user_folder='~/.sfftk', user_conf_fn='sff.conf', config_class=Configs):
    """A function that returns the right config path to use depending on the command specified

    The user may specify

    .. code-block:: bash

        sff <cmd> [<sub_cmd>] [--shipped-configs|--config-path] [args...]`

    and we have to decide which configs to use.

    Example:

    - View the notes in the file. If user configs are available use them otherwise use shipped configs

    .. code-block:: bash

        sff notes list file.json

    - View the notes in the file but ONLY use shipped configs.

    .. code-block:: bash

        sff notes list --shipped-configs file.json

    - View the notes in the file but ONLY use custom configs at path

    .. code-block:: bash

        sff notes list --config-path /path/to/sff.conf file.json

    - Get available configs. First check for user configs and fall back on shipped configs

    .. code-block:: bash

        sff config get --all

    - Get configs from the path

    .. code-block:: bash

        sff config get --config-path /path/to/sff.conf --all
        # ignore shipped still!
        sff config get --config-path /path/to/sff.conf --shipped-configs --all

    - Get shipped configs even if user configs exist

    .. code-block:: bash

        sff config get --shipped-configs --all

    - Set configs to user configs. If user configs don't exist copy shipped and add the new config.

    .. code-block:: bash

        sff config set NAME VALUE

    - Set configs to config path. Ignore user and shipped configs

    .. code-block:: bash

        sff config set --config-path /path/to/sff.conf NAME VALUE

    - Fail! Shipped configs are read-only

    .. code-block:: bash

        sff config set --shipped-configs NAME VALUE

    :param args:
    :param user_folder:
    :param user_conf_fn:
    :return:
    """
    shipped_configs = config_class.shipped_configs
    user_configs = os.path.expanduser(os.path.join(user_folder, user_conf_fn))
    config_file_path = None
    if args.subcommand == 'config':
        # read-only: get
        if args.config_subcommand == 'get':
            if args.config_path is not None:
                config_file_path = args.config_path
            elif args.shipped_configs:
                config_file_path = shipped_configs
            elif os.path.exists(user_configs):
                config_file_path = user_configs
            else:
                config_file_path = shipped_configs
        # read-write: set, del
        else:
            if args.config_path is not None:
                config_file_path = args.config_path
            elif args.shipped_configs:
                config_file_path = None
            elif os.path.exists(user_configs):
                config_file_path = user_configs
            elif not os.path.exists(user_configs):
                if args.verbose:
                    print_date("User configs not found")
                try:
                    # make the dir if it doesn't exist
                    os.mkdir(os.path.dirname(user_configs))
                except OSError:
                    pass
                # copy the shipped configs to user configs
                if args.verbose:
                    print_date("Copying shipped configs to user configs...")
                shutil.copy(config_class.shipped_configs, user_configs)
                config_file_path = user_configs
    else:
        if args.config_path is not None:
            config_file_path = args.config_path
        elif args.shipped_configs:
            config_file_path = config_class.shipped_configs
        elif os.path.exists(user_configs):
            config_file_path = user_configs
        else:
            config_file_path = config_class.shipped_configs
    return config_file_path


def load_configs(config_file_path, config_class=Configs):
    """Load configs from the given file

    :param str config_file_path: a path to a file with configs
    :param class config_class: the config class; default: Configs
    :return configs: the configs
    :rtype configs: Configs
    """
    configs = config_class(config_file_path)
    configs.read()
    return configs


def get_configs(args, configs):
    """Get the value of the named config

    :param args: parsed arguments
    :type args: `argparse.Namespace`
    :param dict configs: configuration options
    :return status: status
    :rtype status: int
    """
    if args.all:
        print_date("Listing all {} configs...".format(len(configs)))
        # view the config object
        # fixme: use print_date
        print(configs, file=sys.stderr)
    else:
        print_date("Getting config {}...".format(args.name))
        # obtain the named config
        try:
            config = configs[args.name]
        except KeyError:
            print_date("No config with name {}".format(args.name))
            return 1
        # view the config
        # fixme: use print_date
        print(config)
    return 0


def set_configs(args, configs):
    """Set the config of the given name to have the given value

    :param args: parsed arguments
    :type args: `argparse.Namespace`
    :param dict configs: configuration options
    :return status: status
    :rtype status: int
    """
    print_date("Setting config {} to value {}...".format(args.name, args.value))
    # add the new config
    configs[args.name] = args.value
    if args.verbose:
        # fixme: use print_date
        print(configs)
    # save the configs
    return configs.write()


def del_configs(args, configs):
    """Delete the named config

    :param args: parsed arguments
    :type args: :py:class:`argparse.Namespace`
    :param dict configs: configuration options
    :return status: status
    :rtype status: int
    """
    if args.all:
        print_date("Deleting all {} configs...".format(len(configs)))
        # empty all values
        configs.clear()
    else:
        # del the named config
        print_date("Deleting config {} having value {}...".format(args.name, configs[args.name]))
        try:
            del configs[args.name]
        except KeyError:
            print_date("No config with name {}".format(args.name))
            return 65
    if args.verbose:
        # fixme: use print_date
        print(configs)
    # save the config
    return configs.write()
