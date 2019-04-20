class TestSequence(type):
    """
    Metaclass to create a test sequence.
    """

    def __new__(mcs, name, bases, dct):
        for k, v in dct.items():
            if k.startswith("test"):
                del (dct[k])
                name_template, creation_func, sequence = v

                for data in sequence:
                    test_name = name_template % data
                    test_func = creation_func(data)
                    dct[test_name] = test_func

        return type.__new__(mcs, name, bases, dct)
