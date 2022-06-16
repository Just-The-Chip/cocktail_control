from imp import source_from_cache
from kivy.config import Config
Config.set('graphics', 'width', 800)
Config.set('graphics', 'height', 480)

from kivy.app import App
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager

from configparser import ConfigParser as AppConfig

import sys
import os

curpath = os.path.abspath(os.path.join(__file__, os.pardir))
if(curpath not in sys.path):
    sys.path.append(curpath)

from drink_selector import DrinkSelectorScreen

class MainApp(App):

    config = AppConfig()

    def __init__(self):
        # self.setup_config()
        Builder.load_file(curpath + '/drink_selector.kv')


        super().__init__()

    def setup_config(self):
        self.config.read(curpath + '/config.ini')

    def build(self):
        self.setup_config()       

        self.screen_manager = ScreenManager()

        self.drink_screen = DrinkSelectorScreen(self.config, name="drink_selector")
        self.screen_manager.add_widget(self.drink_screen)

        self.screen_manager.current = "drink_selector"

        Window.bind(on_keyboard=self.check_hotkey)

        return self.screen_manager

    def check_hotkey(self, window, keycode, scancode, codepoint, modifier):
        print(keycode, scancode, codepoint, modifier)

        key = codepoint.lower() if codepoint is not None else scancode
        # yay thanks https://stackoverflow.com/a/47922465/2993366
        if modifier == ['shift'] and (key == 'q' or key == 113):
            self.stop()

        else:
            self.screen_manager.current_screen.handle_hotkey(key, modifier)

if __name__ == '__main__':
    MainApp().run()