from kivy.config import Config
Config.set('graphics', 'width', 800)
Config.set('graphics', 'height', 480)

from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.textinput import TextInput

import sys
import os

curpath = os.path.dirname(__file__)
if(curpath not in sys.path):
    sys.path.append(curpath)

from repository import DrinkRepository

class ScrollButton(ToggleButton):
    def __init__(self, **kwargs):
        self.img = kwargs.pop('img')
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

    def next_widget(self, direction):
        increment = -1 if direction < 0 else 1

        self.set_current(self.currentPos + increment)    
    
    def select_current(self):
        currentWidget = self.widgetList[self.currentPos]
        #todo: scroll to widget
        currentWidget.state = 'down'
        self.ids.preview.source = currentWidget.img

    def switch_image(self, instance):
        drinkPos = self.widgetList.index(instance)
        self.set_current(drinkPos)   


class MainApp(App):

    repository = DrinkRepository(os.path.join(curpath, 'data.db'))

    #drinks = [{'img': './images/shark_cat.jpg', 'name': 'Shark Cat'}, {'img': './images/Batman.jpg', 'name': 'Batman!'}, {'img': './images/squirtle.jpg', 'name': 'Squirtle'}]

    def __init__(self):
        self.drinks = self.repository.getAvailableDrinks()
        super().__init__()

    def build(self):
        return MainScreen(self.drinks)


if __name__ == '__main__':
    MainApp().run()