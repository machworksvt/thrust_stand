import tkinter as tk

class VariableApp:
    def __init__(self, root):
        self.big_font = ("font", 24, "bold")
        self.little_font = ("font", 16)
        self.root = root
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
        self.label = tk.Label(root, text="Thrust: 0.0 N", font = self.big_font, bg="#333333", fg="white")
        self.label.grid(row=0, column=0, columnspan=3, sticky="nsew")

        # Create buttons
        self.start_button = self.create_button(root,"Start", 1, 0)
        self.stop_button = self.create_button(root, "Stop", 1, 1)
        self.reset_button = self.create_button(root, "Reset", 1, 2)
        self.log_button = self.create_button(root, "Log", 2, 0, 2)  # Log button spans two columns (0 and 1)
        self.calibrate_button = self.create_button(root, "Calibrate", 2, 2)

        # Create calibration Coefficient entry box and frame behind it
        self.calib_entry_bg = tk.Frame(root, bg="#555555")
        self.calib_entry_bg.grid(row=3, column=0, columnspan=3, sticky="nsew")
        self.calib_entry_label = tk.Entry(root, font=self.little_font, fg="grey", bg="#555555", bd=0, highlightthickness=0, insertbackground="white")
        self.calib_entry_label.insert(0, "Calibration Coefficient")
        self.calib_entry_label.bind("<FocusIn>", self.clear_placeholder)
        self.calib_entry_label.bind("<FocusOut>", self.add_placeholder)
        
        self.calib_entry_label.grid(row=3, column=0, columnspan=3, sticky="nsew",padx=15)

        self.set_calib_button = self.create_button(root, "Set", 3, 2)

        

    # hover effect for buttons
    def create_button(self, parent, text, row, col, colspan=1):
        
        button = tk.Button(parent, text=text, font=("TkDefaultFont", 14, "bold"), bg="#444444", fg="white")
        button.grid(row=row, column=col, columnspan=colspan, sticky="nsew")

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
        if self.calibration_entry.get() == "Calibration Coefficient":
            self.calibration_entry.delete(0, tk.END)
            self.calibration_entry.config(fg="white")

    # Add the placeholder text back if the entry box is empty when focus is lost
    def add_placeholder(self, event):
        if not self.calibration_entry.get():  # Only add placeholder if the field is empty
            self.calibration_entry.insert(0, "Calibration Coefficient")
            self.calibration_entry.config(font=self.little_font, fg="grey")
    
    # Validation function to allow only numbers
    def validate_input(self, new_value):
        if new_value == "" or new_value.isdigit() or new_value == ".":
            return True
        else:
            return False  # Reject input if it's not a number


if __name__ == "__main__":
    root = tk.Tk()
    app = VariableApp(root)
    root.mainloop()
