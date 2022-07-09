import gym
import numpy as np

from gym import spaces

from gym_pikachu_volleyball.envs.engine import Engine

class PikachuVolleyballEnv(gym.Env):
    def __init__(self):
        super(PikachuVolleyballEnv, self).__init__()

        observation_size = (304, 432, 3)
        self.observation_space = spaces.Box(
                low = np.zeros(observation_size), 
                high = 255 * np.ones(observation_size),
                dtype = np.uint8)

        self.engine = Engine(False, False)
        self.engine.create_viewer()
   
    def render(self) -> None:
        self.engine.render()

    def close(self) -> None:
        self.engine.close()

