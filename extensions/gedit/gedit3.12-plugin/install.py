#!/usr/bin/python

# TODO - Test on gedit-3 for windows

from __future__ import print_function

from os.path import abspath, dirname, exists, expanduser, expandvars, isdir, islink, lexists, join, normpath
from glob import glob

import errno
import os
import shutil
import stat
import sys

here = dirname(abspath(__file__))
source_dirs = [here, normpath(join(here, '../../lib'))]

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
            return (os.environ['USER'], False)

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

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

def get_dirs_nt(is_admin):
    dirs = {}

    if is_admin:
        dest_dir = expandvars("%ProgramFiles%\\gedit")
        dirs = dict(
            dest_dir=dest_dir,
            language_dir=expandvars("%ProgramFiles%\\gedit\\share\\gtksourceview-3.0\\language-specs"),
            plugin_dir=expandvars("%ProgramFiles%\\gedit\\lib\\gedit-3\\plugins"),                
        )
    else:
        dest_dir = expandvars("%UserProfile%//AppData//Roaming"),
        dirs = dict(
            dest_dir=dest_dir,
            language_dir=None,  # TODO
            plugin_dir=join(dest_dir, "gedit//plugins"),
        )
    return dirs

def get_dirs_unix(is_admin):
    if is_admin:
        if isdir('/usr/lib64'):
            dest_dir="/usr/lib64"
        else:
            dest_dir="/usr/lib"
    else:
        dest_dir=expanduser("~/.local/share")

    dirs=dict(
        dest_dir=dest_dir,
        language_dir=join(dest_dir, "gtksourceview-3.0/language-specs"),
        plugin_dir=join(dest_dir, "gedit/plugins"),
    )
    
    return dirs

if os.name == 'nt':
    get_dirs = get_dirs_nt
    get_dirs = get_dirs_unix #fix for MinGW64 use.
else:
    get_dirs = get_dirs_unix

def install_plugin(name=None, dest_dir=None, plugin_dir=None, language_dir=None, is_admin=False):
    if is_admin and not isdir(plugin_dir):
        print('%s not found' % name)
        sys.exit(1)
    else:
        if not is_admin:
            try:
                os.makedirs(plugin_dir)
            except OSError:
                pass

            if not isdir(plugin_dir):
                print('could not create destinaton dir %s' % plugin_dir)
                sys.exit(1)

    print('install %s plugin to %s' % (name, dest_dir))
    source_dir = None
    try:
        for source_dir in source_dirs:
            copytree(source_dir, plugin_dir)
    except Exception as e:
        print('error attempting to copy %s' % source_dir)
        print(e)
        sys.exit(1)

    if language_dir:
        mkdir_p(language_dir)
        shutil.copyfile(join(here, "shoebot.lang"), join(language_dir, "shoebot.lang"))
        os.system("update-mime-database %s/mime" % dest_dir)

    os.system("glib-compile-schemas %s/gedit/plugins/shoebotit" % dest_dir) ## FIXME, kind of specific to gedit...
    print('success')


def main():
    username, is_admin = has_admin()
    
    dirs = get_dirs(is_admin)
    kwargs = dict(
        name = "gedit-3.12",
        is_admin = is_admin,
        **dirs
    )

    install_plugin(**kwargs)

if __name__ == '__main__':
    main()
