import os.path

NODEBOX = 'nodebox'
DRAWBOT = 'drawbot'
SHOEBOT = 'shoebot'

def run(src, grammar = NODEBOX, format = None, outputfile = 'output.svg', iterations = None, window = False):
    '''
    Convenience function to make it easy to start bots from external programs
    '''
    from core import Context
    from core import CairoCanvas
    from core import CairoImageSink
    from gui import ShoebotWidget

    from core import NodeBot
    ###from drawbot import Drawbot ###TODO

    if window:
        if os.path.isfile(src):
            title = os.path.splitext(os.path.basename(src))[0] + ' - Shoebot'
        else:
            title = 'Untitled - Shoebot'
        cairo_sink = ShoebotWidget().as_window(title)
    else:
        if iterations is None:
            iterations = 1
        cairo_sink = CairoImageSink(outputfile, format, iterations > 1)
    bot_classes = {
        #DRAWBOT : Drawbot,
        NODEBOX : NodeBot,
        #SHOEBOT : Shoebot,
    }
    context = Context(bot_classes[grammar], CairoCanvas(cairo_sink, enable_cairo_queue = True))
    context.run(src, iterations, True)
