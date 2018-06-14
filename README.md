# cocktail_control
Raspberry Pi code to control an automatic cocktail dispenser

# What it will do
This code will display a scrollable list of cocktails from the database that you can scroll through by turning a rotary knob. Once you have a drink selected, you will be able to press a button and the machine will automatically dispense the drink for you according to the recipe in the database.

# Current progress
We are using Kivy for the UI. Right now you can either click on a drink from the list directly or click on the "SCROLL UP" or "SCROLL DOWN" buttons to select the next or previous drink, which will simulate what happens when you turn the knob. Upon selecting a cocktail, the image of the cocktail will show up to the left of the list. There is also code to send commands to the arduino that will be connected to the pi. Hitting the `[ENTER]` key will send a message to the arduino to dispense the currently highlighted drink. 

Because of issues with the graphics driver that Kivy uses on Raspberry pi, the mouse is not visible on the screen and the application displays fullscreen no matter what, with no "X" button. The mouse issue won't be to much of a problem because the display will be controlled by physical buttons, but for now, you can hold down the mouse button and you will see a touch ring, which will help you navigate it. The bigger problem is the lack of a close button, so I added the hotkey `[SHIFT]` + `[Q]` to quit. `[CTRL]` + `[C]` also works when running from the terminal. *DO NOT RUN THIS FROM THONNY!* For whatever reason the keyboard inputs don't work when run from Thonny and you have to unplug the device and plug it back in if you want to exit the program.