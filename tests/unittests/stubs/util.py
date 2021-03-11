def stub_side_effect(name):
    """
    If a stub is called by accident raise an exception.
    """

    def run():
        raise NotImplemented(f"{name} stub should not be directly executed.")

    return run
