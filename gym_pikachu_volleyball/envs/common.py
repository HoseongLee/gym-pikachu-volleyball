class UserInput:
    __slots__ = ['x_direction', 'y_direction', 'power_hit']

    def __init__(self) -> None:
        self.x_direction = 0
        self.y_direction = 0
        self.power_hit = 0

__action_converter_p1 = ((+1, -1,  0),
                         (+1,  0,  0),
                         (+1, +1,  0),
                         (+1, -1, +1),
                         (+1,  0, +1),
                         (+1, +1, +1),
                         ( 0, -1,  0),
                         ( 0,  0,  0),
                         ( 0, +1,  0),
                         ( 0, -1, +1),
                         ( 0,  0, +1),
                         ( 0, +1, +1),
                         (-1, -1,  0),
                         (-1,  0,  0),
                         (-1, +1,  0),
                         (-1, -1, +1),
                         (-1,  0, +1),
                         (-1, +1, +1))

__action_converter_p2 = ((-1, -1,  0),
                         (-1,  0,  0),
                         (-1, +1,  0),
                         (-1, -1, +1),
                         (-1,  0, +1),
                         (-1, +1, +1),
                         ( 0, -1,  0),
                         ( 0,  0,  0),
                         ( 0, +1,  0),
                         ( 0, -1, +1),
                         ( 0,  0, +1),
                         ( 0, +1, +1),
                         (+1, -1,  0),
                         (+1,  0,  0),
                         (+1, +1,  0),
                         (+1, -1, +1),
                         (+1,  0, +1),
                         (+1, +1, +1))

__action_converter = (__action_converter_p1, __action_converter_p2)

def convert_to_user_input(action: int, player_id: int) -> UserInput:
    x_direction, y_direction, power_hit = __action_converter[player_id][action]
    user_input = UserInput()
    user_input.x_direction = x_direction
    user_input.y_direction = y_direction
    user_input.power_hit = power_hit
    return user_input

