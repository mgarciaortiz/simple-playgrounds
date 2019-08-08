from abc import abstractmethod, ABC
import math
import cv2
import numpy as np


class SensorGenerator:

    """
    Register class to provide a decorator that is used to go through the package and
    register available playgrounds.
    """

    subclasses = {}

    @classmethod
    def register(cls, sensor_type):
        def decorator(subclass):
            cls.subclasses[sensor_type] = subclass
            return subclass

        return decorator

    @classmethod
    def create(cls, anatomy, sensor_param ):

        sensor_type = sensor_param["type"]

        if sensor_type not in cls.subclasses:
            raise ValueError('Sensor not implemented:' + sensor_type)

        return cls.subclasses[sensor_type](anatomy, sensor_param )


def get_rotated_point(x_1, y_1, x_2, y_2, angle, height):
    # Rotate x_2, y_2 around x_1, y_1 by angle.
    x_change = (x_2 - x_1) * math.cos(angle) + \
               (y_2 - y_1) * math.sin(angle)
    y_change = (y_1 - y_2) * math.cos(angle) - \
               (x_1 - x_2) * math.sin(angle)
    new_x = x_change + x_1
    new_y = height - (y_change + y_1)
    return int(new_x), int(new_y)


class Sensor(ABC):

    def __init__(self, anatomy, sensor_param):

        self.name = sensor_param.get('name', None)

        # Field of View of the Sensor
        self.fovResolution = sensor_param.get('fovResolution', None)
        self.fovRange = sensor_param.get('fovRange', None)
        self.fovAngle = sensor_param.get('fovAngle', None)
        self.min_range = sensor_param.get('minRange', None)

        
        # Anchor of the sensor
        body_anchor = sensor_param.get('bodyAnchor', None)
        self.body_anchor = anatomy[body_anchor].body

        # Relative location (polar) and angle wrt body
        self.d_r = sensor_param.get('d_r', None)
        self.d_theta = sensor_param.get('d_theta', None)
        self.d_relativeOrientation = sensor_param.get('d_relativeOrientation', None)




        self.get_shape_observation()

        self.resized_img = None
        self.cropped_img = None

        self.observation = None
        

    @abstractmethod
    def update_sensor(self, img):

        w, h, _ = img.shape

        # Position of the body
        x, y = self.body_anchor.position

        x, y =  y, x
        theta = 2*math.pi - self.body_anchor.angle

        # Position and angle of the sensor
        sensor_x = x + self.d_r * math.cos((theta + self.d_theta) % (2 * math.pi))
        sensor_y = y + self.d_r * math.sin((theta + self.d_theta) % (2 * math.pi))
        sensor_angle = theta - self.d_relativeOrientation

        polar_img = cv2.linearPolar(img, (sensor_x, sensor_y), self.fovRange, flags=cv2.INTER_NEAREST)



        angle_center = h * (sensor_angle % (2 * math.pi)) / (2 * math.pi)
        rolled_img = np.roll(polar_img, int(h / 2 - angle_center), axis=0)

        cv2.imshow('test', rolled_img)

        cropped_img = rolled_img[
                      int(h / 2 - h * (self.fovAngle / 2.0) / (2 * math.pi)):int(
                          h / 2 + h * (self.fovAngle / 2.0) / (2 * math.pi)) + 1,
                      self.min_range:
                      ]

        resized_img = cv2.resize(
            cropped_img,
            (cropped_img.shape[1], int(self.fovResolution)),
            interpolation=cv2.INTER_NEAREST
        )

        self.resized_img = resized_img
        self.cropped_img = cropped_img

    @abstractmethod
    def get_shape_observation(self):
        pass