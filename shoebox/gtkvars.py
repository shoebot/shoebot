

class VarWindow(gtk.Window):
    def __init__(self, mainwindow, **args):
        gtk.Window.__init__(self)
        self.connect("destroy", self.on_close)
        self.mainwindow = mainwindow
        layout = gtk.VBox(False); self.add(layout)
        self.sliders = dict([(n, v) for n, v in self.add_sliders(**args)])
            
        for n, v in self.sliders.items():
            v.set_digits(0)
            hb = gtk.HBox(False)
            hb.pack_start(gtk.Label(n.capitalize() + ":"), False, False, 10)
            hb.add(v); layout.add(hb)
            
        self.optInstant = gtk.CheckButton("Instant _apply", True)
        self.optShadow = gtk.CheckButton("Render _shadow", True)
        self.optFade = gtk.CheckButton("Fade _edges", True)
        self.optShadow.set_active(True); self.optFade.set_active(True)
        
        btnUpdate = gtk.Button("_Update"); 
        btnRandom = gtk.Button("_Random")
        btnUpdate.connect("pressed", lambda *w: self.mainwindow.redraw("baa"))
        btnRandom.connect("pressed", self.on_random)
        
        hb = gtk.HBox(False); layout.add(hb)
        hb.add(self.optInstant); hb.add(self.optShadow); hb.add(self.optFade)
        hb.pack_end(btnUpdate, False, False); hb.pack_end(btnRandom, False, False)

    def add_sliders(self, **args):
        for n, v in args.items():
            adj = gtk.Adjustment(v, 0, 100, 1)
            adj.connect("value-changed", lambda *a: self.render_image())
            yield n, gtk.HScale(adj)

    def get_vars(self):
        vars = dict([(n, int(v.get_adjustment().value)) for n, v in self.sliders.items()])
        return vars

    def render_image(self, update = False):
        if self.optInstant.get_active() or update:
            self.mainwindow.redraw("baa")
    
    def on_random(self, *args):
        pass

    def on_close(self, *args):
        gtk.main_quit()

