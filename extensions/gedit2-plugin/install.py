#!/usr/bin/python

from __future__ import print_function
import glob
import os
import shutil
import stat

here = os.path.dirname(os.path.abspath(__file__))
source_dirs = [here, os.path.normpath(os.path.join(here, '../lib'))]


def has_admin():
    import os

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
        return "C:\\Program Files\\gedit\\lib\\gedit-2\\plugins"
    else:
        return os.path.expanduser("~/.gnome2/gedit/gedit-2/plugins")


def plugins_dir_unix(is_admin):
    if is_admin:
        if os.path.isdir('/usr/lib64'):
            return "/usr/lib64/gedit-2/plugins"
        else:
            return "/usr/lib/gedit-2/plugins"
    else:
        return os.path.expanduser("~/.gnome2/gedit/plugins")


def plugins_dir(is_admin):
    if os.name == 'nt':
        return plugins_dir_nt(is_admin)
    else:
        return plugins_dir_unix(is_admin)


def copytree(src, dst, symlinks=False, ignore=None):
    """
    copytree that works even if folder already exists
    """
    # http://stackoverflow.com/questions/1868714/how-do-i-copy-an-entire-directory-of-files-into-an-existing-directory-using-pyth
    if not os.path.exists(dst):
        os.makedirs(dst)
        shutil.copystat(src, dst)
    lst = os.listdir(src)
    if ignore:
        excl = ignore(src, lst)
        lst = [x for x in lst if x not in excl]
    for item in lst:
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if symlinks and os.path.islink(s):
            if os.path.lexists(d):
                os.remove(d)
            os.symlink(os.readlink(s), d)
            try:
                st = os.lstat(s)
                mode = stat.S_IMODE(st.st_mode)
                os.lchmod(d, mode)
            except:
                pass  # lchmod not available
        elif os.path.isdir(s):
            copytree(s, d, symlinks, ignore)
        else:
            shutil.copy2(s, d)


def main():
    username, is_admin = has_admin()
    dest_dir = plugins_dir(is_admin)

    if is_admin and not os.path.isdir(dest_dir):
        print('gedit not found')
        sys.exit(1)
    else:
        if not is_admin:
            try:
                os.makedirs(dest_dir)
            except OSError:
                pass

            if not os.path.isdir(dest_dir):
                print('could not create destinaton dir %s' % dest_dir)
                sys.exit(1)

    for source_dir in source_dirs:
        copytree(source_dir, dest_dir)


if __name__ == '__main__':
    main()
