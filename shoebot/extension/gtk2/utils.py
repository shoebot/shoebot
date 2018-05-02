def get_child_by_name(parent, name):
    """
    Iterate through a gtk container, `parent`,
    and return the widget with the name `name`.
    """

    # http://stackoverflow.com/questions/2072976/access-to-widget-in-gtk
    def iterate_children(widget, name):
        if widget.get_name() == name:
            return widget
        try:
            for w in widget.get_children():
                result = iterate_children(w, name)
                if result is not None:
                    return result
                else:
                    continue
        except AttributeError:
            pass

    return iterate_children(parent, name)
