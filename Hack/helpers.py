"""
@Author https://github.com/DougTheDruid
@Source https://github.com/DougTheDruid/SoT-ESP-Framework
"""

import math
import json
import logging
import win32gui
from pyglet.graphics import Batch
from pyglet.text import Label
from pyglet.shapes import Rectangle

CONFIG = {
    "FPS_TARGET": 165,
    "CREWS_ENABLED": True,
    "SHIPS_ENABLED": True,
    "WORLD_ENABLED": True,
    "PLAYERS_ENABLED": True,
    "BARRELS_ENABLED": True,
    "FOV": 0,  # 0 to disable custom fov
    "SCOPE_FOV": 34.615,
}

# Config specification for logging file
logging.basicConfig(filename='ESP.log', level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(message)s', filemode="w")
logger = logging.getLogger()


# Information on SoT height and width. Used here and in main.py to display
# data to the screen. May need to manually override if wonky
try:
    window = win32gui.FindWindow(None, "Sea of Thieves")
    SOT_WINDOW = win32gui.GetWindowRect(window)  # (x1, y1, x2, y2)
    SOT_WINDOW_H = SOT_WINDOW[3] - SOT_WINDOW[1]
    SOT_WINDOW_W = SOT_WINDOW[2] - SOT_WINDOW[0]
except Exception as e:
    logger.error("Unable to find SoT window; exiting.")
    exit(-1)


# Creates a pyglet "Batch" that we draw our information to. Effectively serves
# as a piece of paper, so we save render cost because its 2D
foreground_batch = Batch()
background_batch = Batch()


# Outlined label
class LabelOutline:
    def __init__(self, text='',
                 font_name=None, font_size=None, bold=False, italic=False, stretch=False,
                 color=(255, 255, 255, 255),
                 x=0, y=0, width=None, height=None,
                 anchor_x='left', anchor_y='baseline',
                 align='left',
                 multiline=False, dpi=None, batch=None, shadows_batch=None, group=None):
        self.label = Label(text=text, font_name=font_name, font_size=font_size, bold=bold,
                           italic=italic, stretch=stretch, color=color, x=x, y=y, width=width, height=height,
                           anchor_x=anchor_x, anchor_y=anchor_y, align=align, multiline=multiline, dpi=dpi, batch=batch, group=group)
        self.shadows: list[Label] = list()

        self._visible = True
        self._x = x
        self._y = y
        self._text = text

        for sx in [-1, 0, 1]:
            for sy in [-1, 0, 1]:
                if sx == 0 and sy == 0: continue
                self.shadows.append(Label(text=text, font_name=font_name, font_size=font_size, bold=bold,
                            italic=italic, stretch=stretch, color=(0, 0, 0, 255), x=x+sx, y=y+sy, width=width, height=height,
                            anchor_x=anchor_x, anchor_y=anchor_y, align=align, multiline=multiline, dpi=dpi, batch=shadows_batch, group=group))
    
    @property
    def content_width(self):
        return self.label.content_width
    
    @property
    def content_height(self):
        return self.label.content_height

    @property
    def visible(self):
        return self.label.visible
    
    @visible.setter
    def visible(self, value):
        if self._visible == value:
            return
        self._visible = value
        self.label.visible = value
        for shadow in self.shadows:
            shadow.visible = value

    @property
    def color(self):
        return self.label.color
    
    @color.setter
    def color(self, value):
        self.label.color = value

    @property
    def text(self):
        return self.label.text
    
    @text.setter
    def text(self, value):
        if self._text == value:
            return
        self._text = value
        self.label.text = value
        for shadow in self.shadows:
            shadow.text = value
    
    @property
    def x(self):
        return self.label.x
    
    @x.setter
    def x(self, value):
        if self._x == value:
            return
        self._x = value
        diff = self.label.x - value
        self.label.x = value

        for shadow in self.shadows:
            shadow.x -= diff
    
    @property
    def y(self):
        return self.label.y
    
    @y.setter
    def y(self, value):
        if self._y == value:
            return
        self._y = value
        diff = self.label.y - value
        self.label.y = value

        for shadow in self.shadows:
            shadow.y -= diff

    def delete(self):
        self.label.delete()
        for shadow in self.shadows:
            shadow.delete()
        del self


# Label with background
class LabelPanel:
    def __init__(self, text='',
                 font_name=None, font_size=None, bold=False, italic=False, stretch=False,
                 color=(255, 255, 255, 255), line_color=(255, 255, 255, 220),
                 x=0, y=0, width=None, height=None,
                 anchor_x='left', anchor_y='baseline',
                 align='left',
                 multiline=False, dpi=None, group=None):
        self.label = Label(text=text, font_name=font_name, font_size=font_size, bold=bold,
                           italic=italic, stretch=stretch, color=color, x=x, y=y, width=width, height=height,
                           anchor_x=anchor_x, anchor_y=anchor_y, align=align, multiline=multiline, dpi=dpi, batch=foreground_batch, group=group)
        
        self.line_height = 2 if line_color[-1] > 0 else 0
        self.background = Rectangle(x=x-6, y=y-self.label.content_height-self.line_height+12, width=self.label.content_width + 12, height=self.label.content_height + 6 + self.line_height,
                                    color=(0, 0, 0), batch=background_batch, group=group)
        self.background.opacity = 150
        self._visible = True
        self._x = x
        self._y = y
        self._text = text

        if line_color[-1] > 0:
            self.line = Rectangle(x=self.background.x, y=self.background.y, width=self.background.width, height=2,
                                  color=line_color[:3], batch=background_batch, group=group)
            self.line.opacity = line_color[-1]
        else:
            self.line = None
        
    @property
    def content_width(self):
        return self.label.content_width
    
    @property
    def content_height(self):
        return self.label.content_height

    @property
    def visible(self):
        return self.label.visible
    
    @visible.setter
    def visible(self, value):
        if value == self._visible:
            return
        self._visible = value
        self.label.visible = value
        self.background.visible = value
        if self.line:
            self.line.visible = value

    @property
    def color(self):
        return self.label.color
    
    @color.setter
    def color(self, value):
        self.label.color = value

    @property
    def text(self):
        return self.label.text
    
    @text.setter
    def text(self, value):
        if self._text == value:
            return
        self._text = value
        self.label.text = value
        self.background.width = self.label.content_width + 12
        self.background.y = self.label.y - self.label.content_height-self.line_height+12
        self.background.height = self.label.content_height + 6 + self.line_height
        if self.line:
            self.line.width = self.background.width
            self.line.y = self.background.y
    
    @property
    def x(self):
        return self.label.x
    
    @x.setter
    def x(self, value):
        if self._x == value:
            return
        self._x = value
        diff = self.label.x - value
        self.label.x = value
        self.background.x -= diff
        if self.line:
            self.line.x -= diff
    
    @property
    def y(self):
        return self.label.y
    
    @y.setter
    def y(self, value):
        if self._y == value:
            return
        self._y = value
        diff = self.label.y - value
        self.label.y = value
        self.background.y -= diff
        if self.line:
            self.line.y -= diff

    def delete(self):
        self.label.delete()
        self.background.delete()
        if self.line:
            self.line.delete()
        del self


# Load our offset json file
with open("offsets.json") as infile:
    OFFSETS = json.load(infile)


def dot(array_1: tuple, array_2: tuple) -> float:
    """
    Python-converted version of Gummy's External SoT v2 vMatrix Dot method (No
    Longer Avail). Takes two lists and multiplies the same index across both
    lists, and adds them together. (Need Source)
    :param tuple array_1: Presumably some array about our player position
    :param tuple array_2: Presumably some array about the dest actor position
    :rtype: float
    :return: The result of a math equation between those two arrays
    """
    if array_2[0] == 0 and array_2[1] == 0 and array_2[2] == 0:
        return 0.0

    return array_1[0] * array_2[0] + array_1[1] \
           * array_2[1] + array_1[2] * array_2[2]


def object_to_screen(player: dict, actor: dict) -> tuple:
    """
    Using the player and an actors coordinates, determine where on the screen
    an object should be displayed. Assumes your screen is 2560x1440

    Python-converted version of Gummy's External SoT v2 WorldToScreen method:
    (No Longer Avail; Need Source)

    :param player: The player coordinate dictionary
    :param actor: An actor coordinate dictionary
    :rtype: tuple
    :return: tuple of x and y screen coordinates to display where the actor is
    on screen
    """
    try:
        player_camera = (player.get("cam_x"), player.get("cam_y"),
                         player.get("cam_z"))
        temp = make_v_matrix(player_camera)

        v_axis_x = (temp[0][0], temp[0][1], temp[0][2])
        v_axis_y = (temp[1][0], temp[1][1], temp[1][2])
        v_axis_z = (temp[2][0], temp[2][1], temp[2][2])

        v_delta = (actor.get("x") - player.get("x"),
                   actor.get("y") - player.get("y"),
                   actor.get("z") - player.get("z"))
        v_transformed = [dot(v_delta, v_axis_y),
                         dot(v_delta, v_axis_z),
                         dot(v_delta, v_axis_x)]

        # Credit https://github.com/AlexBurneikis
        # No valid screen coordinates if its behind us
        if v_transformed[2] < 1.0:
            return False

        fov = player.get("fov")
        screen_center_x = SOT_WINDOW_W / 2
        screen_center_y = SOT_WINDOW_H / 2

        tmp_fov = math.tan(fov * math.pi / 360)

        x = screen_center_x + v_transformed[0] * (screen_center_x / tmp_fov) \
            / v_transformed[2]
        if x > SOT_WINDOW_W or x < 0:
            return False
        y = screen_center_y - v_transformed[1] * \
            (screen_center_x / tmp_fov) \
            / v_transformed[2]
        if y > SOT_WINDOW_H or y < 0:
            return False

        return int(x), int(SOT_WINDOW_H - y)
    except Exception as w2s_error:
        logger.error(f"Couldn't generate screen coordinates for entity: {w2s_error}")


def make_v_matrix(rot: tuple) -> list:
    """
    Builds data around how the camera is currently rotated.

    Python-converted version of Gummy's External SoT v2 Matrix method:
    (No Longer Avail; Need Source)

    :param rot: The player objects camera rotation information
    :rtype: list
    :return: A list of lists containing data about the rotation of our actor
    """
    rad_pitch = (rot[0] * math.pi / 180)
    rad_yaw = (rot[1] * math.pi / 180)
    rad_roll = (rot[2] * math.pi / 180)

    sin_pitch = math.sin(rad_pitch)
    cos_pitch = math.cos(rad_pitch)
    sin_yaw = math.sin(rad_yaw)
    cos_yaw = math.cos(rad_yaw)
    sin_roll = math.sin(rad_roll)
    cos_roll = math.cos(rad_roll)

    matrix = [[0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]]
    matrix[0][0] = cos_pitch * cos_yaw
    matrix[0][1] = cos_pitch * sin_yaw
    matrix[0][2] = sin_pitch

    matrix[1][0] = sin_roll * sin_pitch * cos_yaw - cos_roll * sin_yaw
    matrix[1][1] = sin_roll * sin_pitch * sin_yaw + cos_roll * cos_yaw
    matrix[1][2] = -sin_roll * cos_pitch

    matrix[2][0] = -(cos_roll * sin_pitch * cos_yaw + sin_roll * sin_yaw)
    matrix[2][1] = cos_yaw * sin_roll - cos_roll * sin_pitch * sin_yaw
    matrix[2][2] = cos_roll * cos_pitch
    return matrix


def calculate_distance(obj_to: dict, obj_from: dict) -> int:
    """
    Determines the distances From one object To another in meters, rounding
    to whatever degree of precision you request
    (**2 == ^2)

    Note: Can convert the int() to a round() if you want more precision

    :param obj_to: A coordinate dict for the destination object
    :param obj_from: A coordinate dict for the origin object
    :rtype: int
    :return: the distance in meters from obj_from to obj_to
    """
    distance = math.sqrt((obj_to.get("x") - obj_from.get("x")) ** 2 +
                         (obj_to.get("y") - obj_from.get("y")) ** 2 +
                         (obj_to.get("z") - obj_from.get("z")) ** 2)
    try:
        return int(distance)
    except:
        return 0