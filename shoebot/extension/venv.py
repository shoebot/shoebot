import os


def is_virtualenv(directory, executable='python'):
    """
    :param directory: base directory of python environment
    """
    path = os.path.join(directory, 'bin', executable)
    return os.path.isfile(path)


def virtualenv_has_script(script):
    """
    :param script: script to look for in bin folder
    """

    def f(venv):
        path = os.path.join(venv, 'bin', script)
        if os.path.isfile(path):
            return True

    return f


def virtualenvwrapper_envs(filter=None):
    """
    :return: python environments in ~/.virtualenvs

    :param filter: if this returns False the venv will be ignored

    >>> virtualenvwrapper_envs(filter=virtualenv_has_script('pip'))
    """
    vw_root = os.path.abspath(os.path.expanduser(os.path.expandvars('~/.virtualenvs')))
    venvs = []
    for directory in os.listdir(vw_root):
        venv = os.path.join(vw_root, directory)
        if os.path.isdir(os.path.join(venv)):
            if filter and not filter(venv):
                continue
            venvs.append(venv)
    return sorted(venvs)
