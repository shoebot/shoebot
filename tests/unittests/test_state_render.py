import unittest
import dataclasses

from tests.unittests.helpers import ShoebotTestCase
from shoebot.core.state.chain_dataclass import ChainDataClass, MISSING

class TestRenderState(ShoebotTestCase):
    def test_render_state(self):
        self.run_code("print(1)")


# """
# A simplified set of dataclasses are used to test the chain.
# """
#
# @dataclasses.dataclass
# class _Defaults:
#     fill: str = 'red'
#     stroke: str = 'black'
#     some_context_attr: str = 'context attribute'
#
# @dataclasses.dataclass
# class _Context:
#     fill: str = MISSING
#     stroke: str = MISSING
#     some_context_attr: str = MISSING
#
# @dataclasses.dataclass
# class _BezierPathState:
#     fill: str = 'blue'
#     stroke: str = MISSING
#
# class TestChainDataClass(unittest.TestCase):
#     def setUp(self):
#         self.defaults = _Defaults()
#         self.context = _Context()
#         self.bezier_path = _BezierPathState()
#         self.chain = ChainDataClass(self.bezier_path, self.context, self.defaults)
#
#     def test_attribute_fallback(self):
#         """Test that attributes correctly fall back through the chain."""
#         self.assertEqual(self.chain.fill, 'blue', "Should use BezierPath's fill")
#         self.assertEqual(self.chain.stroke, 'black', "Should fall back to Defaults' stroke")
#
#     def test_cannot_access_parent_attributes(self):
#         """Verify that fetching an attribute not available on the head of the chain fails"""
#         with self.assertRaises(AttributeError):
#             self.chain.some_context_attr
#
#         self.assertEqual(self.chain.parent().some_context_attr, 'context attribute', "Should not be able to access parent attributes")
#
#
#     def test_setting_attributes(self):
#         """Test that setting attributes affects the top of the chain."""
#         self.chain.fill = 'green'
#         self.assertEqual(self.chain.fill, 'green', "Should reflect updated fill color")
#
#         self.chain.__setattr__('fill', 'purple')
#         self.assertEqual(self.chain.fill, 'purple', "Direct __setattr__ should also update fill color")
#
#     def test_freezing_state(self):
#         """Test that freezing state resolves all MISSING values."""
#         self.chain.fill = MISSING  # Set to MISSING to test freeze functionality
#         self.chain.freeze()
#
#         self.assertEqual(self.chain.fill, 'red', "Freezing should resolve fill to default value")
#
#     def test_new_child(self):
#         """Test that extending the chain with new_child adds to the hierarchy."""
#         new_path_state = _BezierPathState(fill='yellow')
#         new_chain = self.chain.new_child(new_path_state)
#
#         self.assertNotEqual(new_chain.fill, self.chain.fill, "New chain should have its own top state")
#         self.assertEqual(new_chain.fill, 'yellow', "New child's fill should override existing state")


if __name__ == '__main__':
    unittest.main()
