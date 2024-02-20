import cairo

from shoebot.core.renderer.renderer import Renderer
from shoebot.core.state.color_data import ColorData
from shoebot.core.state.context import ContextState
from shoebot.core.state.stateful import get_state_stack
from shoebot.graphics import ARC, MOVETO, RMOVETO, LINETO, RLINETO, CURVETO, RCURVETO, CLOSE, BezierPath, ClippingPath


class CairoRenderer(Renderer):
    """
    Draw shoebot graphic objects (BezierPath, Image, etc) on to a cairo Context.
    """
    # TODO - should the __init__ create the ctx or should it be passed in as needed ?

    def __init__(self, ctx: cairo.Context):
        """
        Create a CairoRenderer that will draw on the given cairo Context.

        :param ctx: a cairo Context to draw on.
        """
        super().__init__(ctx)

    def render_pathelement(self, element):
        """
        Run command corresponding to this PathElement on a cairo Context.
        """
        ctx = self.target
        if element.cmd == ARC:
            ctx.arc(element.x, element.y, element.radius, element.start, element.end)
        elif element.cmd == MOVETO:
            ctx.move_to(element.x, element.y)
        elif element.cmd == RMOVETO:
            # actually dx, dy
            ctx.rel_move_to(element.x, element.y)
        elif element.cmd == LINETO:
            ctx.line_to(element.x, element.y)
        elif element.cmd == RLINETO:
            # actually dx, dy
            ctx.rel_line_to(element.x, element.y)
        elif element.cmd == CURVETO:
            ctx.curve_to(element.x, element.y,
                         element.ctrl1.x, element.ctrl1.y,
                         element.ctrl2.x, element.ctrl2.y)
        elif element.cmd == RCURVETO:
            # actually dx, dy
            ctx.rel_curve_to(element.x, element.y,
                             element.ctrl1.x, element.ctrl1.y,
                             element.ctrl2.x, element.ctrl2.y)
        elif element.cmd == CLOSE:
            ctx.close_path()
        else:
            raise ValueError("Unknown command: %s" % element.cmd)

    def render_bezierpath(self, path, state):
        ctx = self.target
        for element in path._elements:
            self.render_pathelement(element)

        stroke_width = state.stroke_width

        # TODO - currently only supports rendering to RGBA
        state_stack = get_state_stack(path)

        stroke = state_stack.stroke.as_rgba()
        fill = state_stack.fill.as_rgba()

        if fill.a > 0.0 and stroke.a > 0.0:
            if stroke.a == 1.0:
                print("DRAW - fill and solid stroke")
                # Fast path if no alpha in stroke
                # TODO:  Probably need color handling that knows about things other than rgba
                ctx.set_source_rgba(*fill.channels)
                ctx.fill_preserve()

                ctx.set_source_rgba(*stroke.channels)
                ctx.set_line_width(stroke_width)
                ctx.stroke()
            else:
                print("DRAW - fill an stroke")
                # Draw fill onto intermediate surface so stroke does not overlay fill
                ctx.push_group()

                ctx.set_source_rgba(*fill.channels)
                ctx.fill_preserve()

                ctx.set_source_rgba(*stroke.channels)
                ctx.set_operator(cairo.OPERATOR_SOURCE)
                ctx.set_line_width(stroke_width)
                ctx.stroke()

                ctx.pop_group_to_source()
                ctx.paint()
        elif fill.a:
            print("nostroke, fill")
            # Stroke has no alpha but fill does.
            ctx.set_source_rgba(*fill.channels)
            ctx.fill()
        elif stroke.a:
            # Fill has no alpha but stroke does.
            print("stroke, nofill")
            ctx.set_source_rgba(*stroke.channels)
            ctx.set_line_width(stroke_width)
            ctx.stroke()

    def render_clippingpath(self, path):
        # TODO test
        ctx = self.target
        for element in path._elements:
            self.render_pathelement(element)
        ctx.clip()

    def render_background(self, color: ColorData):
        # TODO - other kinds of backgrounds, and preserving the current background.
        ctx = self.target
        if color.channel_names == "rgb":
            ctx.set_source_rgb(*color.channels)
            ctx.paint()
            return

        rgba = color.as_rgba()
        if rgba.a == 0.0:
            return

        ctx.set_source_rgba(*rgba.channels)
        ctx.paint()

    def render_canvas(self, canvas):
        print(f"render_canvas [{len(canvas.commands)} commands]")
        for command, state in canvas.commands:
            if isinstance(command, ClippingPath):
                self.render_clippingpath(command, state)
            elif isinstance(command, BezierPath):
                self.render_bezierpath(command, state)
            else:
                raise NotImplementedError(f"Unknown command type {command}")

    def render_context(self, state: ContextState):
        # TODO - perhaps this should be the main entrypoint.
        if state.background is not None:
            self.render_background(state.background)

    def __del__(self):
        del self.target


