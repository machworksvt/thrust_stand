import RPi.GPIO as GPIO
import time
import csv
import threading
from pynput import keyboard

# --- GPIO Setup ---
SERVO_PIN = 18  # PWM Pin for servo
ENCODER_A = 23  # Encoder Channel A
ENCODER_B = 24  # Encoder Channel B

# --- Initialize Variables ---
encoder_position = 0
running = True

# --- Setup GPIO ---
GPIO.setmode(GPIO.BCM)
GPIO.setup(SERVO_PIN, GPIO.OUT)
GPIO.setup(ENCODER_A, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(ENCODER_B, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# --- Servo PWM Setup ---
pwm = GPIO.PWM(SERVO_PIN, 50)  # 50Hz PWM frequency
pwm.start(0)  # Start with 0 duty cycle

# --- Encoder Callback ---
def encoder_callback(channel):
    global encoder_position
    if GPIO.input(ENCODER_B) == GPIO.input(ENCODER_A):
        encoder_position += 1
    else:
        encoder_position -= 1

# --- Attach Interrupts ---
GPIO.add_event_detect(ENCODER_A, GPIO.BOTH, callback=encoder_callback)
GPIO.add_event_detect(ENCODER_B, GPIO.BOTH, callback=encoder_callback)

# --- Function to Convert Angle to PWM Duty Cycle ---
def angle_to_duty_cycle(angle):
    return (angle + 180) / 18 + 2.5  # Scale -180 to 180 degrees to 2.5% - 12.5% duty cycle

# --- Function to Control Servo ---
def move_servo():
    global running
    with open("servo_data.csv", "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Time", "Servo Angle", "Encoder Position"])  # Header row

        for angle in range(-180, 181, 10):  # Sweep from -180 to 180 degrees
            if not running:
                break
            duty_cycle = angle_to_duty_cycle(angle)
            pwm.ChangeDutyCycle(duty_cycle)  # Move servo
            writer.writerow([time.time(), angle, encoder_position])
            time.sleep(0.2)  # Delay for smooth motion

        # Sweep back to -180
        for angle in range(180, -181, -10):
            if not running:
                break
            duty_cycle = angle_to_duty_cycle(angle)
            pwm.ChangeDutyCycle(duty_cycle)
            writer.writerow([time.time(), angle, encoder_position])
            time.sleep(0.2)

    pwm.ChangeDutyCycle(0)  # Stop PWM

# --- Keyboard Listener to Stop ---
def on_press(key):
    global running
    if key == keyboard.Key.space:
        running = False
        pwm.stop()
        GPIO.cleanup()
        return False  # Stop listener

# --- Start Threads ---
servo_thread = threading.Thread(target=move_servo)
servo_thread.start()

# Listen for space key press to stop
with keyboard.Listener(on_press=on_press) as listener:
    listener.join()

print("Script stopped.")
