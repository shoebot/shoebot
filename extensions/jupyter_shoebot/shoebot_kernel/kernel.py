from ipykernel.kernelbase import Kernel
import shoebot
import os
import urllib
import base64


def surface_to_png(surface):
    # https://ipython-books.github.io/16-creating-a-simple-kernel-for-jupyter/
    from io import BytesIO
    b = BytesIO()
    surface.write_to_png(b)
    b.seek(0)
    return urllib.quote_plus(
        base64.b64encode(b.getvalue()))


class ShoebotKernel(Kernel):
    implementation = 'shoebot'
    implementation_version = '1.0'
    language = 'no-op'
    language_version = '0.1'
    language_info = {
        'name': 'Any text',
        'mimetype': 'text/plain',
        'file_extension': '.txt',
    }
    banner = "Shoebot kernel - Run Shoebot scripts"

    def do_execute(self, code, silent, store_history=True, user_expressions=None,
                   allow_stdin=False):

        bot = shoebot.create_bot(outputfile='_temp.png')
        exc = None
        try:
            bot.run(code, break_on_error=True)
            png_data = open('_temp.png', 'r').read()
            # quote and encode PNG data for passing JSON response to Jupyter
            png_string = urllib.quote_plus(base64.b64encode(png_data))
        except Exception as e:
            import traceback
            exc = traceback.format_exc(e)

        if not silent:
            if exc:
                stream_content = {'name': 'stdout', 'text': exc}
                self.send_response(self.iopub_socket, 'stream', stream_content)

            else:
                content = {'source': 'kernel',
                           'data': {'image/png': png_string},
                           'metadata': {
                               'image/png': {
                                   'width': bot.WIDTH,
                                   'height': bot.HEIGHT
                               }}
                           }
                self.send_response(self.iopub_socket, 'display_data', content)
        os.remove('_temp.png')

        return {'status': 'ok',
                # The base class increments the execution count
                'execution_count': self.execution_count,
                'payload': [],
                'user_expressions': {},
                }
