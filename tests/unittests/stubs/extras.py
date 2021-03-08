from unittest.mock import Mock

# Stubs for the extra API that tests add to shoebot
from tests.unittests.stubs.util import stub_side_effect

flush_outputfile = Mock(side_effect=stub_side_effect)
outputfile = Mock(side_effect=stub_side_effect)
self = Mock(side_effect=stub_side_effect)
