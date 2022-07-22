import os
from gym.envs.registration import register

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"

register(
        id="PikachuVolleyball-v0",
        entry_point='gym_pikachu_volleyball.envs:PikachuVolleyballMultiEnv',
)
