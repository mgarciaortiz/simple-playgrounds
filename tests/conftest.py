import pytest

from simple_playgrounds.agents.agents import (BaseAgent, HeadAgent,
                                              HeadEyeAgent, FullAgent)
from simple_playgrounds.agents.parts.controllers import RandomDiscrete, RandomContinuous
from simple_playgrounds.playgrounds.collection import *

from simple_playgrounds.agents.sensors import (RgbCamera, GreyCamera, Lidar,
                                               Proximity, Touch, TopdownSensor,
                                               FullPlaygroundSensor,
                                               SemanticRay, SemanticCones)

### Agent Body


@pytest.fixture(scope="module", params=[RandomDiscrete, RandomContinuous])
def random_control(request):
    return request.param


@pytest.fixture(scope="module", params=[True, False])
def is_interactive(request):
    return request.param


@pytest.fixture(scope="module", params=[True, False])
def going_backward(request):
    return request.param


@pytest.fixture(scope="module", params=[True, False])
def moving_laterally(request):
    return request.param


@pytest.fixture(scope="module", params=[RandomDiscrete, RandomContinuous])
def random_controller(request):
    return request.param


@pytest.fixture(scope="module", params=[BaseAgent, HeadAgent, HeadEyeAgent])
def simple_agent_cls(request):
    return request.param


@pytest.fixture(scope="module", params=[BaseAgent, HeadAgent, HeadEyeAgent, FullAgent])
def all_agent_cls(request):
    return request.param


@pytest.fixture(scope="function")
def base_forward_agent():
    agent = BaseAgent(
        controller=RandomDiscrete(),
        interactive=False,
    )
    return agent


# Agent Sensor
@pytest.fixture(scope="module",
                params=[
                    RgbCamera, GreyCamera, Lidar, Touch, Proximity,
                    TopdownSensor, FullPlaygroundSensor, SemanticRay,
                    SemanticCones
                ])
def any_sensor(request):
    return request.param


@pytest.fixture(scope="module", params=[RgbCamera, SemanticRay, SemanticCones])
def ray_sensor(request):
    return request.param


@pytest.fixture(scope="module", params=[2, 90, 180])
def fov(request):
    return request.param


@pytest.fixture(scope="module", params=[2, 100, 500])
def obs_range(request):
    return request.param


@pytest.fixture(scope="module", params=[2, 32, 64])
def resolution(request):
    return request.param


# Playgrounds
@pytest.fixture(scope="module",
                params=PlaygroundRegister.playgrounds['test'].items())
def pg_cls(request):
    _, pg_class = request.param
    return pg_class


@pytest.fixture(scope="module",
                params=PlaygroundRegister.playgrounds['basic_rl'].items())
def pg_rl_cls(request):
    _, pg_class = request.param
    return pg_class

