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
        # self.menu = kwargs.pop('menu')
        super(IngredientMenuItem, self).__init__(**kwargs)

    # def select_ingredient(self):
    #     print("selected ingredient!")

class PositionSetting(GridLayout):
    def __init__(self, **kwargs):
        self.jar_pos = kwargs.pop('jar_pos')
        self.ingredient_name = kwargs.pop('ingredient_name')
        self.menu = kwargs.pop('menu')
        super(PositionSetting, self).__init__(**kwargs)

    def open_menu(self):
        self.menu.close()
        self.menu.open(self.jar_pos)
        print("open menu!")

    def close_menu(self): 
        self.menu.close()
        print("dismiss menu!")

class IngredientMenu(GridLayout):
    menuItems = []
    currentPos = 0
    selected_position = 0

    def __init__(self, **kwargs):
        self.repository = kwargs.pop('repository')
        self.scrollview = kwargs.pop('scrollview')
        super(IngredientMenu, self).__init__(**kwargs)

    def get_ingredients(self):
        return self.repository.getAll()

    def add_ingredient_option(self, ingredient):
        menuItem = IngredientMenuItem(
            on_release=lambda _: self.confirm_selection(ingredient), 
            current_pos=ingredient['jar_pos'], 
            ingredient_name=ingredient['name']
        )
        self.menuItems.append(menuItem)
        self.add_widget(menuItem)

        return menuItem

    def confirm_selection(self, ingredient):
        print(ingredient['name'])
        # update repository
        # callback for parent menu?
        self.close()

    def open(self, selected_position):
        self.menuItems = []
        self.selected_position = selected_position

        sortedIngredients = sorted(self.get_ingredients(), key=lambda ingredient: ingredient['name'])
        selected_option = None

        for ingredient in sortedIngredients: 
            option = self.add_ingredient_option(ingredient)
            if ingredient['jar_pos'] == selected_position: 
                selected_option = option
                self.currentPos = len(self.menuItems) - 1

        self.select_current()

    def select_current(self):
        selected_option = self.menuItems[self.currentPos]
        self.scrollview.scroll_to(selected_option)
        selected_option.state = 'down'

    def close(self): 
        self.currentPos = 0

        for menu_item in self.menuItems:
            self.remove_widget(menu_item)

        self.menuItems = []


class IngredientSettings(GridLayout):
    widgetList = []
    currentPos = 0
    totalPositions = 22

    def __init__(self, **kwargs):
        self.repository = kwargs.pop('repository')
        super(IngredientSettings, self).__init__(**kwargs)

        self.build_menu()
        self.build_position_settings()

    def destroy_position_settings(self): 
        # self.currentPos = 0

        container = self.ids.container

        for drinkWidget in self.widgetList:
            container.remove_widget(drinkWidget)

        self.widgetList = []

    def get_ingredients(self):
        return self.repository.getAll()

        # self.select_current()

    def build_menu(self):
        self.menu = IngredientMenu(repository=self.repository, scrollview=self.ids.menu_scrollview)
        self.ids.menu_scrollview.add_widget(self.menu)

    # def destroy_menu(self): 
    #     if self.menu is not None:
    #         self.ids.menu_scrollview.remove_widget(self.menu)

    #     self.menu = None

    def build_position_settings(self): 
        container = self.ids.container
        ingredients = self.get_ingredients()

        for i in range(self.totalPositions):
            # btn = ScrollButton(drink_id=drink['id'], img=drink['image'], text=drink['name'], on_press=self.switch_image)
            positionIngredient = list(filter(lambda ingredient: ingredient['jar_pos'] == i + 1, ingredients))

            ingredientName = positionIngredient[0]['name'] if len(positionIngredient) > 0 else ''

            settingWidget = PositionSetting(jar_pos=i+1, ingredient_name=ingredientName, menu=self.menu)

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
