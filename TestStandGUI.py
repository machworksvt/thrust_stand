import time
import tkinter as tk
from tkinter import simpledialog, messagebox
from tkinter import *
import RPi.GPIO as GPIO
from hx711 import HX711
import csv
from datetime import datetime

GPIO.setwarnings(False)
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
        self.log_ready = False
        self.logging = False
        self.logi = 1
        self.date = datetime.now()
        self.root = root
        self.calibration_message_index = 0 # Index is used in the calibration function to determine which message should be showing when
        self.CalibrationCoef = None
        # Calibration instructions are stored in this string 
        self.calibration_messages = ['Press ENTER to start calibration', 
                                      'Place test stand on its side with arrow pointing down, then press ENTER',
                                      'Place known weight on stand, then press Enter']
                                      
        self.time = 0
        self.big_font = ("font", 24, "bold")
        self.little_font = ("font", 16)
       
        self.root.title("Test Stand Dashboard")
        
        # Set background color
        self.root.configure(bg="#333333")

        # Set initial window size
        self.root.geometry("700x400")

        # Set the minimum window size to ensure no text gets cut off
        self.root.minsize(600, 400)

        # set weight of columns
        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=1)
        self.root.columnconfigure(2, weight=1)
        
        # set weight of rows
        self.root.rowconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)
        self.root.rowconfigure(2, weight=1)
        self.root.rowconfigure(3, weight=1)

        # Initialize variable for display purposes (static value for now)
        self.current_value = 0

        # Create data labels
        self.thrust_label = tk.Label(root, text="Thrust: 0.0 N", font = self.big_font, bg="#333333", fg="white")
        self.thrust_label.grid(row=0, column=1, columnspan=2, sticky="nsew")
        
        # Create run-time label
        self.time_label = tk.Label(root, text="00:00.0", font = self.big_font, bg="#333333", fg="white")
        self.time_label.grid(row=0, column=0, columnspan=1, sticky="nsew")
        # Create buttons
        self.start_button = self.create_button(self.start, root,"Start", 1, 0)
        self.stop_button = self.create_button(self.stop, root, "Stop", 1, 1)
        self.reset_button = self.create_button(self.reset, root, "Reset", 1, 2)
        self.log_button = self.create_button(self.log, root, "Log", 2, 0, 2)  # Log button spans two columns (0 and 1)
        self.calibrate_button = self.create_button(self.calibrate, root, "Calibrate", 2, 2)

        # Create calibration Coefficient entry box and frame behind it
        self.calib_entry_bg = tk.Frame(root, bg="#555555")
        self.calib_entry_bg.grid(row=3, column=0, columnspan=3, sticky="nsew")
        self.calib_entry_label = tk.Entry(root, font=self.little_font, fg="grey", bg="#555555", bd=0, highlightthickness=0, insertbackground="white")
        self.calib_entry_label.insert(0, "Calibration Coefficient")
        self.calib_entry_label.bind("<FocusIn>", self.clear_placeholder)
        self.calib_entry_label.bind("<FocusOut>", self.add_placeholder)
        
        self.calib_entry_label.grid(row=3, column=0, columnspan=3, sticky="nsew",padx=15)

        self.set_calib_button = self.create_button(self.set_calibration, root, "Set", 3, 2)

        

    # hover effect for buttons
    def create_button(self, func_name, parent, text, row, col, colspan=1):
        
        button = tk.Button(parent, text=text, font=("TkDefaultFont", 14, "bold"), bg="#444444", fg="white")
        button.grid(row=row, column=col, columnspan=colspan, sticky="nsew")
        button.config(command=func_name)
        # Bind hover events
        button.bind("<Enter>", lambda e, b=button: self.on_hover(b))
        button.bind("<Leave>", lambda e, b=button: self.on_leave(b))
        
        return button
    
    # Change button color when hovered over
    def on_hover(self, button):
        
        button.config(bg="#555555")

    # Return button color to normal when mouse leaves
    def on_leave(self, button):
             
        button.config(bg="#444444")

    # Clear the placeholder text when the user clicks inside the entry box
    def clear_placeholder(self, event):
        if self.calib_entry_label.get() == "Calibration Coefficient":
            self.calib_entry_label.delete(0, tk.END)
            self.calib_entry_label.config(fg="white")

    # Add the placeholder text back if the entry box is empty when focus is lost
    def add_placeholder(self, event):
        if not self.calib_entry_label.get():  # Only add placeholder if the field is empty
            self.calib_entry_label.insert(0, "Calibration Coefficient")
            self.calib_entry_label.config(font=self.little_font, fg="grey")
    
    # Validation function to allow only numbers
    def validate_input(self, new_value):
        if new_value == "" or new_value.isdigit() or new_value == ".":
            return True
        else:
            return False  # Reject input if it's not a number
    
    # Start function first zeros the force sensor, then sets the state of the application to running and runs the update_force() 
    def start(self):
        if not self.running:
            hx.zero()
            self.running = True
            self.update_force() 

    # Resets the force display back to zero
    def reset(self):
        self.force = 0
        self.time = 0
        self.thrust_label.config(text='0.0 N')
        self.time_label.config(text='00:00.0')
    
    # Stops the data reading from the force sensor by setting the application state to not running
    def stop(self):
        self.running = False
    
    # Reads the weight reading from the test stand and converts it to newtons. This function is self-updating so the force readout on the display updates in real-time every 100ms
    def update_force(self):
        if self.running:
            self.weight = hx.get_weight_mean(1) # Gets the reading from the force sensor
            self.force = (self.weight/1000)*9.81
            self.thrust_label.config(text=f'{self.force:.2f} N') 
            
            if self.logi == 3:
                self.thrust_label.after(100, self.write_data)  # Writes data to csv and updates every 100 ms
                self.time += 0.1
                self.minutes = int(self.time//60)
                
                self.seconds_float = self.time%60 
                self.tenths = int((self.seconds_float%1)*10)
                self.seconds_int = int(self.seconds_float - self.tenths/10)
                self.time_label.config(text=f"{self.minutes:02d}:{self.seconds_int:02d}.{self.tenths}")
                
            else:
                self.thrust_label.after(100, self.update_force) # Just updates force readout every 100 ms

    #This function writes data to a csv file
    def create_file(self):
        if self.logi == 3:
            
            with open(self.filename, mode='a', newline='') as file:  # Opens/Creates CSV file
                writer = csv.writer(file)
                writer.writerow(['Time (s)','Thrust (N)'])# Header row
                self.write_data(self.filename)
                
                
    def write_data(self):
        
        with open(self.filename, mode='a', newline='') as file:  # Opens/Creates CSV file
            writer = csv.writer(file)
            writer.writerow([round(self.time,1),round(self.force,3)])#writes every new value of time and thrust in column 1 and 2
         
        self.thrust_label.after(1, self.update_force)
                
    
    #This function uses the log button to toggle the state of self.logging
    def log(self):
        
        
        if self.logi == 1:
            
            self.log_button.config(text='Start Logging')
            self.open_log_window()
            self.logi += 1
            
        elif self.logi == 2:
            self.log_button.config(text='Stop Logging')
            self.logi += 1
                                                                                                                                                                                                                                                                                                         
        else:
            self.log_button.config(text='Log')
            self.logi += -2
    
    def open_log_window(self):
        self.log_window = Toplevel(root)
        self.log_window.title("Choose Save Method")
        self.log_window.geometry("300x300")
        
        self.log_window.columnconfigure(0, weight=1)
        self.log_window.columnconfigure(1, weight=1)

        self.log_window.rowconfigure(0, weight=1)
        self.log_window.rowconfigure(1, weight=1)
        
        self.file_save_method_label=tk.Label(self.log_window, text= "Save Method?", font=self.big_font, bg="#333333", fg="white")
        self.file_save_method_label.grid(row=0, column=0, columnspan=2, sticky="nsew")
        
        self.automatic_button=self.create_button(self.auto_save, self.log_window, "Auto", 1, 0)
        self.manual_button=self.create_button(self.nothing, self.log_window, "Manual", 1, 1)

    def nothing(self):
        
         return
         
    def auto_save(self):
        now = datetime.now()
        
        self.formatted_date = now.strftime("%m-%d-%Y")
        self.formatted_time = now.strftime("%H:%M:%S")
        
        self.filename = f"Test Run {self.formatted_date} {self.formatted_time}"
        self.create_file
        self.log_window.destroy()
        
        

    
# The next four functions all have to do with the calibration process of the force sensor

    # This function takes the inputted calibration coefficient from the GUI and applies it to the force output to get accurate data.
    def set_calibration(self):
        try:
            self.CalibrationCoef = float(self.calib_entry_label.get()) # Accepts the inputed calibration coefficient
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
            self.calibration_message_index += 1
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
