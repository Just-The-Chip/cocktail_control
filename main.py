from kivy.config import Config
Config.set('graphics', 'width', 800)
Config.set('graphics', 'height', 480)

from kivy.app import App
from kivy.core.window import Window
from kivy.uix.gridlayout import GridLayout
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.textinput import TextInput
from kivy.clock import mainthread

from configparser import ConfigParser as AppConfig

import sys
import os
import time

curpath = os.path.abspath(os.path.join(__file__, os.pardir))
if(curpath not in sys.path):
    sys.path.append(curpath)

from repository import DrinkRepository
from dispenser import Dispenser
from hardware import EncoderInput

class ScrollButton(ToggleButton):
    def __init__(self, **kwargs):
        self.img = curpath + '/images/' + kwargs.pop('img')
        self.drink_id = kwargs.pop('drink_id')
        super(ScrollButton, self).__init__(**kwargs)

class MainScreen(GridLayout):

    widgetList = []
    currentPos = 0

    def __init__(self, drinks, **kwargs):
        super(MainScreen, self).__init__(**kwargs)

        self.ids.preview.source = './images/hola.png'

        container = self.ids.container
        for drink in drinks:
            btn = ScrollButton(drink_id=drink['id'], img=drink['image'], text=drink['name'], on_press=self.switch_image)
            self.widgetList.append(btn)
            container.add_widget(btn)

        self.select_current()

    def set_current(self, drinkPos):
        self.widgetList[self.currentPos].state = 'normal'

        if drinkPos >= len(self.widgetList):
            drinkPos = 0
        elif drinkPos < 0:
            drinkPos = len(self.widgetList) - 1

        self.currentPos = drinkPos

        self.select_current()

    @mainthread
    def next_widget(self, direction, **kwargs):
        increment = -1 if direction < 0 else 1
        # print("RECEIVED NEXT WIDGET COMMAND")

        self.set_current(self.currentPos + increment)

        callback = kwargs.get("callback")
        if(callback and hasattr(callback, '__call__')):
            callback()

    def select_current(self):
        currentWidget = self.get_current_drink()

        currentWidget.state = 'down'

        self.ids.preview.source = os.path.abspath(currentWidget.img)

        self.ids.scrollview.scroll_to(currentWidget)

    def switch_image(self, instance):
        drinkPos = self.widgetList.index(instance)
        self.set_current(drinkPos)

    def get_current_drink(self):
        return  self.widgetList[self.currentPos]


class MainApp(App):

    config = AppConfig()
    dispenser = Dispenser(0x04)

    #drinks = [{'img': './images/shark_cat.jpg', 'name': 'Shark Cat'}, {'img': './images/Batman.jpg', 'name': 'Batman!'}, {'img': './images/squirtle.jpg', 'name': 'Squirtle'}]

    def __init__(self):
        self.setup_config()
        self.setup_repository()
        self.setup_dispenser()
        self.setup_encoder()

        self.drinks = self.repository.getAvailableDrinks()
        super().__init__()

    def setup_config(self):
        self.config.read(curpath + '/config.ini')

    def setup_repository(self):
        db_path = self.config['Database'].get('Path', 'data.db')

        if not os.path.isabs(db_path):
            db_path = os.path.join(curpath, db_path)

        self.repository = DrinkRepository(db_path)

    def setup_dispenser(self):
        addr = int(self.config['Dispenser'].get('Address', '0x00'), 16)

        single = int(self.config['Hardware'].get('SwitchSingle'))
        double = int(self.config['Hardware'].get('SwitchDouble'))

        self.dispenser = Dispenser(addr, spin=single, dpin=double)

    def setup_encoder(self):
        clk = int(self.config['Hardware'].get('RotaryClk'))
        dt = int(self.config['Hardware'].get('RotaryDt'))
        btn = int(self.config['Hardware'].get('SelectBtn'))

        r = int(self.config['Hardware'].get('rotaryRLED'))
        g = int(self.config['Hardware'].get('rotaryGLED'))
        b = int(self.config['Hardware'].get('rotaryBLED'))

        self.encoder = EncoderInput(clk, dt, btn, r, g, b)

    def build(self):
        self.screen = MainScreen(self.drinks)
        Window.bind(on_keyboard=self.check_hotkey)

        self.encoder.setupEncoderEvents(lambda dir: self.select_next(dir), self.dispense_current)

        return self.screen

    def check_hotkey(self, window, key, scancode, codepoint, modifier):
        # yay thanks https://stackoverflow.com/a/47922465/2993366
        if modifier == ['shift'] and codepoint.lower() == 'q':
            self.stop()

        elif modifier == [] and codepoint.lower() == 'enter':
            self.dispense_current()

    def select_next(self, dir):
        self.screen.next_widget(dir, callback=lambda: self.highlight_current())

    def highlight_current(self):
        drink_id = self.screen.get_current_drink().drink_id
        recipe = self.repository.getDrinkRecipe(drink_id)
        self.dispenser.highlightDrink(recipe)

    def dispense_current(self):
        self.dispense_drink(self.screen.get_current_drink().drink_id)

    def dispense_drink(self, drink_id):
        print(drink_id)
        recipe = self.repository.getDrinkRecipe(drink_id)

        #TODO: display dispensing message to screen
        self.dispenser.dispenseDrink(recipe)
        #remove dispensing message


if __name__ == '__main__':
    MainApp().run()