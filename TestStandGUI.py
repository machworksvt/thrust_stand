import time
import tkinter as tk
from tkinter import simpledialog, messagebox
import RPi.GPIO as GPIO
from hx711 import HX711
import csv


GPIO.setmode(GPIO.BCM) 
hx = HX711(dout_pin=6, pd_sck_pin=5) # Defines hx to use hx711 python package


# Tkinter class

class Application(tk.Frame):
    
    # Initializes the GUI, any code that needs to run before the GUI opens goes in here
    def __init__(self, window=None):
        super().__init__(window)
        hx.zero() # Zeros the thrust sensor
        self.window = window # Generated the main GUI window
        self.running = False
        self.logging = False
        self.pack()
        self.create_widgets() # Generates the GUI based on the assets defined in create_widgets
        self.window.title("Thrust Sensor")
        self.root = root
        self.calibration_message_index = 0 # Index is used in the calibration function to determine which message should be showing when
        self.CalibrationCoef = None
        # Calibration instructions are stored in this string 
        self.calibration_messages = ['Press ENTER to start calibration', 
                                      'Place test stand on its side with arrow pointing down, then press ENTER',
                                      'Place known weight on stand, then press Enter']
                                      
        self.filename = 'FileTEST.csv'    # Temporary hardcoded file name
        self.time = 0
    # Defines widgets for the GUI
    def create_widgets(self):

        # Generated the force read-out
        self.thrust_label = tk.Label(self, text='0.0 N', font=('Ariel', 80))
        self.thrust_label.pack()
        
        # Start button, when pressed runs the start() funtion
        self.start_button = tk.Button(self, text='Start', height=5, width=7, font=('Ariel', 20), command=self.start)
        self.start_button.pack(side=tk.LEFT)
        
        # Stop button, when pressed runs the stop() function
        self.stop_button = tk.Button(self, text='Stop', height=5, width=7, font=('Ariel', 20), command=self.stop)
        self.stop_button.pack(side=tk.RIGHT)

        #Log Button
        self.log_button = tk.Button(self, text='Log', height=5, width=7, font=('Ariel', 20), command=self.log)
        self.log_button.pack(side=tk.BOTTOM)

        # Reset button, when pressed runs the reset() function
        self.reset_button = tk.Button(self, text='Reset', height=5, width=7, font=('Ariel', 20), command=self.reset)
        self.reset_button.pack(side=tk.BOTTOM)
        
        # Calibrate button, when pressed runs the calibrate() function
        self.calibrate_button = tk.Button(self, text='Calibrate', height=5, width=7, font=('Ariel', 20), command=self.calibrate)
        self.calibrate_button.pack(side=tk.TOP)
        
        # Generates the calibration coefficient input box and button to set the calibration
        self.calib_entry_label = tk.Label(self, text='Calibration Coefficient', font=('Ariel', 14))
        self.calib_entry_label.pack()
        self.calib_entry = tk.Entry(self, font=('Ariel', 14))
        self.calib_entry.pack()
        self.set_calib_button = tk.Button(self, text='Set', font=('Ariel', 10), command=self.set_calibration)
        self.set_calib_button.pack(side=tk.LEFT)
    
    # Start function first zeros the force sensor, then sets the state of the application to running and runs the update_force() 
    def start(self):
        if not self.running:
            hx.zero()
            self.running = True
            self.update_force() 

    # Resets the force display back to zero
    def reset(self):
        self.force = 0
        self.thrust_label.config(text='0.0 N')
    
    # Stops the data reading from the force sensor by setting the application state to not running
    def stop(self):
        self.running = False
    
    # Reads the weight reading from the test stand and converts it to newtons. This function is self-updating so the force readout on the display updates in real-time every 100ms
    def update_force(self):
        if self.running:
            self.weight = hx.get_weight_mean(1) # Gets the reading from the force sensor
            self.force = (self.weight/1000)*9.81
            self.thrust_label.config(text=f'{self.force:.2f} N') 
            
            if self.logging:
                self.thrust_label.after(100, self.write_data)  # Writes data to csv and updates every 100 ms
                self.time += 0.1
                
            else:
                self.thrust_label.after(100, self.update_force) # Just updates force readout every 100 ms
            
                
    

    #This function writes data to a csv file
    def create_file(self):
        if self.logging:
            
            with open(self.filename, mode='a', newline='') as file:  # Opens/Creates CSV file
                writer = csv.writer(file)
                writer.writerow(['Time (s)','Thrust (N)'])# Header row
                self.write_data
                
                
    def write_data(self):
        
        with open(self.filename, mode='a', newline='') as file:  # Opens/Creates CSV file
            writer = csv.writer(file)
            writer.writerow([round(self.time,1),(self.force)])#writes every new value of time and thrust in column 1 and 2
         
        self.thrust_label.after(1, self.update_force)
                
    
    #This function uses the log button to toggle the state of self.logging
    def log(self):
        if not self.logging & self.running:
            self.logging = True
            self.log_button.config(text='Stop\nLogging')
            self.create_file()
            
        else:
            self.logging = False
            self.log_button.config(text='Log')

    
# The next four functions all have to do with the calibration process of the force sensor

    # This function takes the inputted calibration coefficient from the GUI and applies it to the force output to get accurate data.
    def set_calibration(self):
        try:
            self.CalibrationCoef = float(self.calib_entry.get()) # Accepts the inputed calibration coefficient
            hx.set_scale_ratio(self.CalibrationCoef) # Applies the calibration coefficient to the HX711
            
            messagebox.showinfo("Calibration Set", f"Calibration coefficient set to {self.CalibrationCoef}")
        except ValueError:
            messagebox.showerror('Invalid Input', 'Please enter a valid number for calibration.') 
    
    # This function starts the calibration procedure for the thrust sensor
    def calibrate(self):
        self.text_window = tk.Toplevel(self.root) # Opens the text window to diplay calibration instructions
        self.text_window.title('Calibration')
        self.calibration_message_label = tk.Label(self.text_window, text=self.calibration_messages[self.calibration_message_index], font=('Ariel', 20))
        self.calibration_message_label.pack(pady=10)
        self.text_window.bind('<Return>', self.update_calibration_message) # Updates message when the ENTER key is pressed
       
   # This function updates the message displayed in the calibration window based on the message_index    
    def update_calibration_message(self, event):
        if self.calibration_message_index <= 1:
            self.calibration_message_index += 1
            self.calibration_message_label.config(text=self.calibration_messages[self.calibration_message_index])
        elif self.calibration_message_index == 2:
            self.voltage = hx.get_data_mean(readings=1) # Takes the voltage reading with the known weight on the thrust senor 
            self.message_index += 1
            self.text_window.destroy() # Removes the current calibration text box
            self.calibration_input_known_weight() # Generates the numerical input text box
        elif self.calibration_message_index == 3:
            self.calibration_message_label.config(text=self.calibration_messages[self.calibration_message_index])
            
    # This function allows for an input of a know weight to set the calibration coefficient   
    def input_known_weight(self):
        self.calibration_weight = tk.simpledialog.askfloat('Enter Value', 'Enter known weight in grams & press ENTER: ')
        if self.calibration_weight and self.voltage:
            self.CalibrationCoef = self.voltage/self.calibration_weight # Calculates the calibration coefficient
            self.calib_entry.delete(0, tk.END)  # Deletes the current calibration coefficient
            self.calib_entry.insert(0, f'{self.CalibrationCoef:.4f}') # Inserts the new calibration coefficient
            hx.set_scale_ratio(self.CalibrationCoef) # Sets calibration coefficient as the sale ratio for the force sensor
            messagebox.showinfo('calibration Updated', f"New calibration coefficient set to {self.CalibrationCoef}"  f"Place test stannd upright")
            self.message_index = 0
        
                    
root = tk.Tk()
app = Application(window=root)
app.mainloop()
