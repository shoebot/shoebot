import os
import subprocess
import textwrap


def get_example_dir():
    return _example_dir


def find_example_dir():
    """
    Find examples dir .. a little bit ugly..
    """
    # Replace %s with directory to check for shoebot menus.
    code_stub = textwrap.dedent("""
    from pkg_resources import resource_filename, Requirement, DistributionNotFound
    try:
        print(resource_filename(Requirement.parse('shoebot'), '%s'))
    except DistributionNotFound:
        pass

    """)

    # Needs to run in same python env as shoebot (may be different to gedits)
    code = code_stub % 'share/shoebot/examples'
    cmd = ["python", "-c", code]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, errors = p.communicate()
    if errors:
        print('Shoebot experienced errors searching for install and examples.')
        print('Errors:\n{0}'.format(errors.decode('utf-8')))
        return None
    else:
        examples_dir = output.decode('utf-8').strip()
        if os.path.isdir(examples_dir):
            return examples_dir

        # If user is running 'setup.py develop' then examples could be right here
        # code = "from pkg_resources import resource_filename, Requirement; print resource_filename(Requirement.parse('shoebot'), 'examples/')"
        code = code_stub % 'examples/'
        cmd = ["python", "-c", code]
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        output, errors = p.communicate()
        examples_dir = output.decode('utf-8').strip()
        if os.path.isdir(examples_dir):
            return examples_dir

        if examples_dir:
            print('Shoebot could not find examples at: {0}'.format(examples_dir))
        else:
            print('Shoebot could not find install dir and examples.')


_example_dir = find_example_dir()
