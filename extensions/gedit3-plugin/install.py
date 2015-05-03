#!/usr/bin/python

# TODO - Test on gedit-3 for windows

from __future__ import print_function

from os.path import abspath, dirname, exists, expanduser, expandvars, isdir, islink, lexists, join, normpath

import os
import shutil
import stat
import sys

here = dirname(abspatb(__file__))
source_dirs = [here, normpath(join(here, '../lib'))]
plugin_name='gedit-3'


def has_admin():
    if os.name == 'nt':
        try:
            # only windows users with admin privileges can read the C:\windows\temp
            temp = os.listdir(os.sep.join([os.environ.get('SystemRoot', 'C:\\windows'), 'temp']))
        except:
            return (os.environ['USERNAME'], False)
        else:
            return (os.environ['USERNAME'], True)
    else:
        if 'SUDO_USER' in os.environ and os.geteuid() == 0:
            return (os.environ['SUDO_USER'], True)
        else:
            return (os.environ['USERNAME'], False)


def plugins_dir_nt(is_admin):
    if is_admin:
        return expandvars("%ProgramFiles%\\gedit\\lib\\gedit-3\\plugins")
    else:
        return expandvars("%UserProfile%//AppData//Roaming//gedit//plugins")


def dest_dir_unix(is_admin):
    # TODO - See if this can generalise to Windows too
    if is_admin:
        if isdir('/usr/lib64'):
            return "/usr/lib64"
        else:
            return "/usr/lib"
    else:
        return expanduser("~/.local/share")

def plugins_dir_unix(is_admin):
    return join(dest_dir_unix(), "gedit/plugins")

def plugins_dir(is_admin):
    if os.name == 'nt':
        return plugins_dir_nt(is_admin)
    else:
        return plugins_dir_unix(is_admin)

def language_dir(is_admin):
    # TODO
    if os.name == 'nt':
        if is_admin:
            return expandvars("%ProgramFiles%\\gedit\\share\\gtksourceview-3.0\\language-specs")
    else:
        return join(dest_dir_unix(), "gtksourceview-3.0/language-specs")

def copytree(src, dst, symlinks=False, ignore=None):
    """
    copytree that works even if folder already exists
    """
    # http://stackoverflow.com/questions/1868714/how-do-i-copy-an-entire-directory-of-files-into-an-existing-directory-using-pyth
    if not exists(dst):
        os.makedirs(dst)
        shutil.copystat(src, dst)
    lst = os.listdir(src)
    if ignore:
        excl = ignore(src, lst)
        lst = [x for x in lst if x not in excl]
    for item in lst:
        s = join(src, item)
        d = join(dst, item)
        if symlinks and islink(s):
            if lexists(d):
                os.remove(d)
            os.symlink(os.readlink(s), d)
            try:
                st = os.lstat(s)
                mode = stat.S_IMODE(st.st_mode)
                os.lchmod(d, mode)
            except:
                pass  # lchmod not available
        elif isdir(s):
            copytree(s, d, symlinks, ignore)
        else:
            shutil.copy2(s, d)


def main():
    username, is_admin = has_admin()
    dest_dir = plugins_dir(is_admin)

    if is_admin and not isdir(dest_dir):
        print('gedit not found')
        sys.exit(1)
    else:
        if not is_admin:
            try:
                os.makedirs(dest_dir)
            except OSError:
                pass

            if not isdir(dest_dir):
                print('could not create destinaton dir %s' % dest_dir)
                sys.exit(1)

    print('install %s plugin to %s' % (plugin_name, dest_dir))
    source_dir = None
    try:
        for source_dir in source_dirs:
            copytree(source_dir, dest_dir)
    except Exception as e:
        print('error attempting to copy %s' % source_dir)
        print(e)
        sys.exit(1)

    dest_dir = language_dir(is_admin)
    if dest_dir:
        shutil.copyfile("shoebot.lang", dest_dir)
    print('success')


if __name__ == '__main__':
    main()
