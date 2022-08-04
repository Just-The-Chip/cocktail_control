from imp import source_from_cache

from kivy.uix.gridlayout import GridLayout
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.modalview import ModalView
from kivy.uix.screenmanager import Screen
from kivy.clock import mainthread

from random import randint

import sys
import os

curpath = os.path.abspath(os.path.join(__file__, os.pardir))
if(curpath not in sys.path):
    sys.path.append(curpath)

from repository import DrinkRepository
from dispenser import Dispenser
from hardware import EncoderInput

from dispenser import DispenserStatus

class ScrollButton(ToggleButton):
    def __init__(self, **kwargs):
        image_name = kwargs.pop('img') or 'hola.png'
        self.img = curpath + '/images/' + image_name
        self.drink_id = kwargs.pop('drink_id')
        super(ScrollButton, self).__init__(**kwargs)

class RandomDrinkButton(ScrollButton):
    def __init__(self, **kwargs):
        kwargs.update({'img': 'RandomDrink.png', 'drink_id': -1})
        super(RandomDrinkButton, self).__init__(**kwargs)

class DispensingModal(ModalView):
    def __init__(self, **kwargs):
        super(DispensingModal, self).__init__(**kwargs)

class ErrorModal(ModalView):
    def __init__(self, **kwargs):
        self.err_msg = kwargs.pop('err_msg')
        super(ErrorModal, self).__init__(**kwargs)

class DrinkSelector(GridLayout):
    widgetList = []
    currentPos = 0
    modal = None

    def __init__(self, **kwargs):
        super(DrinkSelector, self).__init__(**kwargs)

        self.clear_drinks()

    def clear_drinks(self): 
        self.ids.preview.source = './images/hola.png'
        self.currentPos = 0

        container = self.ids.container

        for drinkWidget in self.widgetList:
            container.remove_widget(drinkWidget)

        self.widgetList = []

    def load_drinks(self, drinks):
        container = self.ids.container
        for drink in drinks:
            btn = ScrollButton(drink_id=drink['id'], img=drink['image'], text=drink['name'], on_press=self.switch_image)
            self.widgetList.append(btn)
            container.add_widget(btn)

        randomDrinkBtn = RandomDrinkButton(on_press=self.switch_image)

        self.widgetList.append(randomDrinkBtn)
        container.add_widget(randomDrinkBtn)

        self.select_current()

    def set_current(self, drinkPos):
        self.widgetList[self.currentPos].state = 'normal'

        if drinkPos >= len(self.widgetList):
            drinkPos = 0
        elif drinkPos < 0:
            drinkPos = len(self.widgetList) - 1

        self.currentPos = drinkPos

        self.select_current()

    def set_random(self):
        self.widgetList[self.currentPos].state = 'normal'

        # the last widget on the list is a random drink
        randomPos = randint(0, len(self.widgetList) -2)
        self.set_current(randomPos)

    @mainthread
    def next_widget(self, direction, **kwargs):
        increment = -1 if direction < 0 else 1
        # print("RECEIVED NEXT WIDGET COMMAND")

        self.set_current(self.currentPos + increment)

        callback = kwargs.get("callback")
        if(callback and hasattr(callback, '__call__')):
            callback()

    @mainthread
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

    @mainthread
    def open_dispensing_modal(self):
        self.dismiss_modal()
        self.modal = DispensingModal()
        self.modal.open()

    def open_error_modal(self, msg): 
        self.dismiss_modal()
        self.modal = ErrorModal(err_msg=msg)
        self.modal.open()

    def dismiss_modal(self):
        if self.modal:
            self.modal.dismiss(force=True)

        self.modal = None


class DrinkSelectorScreen(Screen):

    dispenser = Dispenser(0x04)
    drink_selector = None

    dispensing_modal_open = False
    error_modal_open = False

    #drinks = [{'img': './images/shark_cat.jpg', 'name': 'Shark Cat'}, {'img': './images/Batman.jpg', 'name': 'Batman!'}, {'img': './images/squirtle.jpg', 'name': 'Squirtle'}]

    def __init__(self, config, **kwargs):
        self.config = config
        self.setup_repository()
        self.setup_dispenser()
        self.setup_encoder()

        self.encoder.setupEncoderEvents(lambda dir: self.select_next(dir), self.handle_encoder_press)
        
        super(DrinkSelectorScreen, self).__init__(**kwargs)

    def setup_drink_selector(self): 
        if self.drink_selector is None: 
            self.drink_selector = DrinkSelector()
            self.add_widget(self.drink_selector)

        self.refresh_drinks()

    def refresh_drinks(self):
        self.drinks = self.repository.getAvailableDrinks()
        self.drink_selector.clear_drinks()
        self.drink_selector.load_drinks(self.drinks)

    def setup_repository(self):
        # print({section: dict(self.config[section]) for section in self.config.sections()})        
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

    def handle_hotkey(self, key, modifier):
        if modifier == [] and (key == 40 or key == 'enter'):
            print("enter key pressed!")
            self.handle_encoder_press()
            # if self.error_modal_open:
            #     self.handle_encoder_press()
            # else:
            #     self.dispenser_done(DispenserStatus.CANCEL)

    def handle_encoder_press(self):
        if self.error_modal_open: 
            self.allow_selection()
        elif not self.dispensing_modal_open:
            self.dispense_current()

    def dispenser_done(self, status):
        if status == DispenserStatus.READY:
            self.allow_selection()
            return

        err_msg = "Unknown error. Please consult your local nerd or try again. Status code: " + str(status)

        if status == DispenserStatus.REMOVED:
            err_msg = "Drink removed from dispensing area!"
        elif status == DispenserStatus.CANCEL:
            err_msg = "Drink cancelled. Please check for any empty ingredients."

        self.display_error(err_msg)

    def allow_selection(self):
        self.drink_selector.dismiss_modal()
        self.dispensing_modal_open = False
        self.error_modal_open = False
        self.encoder.enableInput()
        # remove dispensing popup

    def prevent_selection(self):
        self.drink_selector.open_dispensing_modal()
        self.dispensing_modal_open = True
        self.error_modal_open = False
        self.encoder.disableInput()
        # show dispensing popup

    def display_error(self, msg):
        self.drink_selector.open_error_modal(msg)
        self.dispensing_modal_open = False
        self.error_modal_open = True
        self.encoder.setWarningColor()
        # show error popup

    def select_next(self, dir):
        self.drink_selector.next_widget(dir, callback=lambda: self.highlight_current())

    def highlight_current(self):
        drink_id = self.drink_selector.get_current_drink().drink_id
        recipe = self.repository.getDrinkRecipe(drink_id)
        # self.dispenser.highlightDrink(recipe)

    def dispense_current(self):
        drink_id = self.drink_selector.get_current_drink().drink_id

        if (drink_id < 0):
            self.drink_selector.set_random()
            drink_id = self.drink_selector.get_current_drink().drink_id
            self.dispense_current()
        else:
            self.dispense_drink(drink_id)

    def dispense_drink(self, drink_id):
        print(drink_id)
        recipe = self.repository.getDrinkRecipe(drink_id)

        self.prevent_selection()
        self.dispenser.dispenseDrink(recipe, self.dispenser_done)