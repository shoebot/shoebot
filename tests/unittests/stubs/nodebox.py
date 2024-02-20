from unittest.mock import Mock

from shoebot.grammar import NodeBotContext  # TODO - verify if this is right instead of just NodeBot


# These stubs don't do anything, it's about making the IDE not underline "missing" imports for shoebots API.
from tests.unittests.stubs.util import stub_side_effect

for attribute in dir(NodeBotContext):
    globals()[attribute] = Mock(side_effect=stub_side_effect)
