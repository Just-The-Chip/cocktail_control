from kivy.uix.dropdown import DropDown
from kivy.uix.gridlayout import GridLayout
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.screenmanager import Screen
from kivy.uix.image import Image
from kivy.clock import mainthread

import sys
import os

curpath = os.path.abspath(os.path.join(__file__, os.pardir))
if(curpath not in sys.path):
    sys.path.append(curpath)

from repository import IngredientRepository

class IngredientMenuItem(ToggleButton):
    def __init__(self, **kwargs):
        self.current_pos = kwargs.pop('current_pos')
        self.ingredient_name = kwargs.pop('ingredient_name')
        # self.dropdown = kwargs.pop('dropdown')
        super(IngredientMenuItem, self).__init__(**kwargs)

    def select_ingredient(self):
        print("selected ingredient!")

class PositionSetting(GridLayout):
    def __init__(self, **kwargs):
        self.jar_pos = kwargs.pop('jar_pos')
        self.ingredient_name = kwargs.pop('ingredient_name')
        # self.dropdown = kwargs.pop('dropdown')
        super(PositionSetting, self).__init__(**kwargs)

    def open_dropdown(self, btn):
        # self.dropdown.open(btn)
        print("open dropdown!")

    def dismiss_dropdown(self): 
        # self.dropdown.dismiss()
        print("dismiss dropdown!")

class IngredientSettings(GridLayout):
    widgetList = []
    currentPos = 0
    totalPositions = 22

    def __init__(self, **kwargs):
        self.repository = kwargs.pop('repository')
        super(IngredientSettings, self).__init__(**kwargs)

        self.load_ingredients()
        self.build_menu()
        self.build_position_settings()

    # def clear_drinks(self): 
    #     self.ids.preview.source = './images/hola.png'
    #     self.currentPos = 0

    #     container = self.ids.container

    #     for drinkWidget in self.widgetList:
    #         container.remove_widget(drinkWidget)

    #     self.widgetList = []

    def load_ingredients(self):
        self.ingredients = self.repository.getAll()

        # self.select_current()

    def build_menu(self):
        menu = self.ids.menu

        sortedIngredients = sorted(self.ingredients, key=lambda ingredient: ingredient['name'])
        self.dropdownItems = []

        for ingredient in sortedIngredients: 
            dropdownItem = IngredientMenuItem(current_pos=ingredient['jar_pos'], ingredient_name=ingredient['name'])
            self.dropdownItems.append(dropdownItem)
            menu.add_widget(dropdownItem)


    def build_position_settings(self): 
        container = self.ids.container

        for i in range(self.totalPositions):
            # btn = ScrollButton(drink_id=drink['id'], img=drink['image'], text=drink['name'], on_press=self.switch_image)
            positionIngredient = list(filter(lambda ingredient: ingredient['jar_pos'] == i + 1, self.ingredients))

            ingredientName = positionIngredient[0]['name'] if len(positionIngredient) > 0 else ''

            settingWidget = PositionSetting(jar_pos=i+1, ingredient_name=ingredientName)

            self.widgetList.append(settingWidget)
            container.add_widget(settingWidget)

   
    # def set_current(self, drinkPos):
    #     self.widgetList[self.currentPos].state = 'normal'

    #     if drinkPos >= len(self.widgetList):
    #         drinkPos = 0
    #     elif drinkPos < 0:
    #         drinkPos = len(self.widgetList) - 1

    #     self.currentPos = drinkPos

    #     self.select_current()

    # def next_widget(self, direction, **kwargs):
    #     increment = -1 if direction < 0 else 1
    #     # print("RECEIVED NEXT WIDGET COMMAND")

    #     self.set_current(self.currentPos + increment)

    #     callback = kwargs.get("callback")
    #     if(callback and hasattr(callback, '__call__')):
    #         callback()

    # def select_current(self):
    #     currentWidget = self.get_current_drink()

    #     currentWidget.state = 'down'

    #     self.ids.preview.source = os.path.abspath(currentWidget.img)

    #     self.ids.scrollview.scroll_to(currentWidget)

    # def get_current_drink(self):
    #     return  self.widgetList[self.currentPos]

class SettingsScreen(Screen):

    ingredient_settings = None

    def __init__(self, config, **kwargs):
        self.config = config
        self.setup_repository()
        
        super(SettingsScreen, self).__init__(**kwargs)

    def setup_ingredient_settings(self): 
        if self.ingredient_settings is None: 
            self.ingredient_settings = IngredientSettings(repository=self.repository)
            self.add_widget(self.ingredient_settings)

    def setup_repository(self):
        # print({section: dict(self.config[section]) for section in self.config.sections()})        
        db_path = self.config['Database'].get('Path', 'data.db')

        if not os.path.isabs(db_path):
            db_path = os.path.join(curpath, db_path)

        self.repository = IngredientRepository(db_path)

    def handle_hotkey(self, key, modifier):
        print(key)
        print(modifier)
        if modifier == [] and (key == 40 or key == 'enter'):
            print("enter keeeeyyyyyy")

    # def select_next(self, dir):
    #     self.ingredient_settings.next_widget(dir, callback=lambda: self.highlight_current())
