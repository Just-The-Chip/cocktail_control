from imp import source_from_cache
from kivy.config import Config
Config.set('graphics', 'width', 800)
Config.set('graphics', 'height', 480)
Config.set('graphics', 'fullscreen', 'auto')
Config.set('graphics', 'show_cursor', 0)

from kivy.app import App
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager

from configparser import ConfigParser as AppConfig

import sys
import os

# # Replace libraries on windows machine
# import fake_rpi

# sys.modules['RPi'] = fake_rpi.RPi     # Fake RPi
# sys.modules['RPi.GPIO'] = fake_rpi.RPi.GPIO # Fake GPIO
# sys.modules['smbus'] = fake_rpi.smbus # Fake smbus (I2C)

curpath = os.path.abspath(os.path.join(__file__, os.pardir))
if(curpath not in sys.path):
    sys.path.append(curpath)

from drink_selector import DrinkSelectorScreen
from settings import SettingsScreen

class MainApp(App):

    config = AppConfig()

    def __init__(self):
        # self.setup_config()
        Builder.load_file(curpath + '/drink_selector.kv')
        Builder.load_file(curpath + '/settings.kv')

        super().__init__()

    def setup_config(self):
        self.config.read(curpath + '/config.ini')

    def build(self):
        self.setup_config()       

        self.screen_manager = ScreenManager()

        self.drink_screen = DrinkSelectorScreen(self.config, name="drink_selector")
        self.screen_manager.add_widget(self.drink_screen)

        self.settings_screen = SettingsScreen(self.config, name="settings")
        self.screen_manager.add_widget(self.settings_screen)

        self.screen_manager.current = "drink_selector"

        Window.bind(on_keyboard=self.check_hotkey)

        return self.screen_manager

    def check_hotkey(self, window, keycode, scancode, codepoint, modifier):
        print(keycode, scancode, codepoint, modifier)

        key = codepoint.lower() if codepoint is not None else scancode
        # yay thanks https://stackoverflow.com/a/47922465/2993366
        if modifier == ['shift'] and (key == 'q' or key == 20):
            self.stop()

        elif modifier == ['shift'] and (key == 's' or key == 22):
            self.screen_manager.current = "settings"

        elif modifier == ['shift'] and (key == 'd' or key == 7):
            self.screen_manager.current = "drink_selector"

        else:
            self.screen_manager.current_screen.handle_hotkey(key, modifier)

if __name__ == '__main__':
    MainApp().run()