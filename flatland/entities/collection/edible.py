from flatland.entities.entity import Entity
from flatland.utils.definitions import CollisionTypes


class Edible(Entity):

    entity_type = 'edible'
    interactive = True

    def __init__(self, initial_position, default_config_key=None, **kwargs):
        """ Base class for edible entities

        Edible entity provides a reward to the agent that eats it, then shrinks in size, mass, and available reward.

        Args:
            initial_position: initial position of the entity. can be list [x,y,theta], AreaPositionSampler or Trajectory
            default_config_key: can be 'apple' or 'rotten_apple'
            **kwargs: other params to configure entity. Refer to Entity class

        Keyword Args:
            shrink_ratio_when_eaten: When eaten by an agent, the mass, size, and reward are multiplied by this ratio.
                Default: 0.9
            initial_reward: Initial reward of the edible
            min_reward: When reward is lower than min_reward, the edible entity disappears

        """

        default_config = self._parse_configuration('interactive', default_config_key)
        entity_params = {**default_config, **kwargs}

        super().__init__(initial_position=initial_position, **entity_params)

        self.shrink_ratio_when_eaten = entity_params['shrink_ratio_when_eaten']
        self.min_reward = entity_params['min_reward']
        self.initial_reward = entity_params['initial_reward']

        self.initial_width, self.initial_length = self.width, self.length
        self.initial_radius = self.radius
        self.initial_mass = self.mass

        self.reward = self.initial_reward

        self.pm_interaction_shape.collision_type = CollisionTypes.EDIBLE

    def generate_shapes_and_masks(self):

        self.pm_visible_shape = self.create_pm_shape()
        self.visible_mask = self.create_mask()

        self.pm_interaction_shape = self.create_pm_shape(is_interactive=True)
        self.pm_interaction_shape.collision_type = CollisionTypes.EDIBLE
        self.interaction_mask = self.create_mask(is_interactive=True)

        self.pm_elements = [self.pm_body, self.pm_visible_shape, self.pm_interaction_shape]

        if self.graspable:
            self.pm_grasp_shape = self.create_pm_shape(is_interactive=True)
            self.pm_grasp_shape.collision_type = CollisionTypes.GRASPABLE
            self.grasp_mask = self.create_mask(is_interactive=True)
            self.pm_elements.append(self.pm_grasp_shape)

    def get_reward(self):

        return self.reward

    def eats(self):

        # Change reward, size and mass
        previous_position = self.pm_body.position
        previous_angle = self.pm_body.angle

        self.reward = self.reward*self.shrink_ratio_when_eaten

        if self.movable:
            self.mass = self.mass * self.shrink_ratio_when_eaten

        self.pm_body = self.create_pm_body()
        # self.pm_elements = [self.pm_body]

        self.width = self.width * self.shrink_ratio_when_eaten
        self.length = self.length * self.shrink_ratio_when_eaten
        self.radius = self.radius * self.shrink_ratio_when_eaten
        self.interaction_width = self.width + self.interaction_range
        self.interaction_length = self.length + self.interaction_range
        self.interaction_radius = self.radius + self.interaction_range

        self.pm_body.position = previous_position
        self.pm_body.angle = previous_angle

        self.generate_shapes_and_masks()

        if self.initial_reward > 0 and self.reward > self.min_reward:
            return False
        elif self.initial_reward < 0 and self.reward < self.min_reward:
            return False
        else:
            return True

    def reset(self, new_position=None):

        self.reward = self.initial_reward
        self.mass = self.initial_mass

        self.width, self.length = self.initial_width, self.initial_length
        self.radius = self.initial_radius

        self.interaction_width = self.width + self.interaction_range
        self.interaction_length = self.length + self.interaction_range
        self.interaction_radius = self.radius + self.interaction_range

        self.pm_body = self.create_pm_body()

        super().reset()

        self.generate_shapes_and_masks()


class Apple(Edible):

    def __init__(self, initial_position, **kwargs):
        """ Edible entity that provides a positive reward

        Default: Green Circle of radius 10, with an initial_reward of 30, a min reward of 5, and a shrink_ratio of 0.9
        """

        super(Apple, self).__init__(initial_position=initial_position, default_config_key='apple', **kwargs)


class RottenApple(Edible):

    def __init__(self, initial_position, **kwargs):

        """ Edible entity that provides a positive reward

        Default: Brown Circle of radius 10, with an initial_reward of -30, a min reward of -5, and a shrink_ratio of 0.9
        """

        super(RottenApple, self).__init__(initial_position=initial_position, default_config_key='rotten_apple',
                                          **kwargs)
