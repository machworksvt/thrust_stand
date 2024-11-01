import time
import tkinter as tk
from tkinter import simpledialog, messagebox
import RPi.GPIO as GPIO
from hx711 import HX711


GPIO.setmode(GPIO.BCM) 
hx = HX711(dout_pin=6, pd_sck_pin=5) # Defines hx to use hx711 python package


# Tkinter class

class Application(tk.Frame):
    
    #Initializes the GUI, any code that needs to run before the GUI opens goes in here
    def __init__(self, window=None):
        super().__init__(window)
        hx.zero() # Zeros the thrust sensor
        self.window = window
        self.running = False
        self.pack()
        self.create_widgets() # Generates the GUI based on the assets defined in create_widgets
        self.window.title("Thrust Sensor")
        self.root = root
        self.message_index = 0 
        self.CalibrationCoef = None
        self.calibration_messages = ['Press ENTER to start calibration', 
                                      'Place test stand on its side with arrow pointing down, then press ENTER',
                                      'Place known weight on stand, then press Enter']
                                    
        hx.set_scale_ratio(self.calib_entry) # Sets the scale ratio of the hx711 according to the calibration coef
                             
                                      
                                      

    # Defines widgets (text labels, buttons, etc) for the GUI
    def create_widgets(self):
        self.thrust_label = tk.Label(self, text='0.0 N', font=('Ariel', 80))
        self.thrust_label.pack()
        self.start_button = tk.Button(self, text='Start', height=5, width=7, font=('Ariel', 20), command=self.start)
        self.start_button.pack(side=tk.LEFT)
        self.stop_button = tk.Button(self, text='Stop', height=5, width=7, font=('Ariel', 20), command=self.stop)
        self.stop_button.pack(side=tk.RIGHT)
        self.reset_button = tk.Button(self, text='Reset', height=5, width=7, font=('Ariel', 20), command=self.reset)
        self.reset_button.pack(side=tk.BOTTOM)
        self.calibrate_button = tk.Button(self, text='Calibrate', height=5, width=7, font=('Ariel', 20), command=self.calibrate)
        self.calibrate_button.pack(side=tk.TOP)
        self.calib_entry_label = tk.Label(self, text='Calibration Coefficient', font=('Ariel', 14))
        self.calib_entry_label.pack()
        self.calib_entry = tk.Entry(self, font=('Ariel', 14))
        self.calib_entry.pack()
        self.set_calib_button = tk.Button(self, text='Set', font=('Ariel', 10), command=self.set_calibration)
        self.set_calib_button.pack(side=tk.LEFT)
    
    # Start function starts the sensor data flowing, also zeros sensor before each start
    def start(self):
        if not self.running:
            hx.zero()
            self.running = True
            self.update_force() # Starts updating the force readout by calling the update_force funcion

    #Resets the force display
    def reset(self):
        self.force = 0
        self.thrust_label.config(text='0.0 N')
    
    #Stops the data reading from the force sensor
    def stop(self):
        self.running = False
    
    # Reads the weight reading from the test stand and converts it to newtons
    def update_force(self):
        if self.running:
            self.weight = hx.get_weight_mean(1) # Gets the reading from the force sensor
            self.force = (self.weight/1000)*9.81
            self.thrust_label.config(text=f'{self.force:.2f} N') 
            self.thrust_label.after(100, self.update_force)  # Update every 100 ms
            
    def set_calibration(self):
        try:
            self.CalibrationCoef = float(self.calib_entry.get())
            hx.set_scale_ratio(self.CalibrationCoef)
            messagebox.showinfo("Calibration Set", f"Calibration coefficient set to {self.CalibrationCoef}")
        except ValueError:
            messagebox.showerror('Invalid Input', 'Please enter a valid number for calibration.')   
            
    # Starts the calibration procedure for the thrust sensor
    def calibrate(self):
        self.text_window = tk.Toplevel(self.root)
        self.text_window.title('Calibration')
        self.message_label = tk.Label(self.text_window, text=self.calibration_messages[self.message_index], font=('Ariel', 20))
        self.message_label.pack(pady=10)
        self.text_window.bind('<Return>', self.update_message)
       
        
    def update_message(self, event):
        if self.message_index <= 1:
            self.message_index += 1
            self.message_label.config(text=self.calibration_messages[self.message_index])
        elif self.message_index == 2:
            self.voltage = hx.get_data_mean(readings=1)
            self.message_index += 1
            self.text_window.destroy()
            self.input_known_weight()
        elif self.message_index == 3:
            self.message_label.config(text=self.calibration_messages[self.message_index])


        

            
    def input_known_weight(self):
        self.calibration_weight = tk.simpledialog.askfloat('Enter Value', 'Enter known weight in grams & press ENTER: ')
        if self.calibration_weight and self.voltage:
            self.CalibrationCoef = self.voltage/self.calibration_weight
            self.calib_entry.delete(0, tk.END)
            self.calib_entry.insert(0, f'{self.CalibrationCoef:.4f}')
            hx.set_scale_ratio(self.CalibrationCoef)
            messagebox.showinfo('calibration Updated', f"New calibration coefficient set to {self.CalibrationCoef}"  f"Place test stannd upright")
            self.message_index = 0
        
            
        
        
            

        
            
root = tk.Tk()
app = Application(window=root)
app.mainloop()
