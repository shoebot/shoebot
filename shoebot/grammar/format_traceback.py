import linecache
import sys
import traceback


def simple_traceback(ex, source):
    """
    Format traceback, showing line number and surrounding source.
    """
    exc_type, exc_value, exc_tb = sys.exc_info()
    exc = traceback.format_exception(exc_type, exc_value, exc_tb)

    source_arr = source.splitlines()

    # Defaults...
    exc_location = exc[-2]
    for i, err in enumerate(exc):
        if 'exec source in ns' in err:
            exc_location = exc[i + 1]
            break

    # extract line number from traceback
    fn = exc_location.split(',')[0][8:-1]
    line_number = int(exc_location.split(',')[1].replace('line', '').strip())

    # Build error messages

    err_msgs = []

    # code around the error
    err_where = ' '.join(exc[i - 1].split(',')[1:]).strip()  # 'line 37 in blah"
    err_msgs.append('Error in the Shoebot script at %s:' % err_where)
    for i in xrange(max(0, line_number - 5), line_number):
        if fn == "<string>":
            line = source_arr[i]
        else:
            line = linecache.getline(fn, i + 1)
        err_msgs.append('%s: %s' % (i + 1, line.rstrip()))
    err_msgs.append('  %s^ %s' % (len(str(i)) * ' ', exc[-1].rstrip()))

    err_msgs.append('')
    # traceback
    err_msgs.append(exc[0].rstrip())
    for err in exc[3:]:
        err_msgs.append(err.rstrip())

    return '\n'.join(err_msgs)