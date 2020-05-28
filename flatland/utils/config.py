from enum import IntEnum

SIMULATION_STEPS = 4
SPACE_DAMPING = 0.9


class CollisionTypes(IntEnum):

    AGENT = 1
    CONTACT = 2
    INTERACTIVE = 3
    ZONE = 4
    GEM = 5

geometric_shapes = {'line': 2, 'circle': 60, 'triangle': 3, 'square': 4, 'pentagon': 5, 'hexagon': 6}
