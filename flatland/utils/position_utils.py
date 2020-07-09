from collections.abc import Generator
import numpy as np
import random, math
from .definitions import geometric_shapes


class PositionAreaSampler:
    """ Sampler for a random position within a particular area

    Example:
        area_1 = PositionAreaSampler(area_shape='rectangle', center=[70, 70], shape=[30, 100])
        area_2 = PositionAreaSampler(area_shape='gaussian', center=[150, 50], variance = 300, radius=60)

    """
    def __init__(self, center, area_shape, **kwargs):
        """

        Args:
            center (:obj: list of :obj: int): x, y coordinates of the center of the area
            area_shape (str): 'circle', 'gaussian' or 'rectangle'
            **kwargs: Keyword arguments depending on the area_shape

        Keyword Arguments:
            width_length (:obj: list of :obj: int): Width and Length of the rectangle shape
            radius (int): radius of the gaussian and circle shape
            variance (int): variance of the gaussian
            theta_range (int): min and max sampled angle

        """

        self.area_shape = area_shape
        self.center = center

        self.theta_min, self.theta_max = kwargs.get('theta_range', [-math.pi, math.pi])

        # Area shape
        if self.area_shape == 'rectangle':
            self.width, self.length = kwargs['width_length']

        elif self.area_shape == 'circle':
            self.radius = kwargs['radius']

        elif self.area_shape == 'gaussian':
            self.radius = kwargs['radius']
            self.variance = kwargs['variance']

        else:
            raise ValueError('area shape not implemented')

    def sample(self, center=None):
        """

        Args:
            center:

        Returns:
            position ('obj'list of 'obj'float): (x,y,theta) position sampled

        """
        x, y, theta = 0, 0, 0

        if center is not None:
            self.center = center

        if self.area_shape == 'rectangle':
            x = random.uniform(self.center[0] - self.width/2, self.center[0] + self.width/2)
            y = random.uniform(self.center[1] - self.length/2, self.center[1] + self.length/2)
            theta = random.uniform(self.theta_min, self.theta_max)

        elif self.area_shape == 'circle':

            x = math.inf
            y = math.inf
            theta = random.uniform(self.theta_min, self.theta_max)

            while (x - self.center[0]) ** 2 + (y - self.center[1]) ** 2 > self.radius ** 2:
                x = random.uniform(self.center[0] - self.radius / 2, self.center[0] + self.radius / 2)

                y = random.uniform(self.center[1] - self.radius / 2, self.center[1] + self.radius / 2)

        elif self.area_shape == 'gaussian':

            x = math.inf
            y = math.inf
            theta = random.uniform(self.theta_min, self.theta_max)

            while (x - self.center[0])**2 + (y - self.center[1])**2 > self.radius**2:

                x, y = np.random.multivariate_normal(self.center, [[self.variance, 0], [0, self.variance]])

        return x, y, theta


class Trajectory(Generator):

    """ Trajectory is a generator which is used to define a list of positions that an entity follows.

    Example:
    trajectory = Trajectory('waypoints', 300, waypoints=[[20, 20], [20, 180], [180,180], [180,20]])
    trajectory = Trajectory('shape', 200, 8, shape='square', center=[100, 70, 0], radius=50)

    """

    def __init__(self, trajectory_type, trajectory_duration, n_rotations=0, index_start=0, **kwargs):
        """ Trajectory follows waypoints or shape.

        Args:
            trajectory_type (str): 'waypoints' or 'shape'
            trajectory_duration (:obj:'int'): number of steps to complete a full trajectory
            n_rotations (:obj:'int'): number of entity rotations during one full trajectory.
                Default is 0.
            index_start (:obj:'int'): offset for the start of the trajectory
                Default is 0.
            **kwargs: Arbitrary keyword arguments

        Keyword Arguments:
            shape (str): 'line', 'circle', 'square', 'pentagpn', 'hexagon'
            center (:obj:'list' of :obj:'int'): if shape is used, (x,y,orientation) of the center of a shape
            radius (:obj:'int'): if shape is used, radius of the shape that entity is following
            waypoints (:obj:'list' of :obj:'int'): if 'waypoints' is used, list of waypoints
            counter_clockwise (:obj:'bool): direction of the trajectory. Default is False

        """

        self.trajectory_duration = trajectory_duration
        self.trajectory_type = trajectory_type
        self.n_rotations = n_rotations

        # Calculate waypoints when trajectory_type is shape
        if self.trajectory_type is 'shape':
            self.shape = kwargs['shape']
            self.radius = kwargs['radius']
            self.center = kwargs['center']
            self.orientation_shape = self.center[2]
            self.waypoints = self.generate_geometric_waypoints()

        elif self.trajectory_type is 'waypoints':
            self.waypoints = kwargs['waypoints']

        # Generate all trajectory points based on waypoints
        self.trajectory_points = self.generate_trajectory()

        self.index_start = index_start
        self.current_index = self.index_start

        self.counter_clockwise = kwargs.get('counter_clockwise', False)

    @property
    def index_start(self):

        if self.trajectory_type is 'shape':
            number_sides = geometric_shapes[self.shape]

            # Center the starting point on the x axis, angle 0
            return self._index_start - int(len(self.trajectory_points) / number_sides / 2)

        else:
            return self._index_start

    @index_start.setter
    def index_start(self, index_start):

        self._index_start = index_start

    def generate_geometric_waypoints(self):

        number_sides = geometric_shapes[self.shape]
        offset_angle = math.pi / number_sides + self.orientation_shape

        waypoints = []
        for n in range(number_sides):
            waypoints.append([self.center[0] + self.radius * math.cos(n * 2 * math.pi / number_sides + offset_angle),
                              self.center[1] + self.radius * math.sin(n * 2 * math.pi / number_sides + offset_angle),
                              0])

        return waypoints[::-1]

    def generate_trajectory(self):

        shifted_waypoints = self.waypoints[1:] + self.waypoints[:1]
        total_length = sum([math.sqrt((x1[0] - x2[0])**2 + (x1[1] - x2[1])**2)
                            for x1, x2 in zip(self.waypoints, shifted_waypoints)])

        trajectory_points = []

        for pt_1, pt_2 in zip(self.waypoints, shifted_waypoints):

            distance_between_points = math.sqrt((pt_1[0] - pt_2[0])**2 + (pt_1[1] - pt_2[1])**2)

            # Ratio of trajectory points between these two waypoints
            ratio_points = distance_between_points / total_length
            n_points = int(self.trajectory_duration *ratio_points)

            pts_x = [pt_1[0] + x * (pt_2[0] - pt_1[0]) / n_points for x in range(n_points)]
            pts_y = [pt_1[1] + x * (pt_2[1] - pt_1[1]) / n_points for x in range(n_points)]

            for i in range(n_points):
                trajectory_points.append([pts_x[i], pts_y[i], 0])

        for pt_index in range(len(trajectory_points)):

            angle = (pt_index * self.n_rotations) * (2*math.pi) / len(trajectory_points) % (2*math.pi)

            trajectory_points[pt_index][2] = angle

        return trajectory_points

    def send(self, ignored_args):
        """ Function for generator. Sends current position, then changes current position depending on rotation side.

        Args:
            ignored_args:

        Returns:
            position ('obj' list of :obj:'int'): next (x,y,theta) position

        """
        returned_value = self.trajectory_points[self.current_index]

        if self.counter_clockwise:
            self.current_index -= 1
            if self.current_index == -(len(self.trajectory_points)):
                self.current_index = 0

        else:
            self.current_index += 1
            if self.current_index == len(self.trajectory_points):
                self.current_index = 0

        return returned_value

    def throw(self, type=None, value=None, traceback=None):
        raise StopIteration

    def reset(self, index_start=None):
        """Resets the trajectory to its initial position.

        Args:
            index_start (:obj:'list' of :obj:'int'): optional. If provided, changes the initial index for trajectory

        Returns:

        """
        if index_start is not None:
            self.index_start = index_start

        self.current_index = self.index_start
