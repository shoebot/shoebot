class DrawQueueSink(object):
    '''
    DrawQueueSink, creates parameters for use by the draw queue.
    (the render_context).

    The render context is a set of platform sepecific
    parameters used by implementations of the drawqueue,
    canvas, and sink.
    '''

    def set_bot(self, bot):
        self.bot = bot

    def render(self, size, frame, drawqueue):
        '''
        Calls implmentation to get a render context,
        passes it to the drawqueues render function
        then calls self.rendering_finished
        '''
        r_context = self.create_rcontext(size, frame)
        drawqueue.render(r_context)
        self.rendering_finished(size, frame, r_context)
        return r_context

    def create_rcontext(self, size, frame):
        '''
        Returns a cairo context for drawing this
        frame of the bot
        '''
        pass

    def rendering_finished(self, size, frame, cairo_ctx):
        pass

    def main_iteration(self):
        """
        Called from main loop, if your sink needs to handle GUI events
        do it here.

        :return:
        """
        pass
