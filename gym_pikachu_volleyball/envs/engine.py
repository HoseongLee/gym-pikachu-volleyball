import random
from typing import Tuple

from gym_pikachu_volleyball.envs.viewer import Viewer
from gym_pikachu_volleyball.envs.constants import *
from gym_pikachu_volleyball.envs.common import UserInput

class Engine:
    __slots__ = ['players', 'ball', 'viewer']

    def __init__(self, is_player1_computer: bool, is_player2_computer: bool) -> None:
        self.players = (
                Player(False, is_player1_computer), 
                Player(True, is_player2_computer))

        self.ball = Ball(False)

    def step(self, user_inputs: Tuple[UserInput, UserInput]):
        is_ball_touching_ground =\
                self.__process_collision_between_ball_and_world_and_set_ball_position();

        for i in range(2):
            self.__process_player_movement_and_set_player_position(i, user_inputs[i])

        for i in range(2):
            is_happening = self.__is_collision_between_ball_and_player_happening(i)
            player = self.players[i]
            if is_happening:
                if not player.is_collision_with_ball_happening:
                    self.__process_collision_between_ball_and_player(i, user_inputs[i])
                    player.is_collision_with_ball_happening = True
            else:
                player.is_collision_with_ball_happening = False

        return is_ball_touching_ground

    def reset(self, is_player2_serve: bool) -> None:
        self.players[0].reset()
        self.players[1].reset()
        self.ball.reset(is_player2_serve)

    def __is_collision_between_ball_and_player_happening(self, player_id: int) -> bool:
        player = self.players[player_id]
        return abs(self.ball.x - player.x) <= PLAYER_HALF_LENGTH and\
                abs(self.ball.y - player.y) <= PLAYER_HALF_LENGTH

    def __process_collision_between_ball_and_world_and_set_ball_position(self) -> bool:
        self.ball.previous_previous_x = self.ball.previous_x
        self.ball.previous_previous_y = self.ball.previous_y
        self.ball.previous_x = self.ball.x
        self.ball.previous_y = self.ball.y

        self.ball.fine_rotation = (self.ball.fine_rotation + self.ball.x_velocity // 2) % 50
        self.ball.rotation = self.ball.fine_rotation // 10

        future_ball_x = self.ball.x + self.ball.x_velocity

        if future_ball_x < BALL_RADIUS or future_ball_x > GROUND_WIDTH:
            self.ball.x_velocity = -self.ball.x_velocity

        future_ball_y = self.ball.y + self.ball.y_velocity
        if future_ball_y < 0:
            self.ball.y_velocity = 1

        if abs(self.ball.x - GROUND_HALF_WIDTH) < NET_PILLAR_HALF_WIDTH and\
                self.ball.y > NET_PILLAR_TOP_TOP_Y_COORD:
            if self.ball.y <= NET_PILLAR_TOP_BOTTOM_Y_COORD:
                if self.ball.y_velocity > 0:
                    self.ball.y_velocity = -self.ball.y_velocity
            else:
                if self.ball.x < GROUND_HALF_WIDTH:
                    self.ball.x_velocity = -abs(self.ball.x_velocity)
                else:
                    self.ball.x_velocity = abs(self.ball.x_velocity)

        future_ball_y = self.ball.y + self.ball.y_velocity

        if future_ball_y > BALL_TOUCHING_GROUND_Y_COORD:
            self.ball.y = BALL_TOUCHING_GROUND_Y_COORD
            self.ball.y_velocity = -self.ball.y_velocity
            self.ball.punch_effect_x = self.ball.x
            self.ball.punch_effect_y = BALL_TOUCHING_GROUND_Y_COORD + BALL_RADIUS
            self.ball.punch_effect_radius = BALL_RADIUS
            return True

        self.ball.y = future_ball_y
        self.ball.x = self.ball.x + self.ball.x_velocity
        self.ball.y_velocity += 1

        return False

    def __process_player_movement_and_set_player_position(self, player_id: int, user_input: UserInput):
        player = self.players[player_id]

        if player.state == 4:
            player.lying_down_duration_left -= 1
            if player.lying_down_duration_left < -1:
                player.state = 0
            return

        player_velocity_x = 0
        if player.state < 5:
            if player.state < 3:
                player_velocity_x = user_input.x_direction * 6
            else:
                player_velocity_x = player.diving_direction * 8

        future_player_x = player.x + player_velocity_x
        player.x = future_player_x

        if not player.is_player2:
            if future_player_x < PLAYER_HALF_LENGTH:
                player.x = PLAYER_HALF_LENGTH
            elif future_player_x > GROUND_HALF_WIDTH - PLAYER_HALF_LENGTH:
                player.x = GROUND_HALF_WIDTH - PLAYER_HALF_LENGTH
        else:
            if future_player_x < GROUND_HALF_WIDTH + PLAYER_HALF_LENGTH:
                player.x = GROUND_HALF_WIDTH + PLAYER_HALF_LENGTH
            elif future_player_x > GROUND_WIDTH - PLAYER_HALF_LENGTH:
                player.x = GROUND_WIDTH - PLAYER_HALF_LENGTH

        if player.state < 3 and user_input.y_direction == -1 and\
                player.y == PLAYER_TOUCHING_GROUND_Y_COORD:
            player.y_velocity = -16
            player.state = 1
            player.frame_number = 0

        future_player_y = player.y + player.y_velocity
        player.y = future_player_y

        if future_player_y < PLAYER_TOUCHING_GROUND_Y_COORD:
            player.y_velocity += 1
        elif future_player_y > PLAYER_TOUCHING_GROUND_Y_COORD:
            player.y_velocity = 0
            player.y = PLAYER_TOUCHING_GROUND_Y_COORD
            player.frame_number = 0

            if player.state == 3:
                player.state = 4
                player.frame_number = 0
                player.lying_down_duration_left = 3
            else:
                player.state = 0

        if user_input.power_hit == 1:
            if player.state == 1:
                player.delay_before_next_frame = 5
                player.frame_number = 0
                player.state = 2
            elif player.state == 0 and user_input.x_direction != 0:
                player.state = 3
                player.frame_number = 0
                player.diving_direction = user_input.x_direction
                player.y_velocity = -5

        if player.state == 1:
            player.frame_number = (player.frame_number + 1) % 3
        elif player.state == 2:
            if player.delay_before_next_frame < 1:
                player.frame_number += 1
                if player.frame_number > 4:
                    player.frame_number = 0
                    player.state = 1
            else:
                player.delay_before_next_frame += 1
        elif player.state == 0:
            player.delay_before_next_frame += 1
            if player.delay_before_next_frame > 3:
                player.delay_before_next_frame = 0
                future_frame_number = player.frame_number + player.normal_status_arm_swing_direction
                if future_frame_number < 0 or future_frame_number > 4:
                    player.normal_status_arm_swing_direction *= -1
                player.frame_number += player.normal_status_arm_swing_direction

        if player.game_ended:
            if player.state == 0:
                if player.is_winner:
                    player.state = 5
                else:
                    player.state = 6
                player.delay_before_next_frame = 0
                player.frame_number = 0

            self.__process_game_end_frame_for(player_id)

    def __process_collision_between_ball_and_player(self, player_id: int, user_input: UserInput):
        player = self.players[player_id]

        if self.ball.x < player.x:
            self.ball.x_velocity = -abs(self.ball.x - player.x) // 3
        elif self.ball.x > player.x:
            self.ball.x_velocity = abs(self.ball.x - player.x) // 3

        if self.ball.x_velocity == 0:
            self.ball.x_velocity = random.randint(-1, +1)

        ball_abs_y_velocity = abs(self.ball.y_velocity)
        self.ball.y_velocity = -ball_abs_y_velocity

        if ball_abs_y_velocity < 15:
            self.ball.y_velocity = -15

        if player.state == 2:
            if self.ball.x < GROUND_HALF_WIDTH:
                self.ball.x_velocity = (abs(user_input.x_direction) + 1) * 10
            else:
                self.ball.x_velocity = -(abs(user_input.x_direction) + 1) * 10
            
            self.ball.punch_effect_x = self.ball.x
            self.ball.punch_effect_y = self.ball.y

            self.ball.y_velocity = abs(self.ball.y_velocity) * user_input.y_direction * 2
            self.ball.punch_effect_radius = BALL_RADIUS

            self.ball.is_power_hit = True
        else:
            self.ball.is_power_hit = False

    def __process_game_end_frame_for(self, player_id: int) -> None:
        player = self.players[player_id]
        if player.game_ended and player.frame_number < 4:
            player.delay_before_next_frame += 1
            if player.delay_before_next_frame > 4:
                player.delay_before_next_frame = 0
                player.frame_number += 1

    def create_viewer(self) -> None:
        self.viewer = Viewer(self)

    def render(self) -> None:
        if self.viewer.headless:
            self.viewer.init_screen()

        self.viewer.render()

    def close(self) -> None:
        self.viewer.close()

class Player:
    __slots__ = ['is_player2', 'is_computer', 
            'diving_direction', 'lying_down_duration_left', 
            'is_winner', 'game_ended', 'computer_where_to_stand_by', 
            'x', 'y', 'y_velocity', 'is_collision_with_ball_happening', 
            'state', 'frame_number', 'normal_status_arm_swing_direction', 
            'delay_before_next_frame', 'computer_boldness']

    def __init__(self, is_player2: bool, is_computer: bool) -> None:
        self.is_player2 = is_player2
        self.is_computer = is_computer

        self.diving_direction = 0
        self.lying_down_duration_left = -1
        self.is_winner = False
        self.game_ended = False

        self.computer_where_to_stand_by = 0

        self.reset()

    def reset(self) -> None:
        self.x = 36 if not self.is_player2 else GROUND_WIDTH - 36
        self.y = PLAYER_TOUCHING_GROUND_Y_COORD

        self.y_velocity = 0
        self.is_collision_with_ball_happening = False

        self.state = 0
        self.frame_number = 0
        self.normal_status_arm_swing_direction = 1
        self.delay_before_next_frame = 0

        self.computer_boldness = random.randrange(0, 5)

class Ball:
    __slots__ = ['expected_landing_point_x', 
            'rotation', 'fine_rotation', 
            'punch_effect_x', 'punch_effect_y', 
            'previous_x', 'previous_previous_x', 
            'previous_y', 'previous_previous_y', 
            'x', 'y', 'x_velocity', 'y_velocity', 
            'punch_effect_radius', 'is_power_hit']
    
    def __init__(self, is_player2_serve: bool) -> None:
        self.reset(is_player2_serve)

        self.expected_landing_point_x = 0

        self.rotation = 0
        self.fine_rotation = 0
        self.punch_effect_x = 0
        self.punch_effect_y = 0

        self.previous_x = 0
        self.previous_previous_x = 0
        self.previous_y = 0
        self.previous_previous_y = 0

    def reset(self, is_player2_serve: bool) -> None:
        self.x = 56 if not is_player2_serve else GROUND_WIDTH - 56
        self.y = 0

        self.x_velocity = 0
        self.y_velocity = 1

        self.punch_effect_radius = 0
        self.is_power_hit = False

