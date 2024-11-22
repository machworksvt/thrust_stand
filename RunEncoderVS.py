import RPi.GPIO as GPIO
import time
import csv


# Servo pin setup
servo_pin = 12  # GPIO pin for the servo
GPIO.setmode(GPIO.BCM)  # BCM numbering
GPIO.setup(servo_pin, GPIO.OUT)  # Set as output
GPIO.setup(20, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(16, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

encoder_a = 20  # GPIO pin for encoder channel A
encoder_b = 16 # GPIO pin for encoder channel B

# PWM setup for servo
pwm = GPIO.PWM(servo_pin, 50)  # 50Hz frequency
pwm.start(0)  # Initialize at 0% duty cycle

# CSV file setup
csv_filename = 'encoder_test.csv'

# Rotary encoder position tracking
encoder_position = 0
current_stateA = 0
last_stateA = GPIO.input(encoder_a)

def set_angle(angle, writer):
    """Set servo angle and record angle with encoder position."""
    duty_cycle = 3 + (angle / 18)  # Maps 0-180 to 2-12 duty cycle
    pwm.ChangeDutyCycle(duty_cycle)
    current_stateA = GPIO.input(encoder_a)
    if current_stateA != last_stateA:
		if GPIO.input(encoder_b) != current_stateA:
			encoder_position += 1 #clockwise
		else:
			encoder_position += -1 #countercw 
		print(encoder_position)
	last_stateA = current_stateA
	print(f"Setting angle: {angle} deg -> Duty cycle: {duty_cycle:.2f}%, Encoder: {encoder_position}")
    writer.writerow([angle, duty_cycle, encoder_position])
    time.sleep(1)
    pwm.ChangeDutyCycle(0)  # Minimize jitter

# try:
	# while True:
		# current_stateA = GPIO.input(encoder_a) 
		# if current_stateA != last_stateA:
			# if GPIO.input(encoder_b) != current_stateA:
				# encoder_position += 1  # Clockwise rotation
			# else:
				# encoder_position += -1  # Counter-clockwise rotation
			# print(encoder_position)
		# last_stateA = current_stateA
		
try:
    with open(csv_filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Angle (deg)', 'Duty Cycle (%)', 'Encoder Position'])

        # Sweep servo angles while recording encoder data
        for angle in range(0, 181, 10):  # From 0 to 180 degrees
            set_angle(angle, writer)
            time.sleep(0.5)

        for angle in range(180, -1, -10):  # Back down from 180 to 0 degrees
            set_angle(angle, writer)
            time.sleep(0.5)

finally:
    pwm.stop()  # Stop the servo PWM signal
    GPIO.cleanup()  # Reset GPIO settings
				
	
					
except KeyboardInterrupt:				
	GPIO.cleanup
			
