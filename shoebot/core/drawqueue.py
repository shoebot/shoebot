class DrawQueue:
    '''
    A list of draw commands, stored as callables that
    take a drawing context
    '''

    def __init__(self, render_funcs = None):
        self.render_funcs = render_funcs or deque()

    def append(self, render_func):
        '''
        Add a render function to the queue
        '''
        self.render_funcs.append(render_func)

    def render(self, ctx):
        '''
        Call all the render functions with ctx
        '''
        for render_func in self.render_funcs:
            render_func(ctx)
