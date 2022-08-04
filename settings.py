from kivy.uix.gridlayout import GridLayout
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.screenmanager import Screen

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
        self.ingredient_id = kwargs.pop('ingredient_id')
        super(IngredientMenuItem, self).__init__(**kwargs)

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
    _menu_open = False

    def __init__(self, **kwargs):
        self.repository = kwargs.pop('repository')
        self.scrollview = kwargs.pop('scrollview')
        self.confirm_callback = kwargs.pop('confirm_callback')
        super(IngredientMenu, self).__init__(**kwargs)

    def get_ingredients(self):
        return self.repository.getAll()

    def add_ingredient_option(self, ingredient, menuPos):
        menuItem = IngredientMenuItem(
            on_release=lambda _: self.set_current(menuPos), 
            current_pos=ingredient['jar_pos'], 
            ingredient_name=ingredient['name'],
            ingredient_id = ingredient["id"]
        )
        self.menuItems.append(menuItem)
        self.add_widget(menuItem)

        return menuItem

    def add_none_option(self):
        fake_ingredient = {"id": None, "jar_pos": None, "name": "--None--"}
        self.add_ingredient_option(fake_ingredient, 0)

    def confirm_selection(self):
        selectedIngredient = self.menuItems[self.currentPos]

        print(selectedIngredient.ingredient_name)
        self.confirm_callback(selectedIngredient.ingredient_id, self.selected_position)
        self.close()

    def open(self, selected_position):
        self.menuItems = []
        self.selected_position = selected_position

        sortedIngredients = sorted(self.get_ingredients(), key=lambda ingredient: ingredient['name'])

        self.add_none_option()

        i = 0
        for ingredient in sortedIngredients: 
            i += 1
            self.add_ingredient_option(ingredient, i)
            if ingredient['jar_pos'] == selected_position: 
                self.currentPos = i

        self.select_current()
        self._menu_open = True

    def close(self): 
        self.currentPos = 0

        for menu_item in self.menuItems:
            self.remove_widget(menu_item)

        self.menuItems = []
        self._menu_open = False

    def is_open(self):
        return self._menu_open

    def select_current(self):
        selected_option = self.menuItems[self.currentPos]
        self.scrollview.scroll_to(selected_option)
        selected_option.state = 'down'

    def set_current(self, menuPos):
        self.menuItems[self.currentPos].state = 'normal'

        if menuPos >= len(self.menuItems):
            menuPos = 0
        elif menuPos < 0:
            menuPos = len(self.menuItems) - 1

        self.currentPos = menuPos

        self.select_current()

    def next_menu_item(self, direction):
        increment = -1 if direction < 0 else 1
        # print("RECEIVED NEXT WIDGET COMMAND")

        self.set_current(self.currentPos + increment)


class IngredientSettings(GridLayout):
    widgetList = []
    currentPos = 0
    totalPositions = 22

    def __init__(self, **kwargs):
        self.repository = kwargs.pop('repository')
        super(IngredientSettings, self).__init__(**kwargs)

        self.build_menu()
        self.build_position_settings()

    def get_ingredients(self):
        return self.repository.getAll()

    def build_menu(self):
        self.menu = IngredientMenu(
            repository=self.repository, 
            scrollview=self.ids.menu_scrollview,
            confirm_callback=self.update_position
        )
        self.ids.menu_scrollview.add_widget(self.menu)

    def update_position(self, ingredient_id, position):
        self.repository.updateIngredient(ingredient_id, jar_pos=position)
        self.reload_position_settings()

    def build_position_settings(self): 
        container = self.ids.container
        ingredients = self.get_ingredients()

        for i in range(self.totalPositions):
            # btn = ScrollButton(drink_id=drink['id'], img=drink['image'], text=drink['name'], on_press=self.switch_image)
            positionIngredient = list(filter(lambda ingredient: ingredient['jar_pos'] == i + 1, ingredients))

            ingredientName = positionIngredient[0]['name'] if len(positionIngredient) > 0 else ''

            settingWidget = PositionSetting(
                jar_pos=i+1, 
                ingredient_name=ingredientName, 
                menu=self.menu
            )

            self.widgetList.append(settingWidget)
            container.add_widget(settingWidget)

        self.select_current()

    def destroy_position_settings(self):
        container = self.ids.container

        for drinkWidget in self.widgetList:
            container.remove_widget(drinkWidget)

        self.widgetList = []

    def reload_position_settings(self):
        self.destroy_position_settings()
        self.build_position_settings()

    def select_current(self):
        selected_position = self.widgetList[self.currentPos]
        self.ids.scrollview.scroll_to(selected_position)
        selected_position.ids.toggle_btn.state = 'down'
   
    def set_current(self, widgetPos):
        self.widgetList[self.currentPos].ids.toggle_btn.state = 'normal'

        if widgetPos >= len(self.widgetList):
            widgetPos = 0
        elif widgetPos < 0:
            widgetPos = len(self.widgetList) - 1

        self.currentPos = widgetPos

        self.select_current()

    def next_widget(self, direction):
        increment = -1 if direction < 0 else 1
        # print("RECEIVED NEXT WIDGET COMMAND")

        self.set_current(self.currentPos + increment)

    def handle_up_key(self):
        if self.menu.is_open():
            self.menu.next_menu_item(-1)
        else:
            self.next_widget(-1)

    def handle_down_key(self):
        if self.menu.is_open():
            self.menu.next_menu_item(1)
        else:
            self.next_widget(1)

    def handle_left_key(self):
        if self.menu.is_open():
            self.menu.close()

    def handle_right_key(self):
        currentWidget = self.widgetList[self.currentPos]
        print("Handle right key")
        print(currentWidget)

        if not self.menu.is_open() and currentWidget is not None:
            print("open menu")
            currentWidget.open_menu()

    def handle_enter_key(self):
        if self.menu.is_open():
            self.menu.confirm_selection()
        else:
            self.handle_right_key()

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

        if key == 40 or key == 'enter':
            self.ingredient_settings.handle_enter_key()

        elif key == 79 or key == 'right':
            self.ingredient_settings.handle_right_key()

        elif key == 80 or key == 'left':
            self.ingredient_settings.handle_left_key()

        elif key == 81 or key == 'down':
            self.ingredient_settings.handle_down_key()

        elif key == 82 or key == 'up':
            self.ingredient_settings.handle_up_key()

