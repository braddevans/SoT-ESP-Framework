from pyglet.text import Label
from pyglet.shapes import Rectangle
from helpers import foreground_batch, background_batch

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


class LabelDefault:
    def __init__(self, text='',
                 font_name=None, font_size=None, bold=False, italic=False, stretch=False,
                 color=(255, 255, 255, 255),
                 x=0, y=0, width=None, height=None,
                 anchor_x='left', anchor_y='baseline',
                 align='left',
                 multiline=False, dpi=None, batch=None, group=None):
        self.label = Label(text=text, font_name=font_name, font_size=font_size, bold=bold,
                           italic=italic, stretch=stretch, color=color, x=x, y=y, width=width, height=height,
                           anchor_x=anchor_x, anchor_y=anchor_y, align=align, multiline=multiline, dpi=dpi, batch=batch, group=group)

        self._visible = True
        self._x = x
        self._y = y
        self._text = text
    
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
    
    @property
    def x(self):
        return self.label.x
    
    @x.setter
    def x(self, value):
        if self._x == value:
            return
        self._x = value
        self.label.x = value
    
    @property
    def y(self):
        return self.label.y
    
    @y.setter
    def y(self, value):
        if self._y == value:
            return
        self._y = value
        self.label.y = value

    def delete(self):
        self.label.delete()
        del self