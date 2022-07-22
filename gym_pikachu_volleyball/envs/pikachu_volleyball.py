import gym
import numpy as np

from gym import spaces
from gym.utils.renderer import Renderer

from typing import Tuple, Union, Optional

from gym_pikachu_volleyball.envs.engine import Engine
from gym_pikachu_volleyball.envs.common import convert_to_user_input
from gym_pikachu_volleyball.envs.constants import GROUND_HALF_WIDTH

class PikachuVolleyballEnv(gym.Env):

    metadata = {"render_modes": ["human", ]}

    def __init__(self, is_player1_computer: bool, is_player2_computer: bool, render_mode: str):
        super(PikachuVolleyballEnv, self).__init__()

        observation_size = (304, 432, 3)
        self.observation_space = spaces.Box(
                low = np.zeros(observation_size), 
                high = 255 * np.ones(observation_size),
                dtype = np.uint8)

        self.engine = Engine(is_player1_computer, is_player2_computer)
        self.engine.create_viewer(render_mode)

        self.render_mode = render_mode
        self._renderer = Renderer(self.render_mode, self.engine.render)
   
    def render(self):
        return self._renderer.get_renders()

    def close(self) -> None:
        self.engine.close()

class PikachuVolleyballMultiEnv(PikachuVolleyballEnv):
    def __init__(self, render_mode: str):
        super(PikachuVolleyballMultiEnv, self).__init__(False, False, render_mode)

        self.action_space = spaces.MultiDiscrete([18, 18])

    def step(self, actions: Tuple[int, int]) -> Tuple[np.ndarray, float, bool, bool, dict]:
        converted_action = tuple(convert_to_user_input(actions[i], i) for i in range(2))
        is_ball_touching_ground = self.engine.step(converted_action)
        self.engine.viewer.update()
        self._renderer.render_step()
        if is_ball_touching_ground:
            reward = 1 if self.engine.ball.punch_effect_x < GROUND_HALF_WIDTH else -1
            return self.engine.viewer.get_screen_rgb_array(), reward, True, True, {}
        return self.engine.viewer.get_screen_rgb_array(), 0.0, False, False, {}

    def reset(self, options: dict, seed: Optional[int]=None, return_info: bool=False) -> Union[np.ndarray, Tuple[np.ndarray, dict]]:
        if seed is not None: self.engine.seed(seed)
        self.engine.reset(options['is_player2_serve'])
        self._renderer.render_step()

        screen = self.engine.viewer.get_screen_rgb_array() 
        return (screen, {}) if return_info else screen

