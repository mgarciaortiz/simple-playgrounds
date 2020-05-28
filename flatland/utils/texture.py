from pygame import Surface, PixelArray, SRCALPHA
from pygame import surfarray
import cv2


from scipy.stats import truncnorm
import numpy.random as rand
import numpy as np
import math, random


class Texture(object):

    subclasses = {}

    @classmethod
    def register_subclass(cls, texture_type):

        def decorator(subclass):

            cls.subclasses[texture_type] = subclass
            return subclass

        return decorator

    @classmethod
    def create(cls, params):

        texture_type = params['texture_type']

        if texture_type not in cls.subclasses:
            raise ValueError('Texture not implemented: '+texture_type)

        return cls.subclasses[texture_type](**params)


@Texture.register_subclass('color')
class ColorTexture(Texture):

    def __init__(self, **params):
        super(ColorTexture, self).__init__()
        self.color = params['color']

    def generate(self, width, height):
        surface = Surface((width, height))
        surface.fill(self.color)
        return surface



@Texture.register_subclass('uniform')
class UniformTexture(Texture):

    def __init__(self, **params):
        super(UniformTexture, self).__init__()
        self.min = params['color_min']
        self.max = params['color_max']

    def generate(self, width, height):
        """
        Generate a pygame Surface with pixels following a uniform density
        :param width: the width of the generated Surface
        :param height: the height of the generated Surface
        :return: the pygame Surface
        """

        random_image = np.random.uniform(self.min, self.max, (int(width), int(height), 3)).astype('int')
        surf = surfarray.make_surface(random_image)
        return surf


@Texture.register_subclass('random_tiles')
class RandomTilesTexture(Texture):

    def __init__(self, **params):
        super(RandomTilesTexture, self).__init__()
        self.min = params['color_min']
        self.max = params['color_max']
        self.size_tiles = params['size_tiles']

    def generate(self, width, height):
        """
        Generate a pygame Surface with pixels following a uniform density
        :param width: the width of the generated Surface
        :param height: the height of the generated Surface
        :return: the pygame Surface
        """

        random_image = np.random.uniform(self.min, self.max, (int(width*1.0/self.size_tiles), int(height*1.0/self.size_tiles), 3)).astype('int')
        random_image = cv2.resize(random_image, ( int(height), int(width) ), interpolation=cv2.INTER_NEAREST)
        surf = surfarray.make_surface(random_image)
        return surf


@Texture.register_subclass('list_random_tiles')
class ListRandomTilesTexture(Texture):

    def __init__(self, list_rgb_colors = (130, 150, 170), delta_uniform = 5, size_tiles = 4, **kwargs):
        super(ListRandomTilesTexture, self).__init__()
        self.list_rgb_colors = list_rgb_colors
        self.delta_uniform = delta_uniform
        self.size_tiles = size_tiles

    def generate(self, width, height):
        """
        Generate a pygame Surface with pixels following a uniform density
        :param width: the width of the generated Surface
        :param height: the height of the generated Surface
        :return: the pygame Surface
        """

        color = random.choice(self.list_rgb_colors)
        min_color = [ max(0, x - self.delta_uniform) for x in color]
        max_color = [ min(255, x + self.delta_uniform) for x in color]

        random_image = np.random.uniform(min_color, max_color, (int(width*1.0/self.size_tiles), int(height*1.0/self.size_tiles), 3)).astype('int')
        random_image = cv2.resize(random_image, ( int(height), int(width) ), interpolation=cv2.INTER_NEAREST)
        surf = surfarray.make_surface(random_image)
        return surf

@Texture.register_subclass('unique_random_tiles')
class UniqueRandomTilesTexture(Texture):



    def __init__(self, n_colors = 10, delta_uniform = 5, size_tiles = 4, color_min = (0,0,0), color_max = (255,255,255),
                 **kwargs):
        super(UniqueRandomTilesTexture, self).__init__()
        self.n_colors = n_colors
        self.delta_uniform = delta_uniform
        self.size_tiles = size_tiles
        self.color_min = color_min
        self.color_max = color_max

        n_r_splits = int( n_colors ** (1/3) )
        n_g_splits = int( n_colors ** (1/3))
        n_b_splits = n_colors - 2*int(n_colors ** (1/3))

        r_list = [ color_min[0] + n_r * (color_max[0] - color_min[0] )/ (n_r_splits-1) for n_r in range(0, n_r_splits) ]
        g_list = [ color_min[1] + n_g * (color_max[1] - color_min[1] ) / (n_g_splits-1) for n_g in range(0, n_g_splits) ]
        b_list = [ color_min[2] + n_b * (color_max[2] - color_min[2] ) / (n_b_splits-1) for n_b in range(0, n_b_splits) ]

        self.list_rgb_colors = []

        for r in r_list:
            for g in g_list:
                for b in b_list:
                    self.list_rgb_colors.append([r,b,g])

        random.shuffle(self.list_rgb_colors)

    def generate(self, width, height):
        """
        Generate a pygame Surface with pixels following a uniform density
        :param width: the width of the generated Surface
        :param height: the height of the generated Surface
        :return: the pygame Surface
        """

        color = self.list_rgb_colors.pop()
        min_color = [ max(0, x - self.delta_uniform) for x in color]
        max_color = [ min(255, x + self.delta_uniform) for x in color]

        random_image = np.random.uniform(min_color, max_color, (int(width*1.0/self.size_tiles), int(height*1.0/self.size_tiles), 3)).astype('int')
        random_image = cv2.resize(random_image, ( int(height), int(width) ), interpolation=cv2.INTER_NEAREST)
        surf = surfarray.make_surface(random_image)
        return surf


@Texture.register_subclass('polar_stripes')
class PolarStripesTexture(Texture):

    def __init__(self, **params):
        super(PolarStripesTexture, self).__init__()
        self.color_1 = params['color_1']
        self.color_2 = params['color_2']
        self.n_stripes = params['n_stripes']

    def generate(self, width, height):
        """
        Generate a pyame Surface with pixels following a circular striped pattern from the center of the parent entity
        :param width: the width of the generated surface
        :param height: the height of the generated surface
        :return: the pygame Surface
        """

        width = int(width)
        height = int(height)

        img = np.zeros( (width, height , 3) )

        x = width/2
        y = height/2

        for i in range(width):
            for j in range(height):

                angle = np.arctan2( j - y, i - x)  % (2*math.pi/self.n_stripes)

                if angle  > math.pi/(self.n_stripes) :
                    img[i, j, :] = self.color_1
                else:
                    img[i, j, :] = self.color_2

        surf = surfarray.make_surface(img)
        return surf

@Texture.register_subclass('centered_random_tiles')
class CenteredRandomTilesTexture(Texture):

    def __init__(self, **params):
        super(CenteredRandomTilesTexture, self).__init__()
        self.min = params['color_min']
        self.max = params['color_max']
        self.radius = params['radius']
        self.size_tiles = params['size_tiles']
        self.n_stripes = int(2*math.pi*self.radius / self.size_tiles)

    def generate(self, width, height):
        """
        Generate a pyame Surface with pixels following a circular striped pattern from the center of the parent entity
        :param width: the width of the generated surface
        :param height: the height of the generated surface
        :return: the pygame Surface
        """

        width = int(width)
        height = int(height)

        img = np.zeros( (width, height , 3) )

        colors = [ [ random.randint( self.min[i],self.max[i] ) for i in range(3)] for c in range(self.n_stripes) ]

        x = width/2
        y = height/2

        for i in range(width):
            for j in range(height):

                angle = int( np.arctan2( j - y, i - x)  / (2*math.pi/self.n_stripes) )

                img[i, j, :] = colors[angle]

        surf = surfarray.make_surface(img)
        return surf

@Texture.register_subclass('list_centered_random_tiles')
class ListCenteredRandomTiles(Texture):

    def __init__(self, **params):
        super(ListCenteredRandomTiles, self).__init__()
        self.radius = params['radius']
        self.size_tiles = params['size_tiles']
        self.n_stripes = int(2*math.pi*self.radius / self.size_tiles)
        self.colors = params['colors']

    def generate(self, width, height):
        """
        Generate a pyame Surface with pixels following a circular striped pattern from the center of the parent entity
        :param width: the width of the generated surface
        :param height: the height of the generated surface
        :return: the pygame Surface
        """

        width = int(width)
        height = int(height)

        img = np.zeros( (width, height , 3) )

        colors = random.choices( self.colors, k = self.n_stripes)

        x = width/2
        y = height/2

        for i in range(width):
            for j in range(height):

                angle = int( np.arctan2( j - y, i - x)  / (2*math.pi/self.n_stripes) )

                img[i, j, :] = colors[angle]

        surf = surfarray.make_surface(img)
        return surf



class NormalTexture(Texture):

    def __init__(self, m, d):
        super(NormalTexture, self).__init__()
        self.m = m
        self.d = d

    def generate(self, width, height):
        """
        Generate a pygame Surface with pixels following a normal density of diagonal covariance matrix.
        :param width: the width of the generated Surface
        :param height: the height of the generated Surface
        :return: the pygame Surface
        """

        surface = Surface((width, height), SRCALPHA)
        pxarray = PixelArray(surface)

        m = np.array(self.m)
        d = np.array(self.d)

        t = np.zeros((width, height, 3))

        for c in range(3):
            a, b = (0 - m[c]) / d[c], (255 - m[c])/d[c]
            tc = truncnorm.rvs(a, b, size=width * height)
            t[:, :, c] = tc.reshape(width, height)

        for i in range(width):
            for j in range(height):
                pxarray[i, j] = tuple((d * t[i, j] + m).astype(int))

        return surface


class StripesTexture(Texture):

    def __init__(self, colors, lengths, angle):
        super(StripesTexture, self).__init__()
        self.colors = colors
        self.lengths = lengths
        self.angle = angle
        assert len(self.colors) == len(self.lengths), "Parameters 'lengths' and 'colors' should be the same length."

    def generate(self, width, height):
        """
        Generate a pygame Surface with pixels following a striped pattern.
        :param width: the width of the generated surface
        :param height: the height of the generated surface
        :return: the pygame Surface
        """

        surface = Surface((width, height), SRCALPHA)
        pxarray = PixelArray(surface)

        for i in range(width):
            for j in range(height):
                l = np.sqrt(i**2 + j**2) * np.cos(np.arctan((j+1)/(i+1)) - self.angle)
                r = l % sum(self.lengths)
                for mode, d in enumerate(np.cumsum(self.lengths)):
                    if r < d:
                        pxarray[i, j] = self.colors[mode]
                        break

        return surface



