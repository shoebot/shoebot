from pathlib import Path


class Output:
    # TODO move somewhere more general
    """
    An "Output" handles creation and destruction of renderers.

    Renderer creation:
    Renderers require a size to be known, which is only known when size() is called in a bot
    or if size was never called and default size can be used.

    Once size is known renderers can be created.

    Renderer destruction:
    In some cases extra work needs to be performed before destroying a renderer - e.g. saving
    to a file, the Output implementation handles this.
    """

    def __init__(self):
        self.renderer = None

    def destroy_renderer(self):
        """
        Implementing classes can override this to perform extra work before destroying the renderer,
        e.g. saving to a file.
        """
        del self.renderer

class FileOutput(Output):
    """
    Outputs that save to a file or series of files can
    extend this class and will be automatically found by
    callers to outputs_for_format.
    """
    SUPPORTED_FILE_FORMATS = None
    TARGET_IS_FILE = True

    def __init__(self, filename_template):
        # Use pathlib to parse the filename template for it's format
        self.filename_template = filename_template
        self.format = Path(filename_template).suffix[1:]
        assert self.format in self.SUPPORTED_FILE_FORMATS

    @classmethod
    def outputs_for_format(cls, file_format):
        for output_class in FileOutput.__subclasses__():
            if output_class.SUPPORTED_FILE_FORMATS and file_format in output_class.SUPPORTED_FILE_FORMATS:
                yield output_class





def get_matching_outputs(windowed=None, file_format=None):
    pass

def get_output(args):
    if args.outputfile:
        file_format = Path(args.outputfile).suffix[1:]
        for output_type in FileOutput.outputs_for_format(file_format):
            return output_type(args.outputfile)
        raise ValueError(f"Unsupported output file format: {args.outputfile}")

def get_first_working_output():
    for k, w in prefs or DEFAULT_PREFS.items():
        pass
    if args.outputfile:
        file_format = Path(args.outputfile).suffix[1:]
        for output_type in FileOutput.outputs_for_format(file_format):
            return output_type(args.outputfile)
        raise ValueError(f"Unsupported output file format: {file_format}")