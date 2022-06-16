from kivy.uix.gridlayout import GridLayout
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.modalview import ModalView
from kivy.uix.image import Image
from kivy.clock import mainthread

import sys
import os
import time

class ScrollButton(ToggleButton):
    def __init__(self, **kwargs):
        self.jar_pos = kwargs.pop('ingredient_id')
        self.ingredient_id = kwargs.pop('ingredient_id')
        super(ScrollButton, self).__init__(**kwargs)