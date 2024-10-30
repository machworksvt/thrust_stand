import time
#from pynput.keyboard import Key, Listener      the keyboard stuff isn't needed for the gui to work. leaving here in case we incorporate keyboard stuff later
import RPi.GPIO as GPIO
from hx711 import HX711
import tkinter as tk

class Application(tk.Frame):
    
    def __init__(self,window=None):
        super().__init__()  # Initialize the parent class (tk.Frame)
        
        self.window = window  # Store the window instance
        window.geometry("1250x500")  # Set the window size
        self.window.title("Thrust Sensor")  # Set the window title
        
        self.running = False  # Initialize the running state
        self.pack()  # Add the frame to the window
        self.create_widgets()  # Create the GUI widgets
        self.force = 0  # Initialize the force value
        

    def create_widgets(self):
        """Create the widgets for the GUI"""
        self.thrust_label = tk.Label(self, text = '0.00 N', font=('Ariel', 80))
        self.thrust_label.pack()
        
        "Creates the start button. Sets the size, font, and can do color as well. Also specifies where the widget will be placed (left)"
        self.start_button = tk.Button(self, text='Start',height=5, width= 7, font=('Ariel', 80), command=self.start)
        self.start_button.pack(side = tk.LEFT)
        
        "Creates the stop button. Sets the size, font, and can do color as well. Also specifies where the widget will be placed (right)"
        self.stop_button = tk.Button(self, text='Stop', height=5, width=7, font=('Ariel', 80), command=self.stop)
        self.stop_button.pack(side = tk.LEFT)
        
        "Creates the reset button. Sets the size, font, and can do color as well. Also specifies where the widget will be placed (bottom)"
        self.reset_button = tk.Button(self, text='Reset', height=5, width=7, font=('Ariel', 80), command=self.reset)
        self.reset_button.pack(side = tk.LEFT)

        "Creates the calibrate button. Sets the size, font, and can do color as well. Also specifies where the widget will be placed (top)"
        "This one will need work. Just adding in now so it's not forgotten"
        self.calibrate_button = tk.Button(self, text='Calibrate', height=5, width=7, font=('Ariel', 80), command=self.calibrate)
        self.calibrate_button.pack(side = tk.LEFT)

        self.log_button = tk.Button(self, text='Log', height=5, width=7, font=('Ariel', 80), command=self.log)
        self.log_button.pack(side = tk.LEFT)
    
    def start(self):
        """When the start button is pressed, if the current running state is not True, this function is called which changes the running state from it's default of False to True. It also updates the thrust value."""
        if not self.running:
            self.running = True
            self.update_thrust()

    def reset(self):
        """When the reset button is pressed, this function is called which resets the thrust value to 0.00 N."""
        self.force = 0
        self.thrust_label.config(text='0.00 N')

    def stop(self):
        """When the stop button is pressed, this function is called which changes the running state from True to False."""
        self.running = False

    def calibrate(self):
        """When the calibrate button is pressed, this function is called which will contain the calibration logic."""
        
        """This is a placeholder for now."""
        
        pass

    def update_thrust(self):
        """Text"""
        if self.running:
            "Need to put the force calulation stuff here"
            self.thrust_label.config(text=f'{self.force:.2f} N')
            self.thrust_label.after(100, self.update_thrust) # Update every 100 ms (1ms = 0.1sec)(can change this as needed)

    def set_force(self):
        """Text"""
        """weight = 0
        weight = hx.get_weight_mean(1)
        force = (weight/1000)*9.81
        self.force = force
        return force"""
        pass
        

root = tk.Tk()
app = Application(window=root)
app.mainloop()

GPIO.setmode(GPIO.BCM)

hx = HX711(dout_pin=6,pd_sck_pin=5)

CalibrationCoef = 55.7567

