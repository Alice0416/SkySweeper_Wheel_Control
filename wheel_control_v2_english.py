import time
import RPi.GPIO as GPIO

# Set GPIO mode to BCM numbering
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)  # Disable GPIO warnings

# Define GPIO pins for motor control
pins = {
    'out1_positive': 17,  # Motor 1 forward
    'out1_negative': 18,  # Motor 1 reverse
    'out2_positive': 27,  # Motor 2 forward
    'out2_negative': 22,  # Motor 2 reverse
    'out3_positive': 23,  # Motor 3 forward
    'out3_negative': 24   # Motor 3 reverse
}

# Initialize PWM (100Hz frequency)
pwm = {}
for name, pin in pins.items():
    GPIO.setup(pin, GPIO.OUT)
    pwm[name] = GPIO.PWM(pin, 100)  # 100Hz PWM
    pwm[name].start(0)              # Start with 0% duty cycle

# Function to stop all motors
def stop():
    for name in pwm:
        pwm[name].ChangeDutyCycle(0)

# Function to move forward
def move_forward(speed=255):
    # speed: 0 to 255, controls how fast it moves
    out1 = speed   # Motor 1 forward
    out2 = speed   # Motor 2 forward
    out3 = speed   # Motor 3 forward
    control_motors(out1, out2, out3)

# Function to move backward
def move_backward(speed=255):
    out1 = -speed  # Motor 1 reverse
    out2 = -speed  # Motor 2 reverse
    out3 = -speed  # Motor 3 reverse
    control_motors(out1, out2, out3)

# Function to move left
def move_left(speed=255):
    out1 = speed   # Motor 1 forward
    out2 = -speed  # Motor 2 reverse
    out3 = 0       # Motor 3 stopped
    control_motors(out1, out2, out3)

# Function to move right
def move_right(speed=255):
    out1 = -speed  # Motor 1 reverse
    out2 = speed   # Motor 2 forward
    out3 = 0       # Motor 3 stopped
    control_motors(out1, out2, out3)

# Function to control the motors
def control_motors(out1, out2, out3):
    # Limit the range to -255 to 255
    out1 = max(-255, min(255, out1))
    out2 = max(-255, min(255, out2))
    out3 = max(-255, min(255, out3))

    # Motor 1 control
    if out1 >= 0:
        pwm['out1_positive'].ChangeDutyCycle(out1 / 255 * 100)
        pwm['out1_negative'].ChangeDutyCycle(0)
    else:
        pwm['out1_positive'].ChangeDutyCycle(0)
        pwm['out1_negative'].ChangeDutyCycle(abs(out1) / 255 * 100)

    # Motor 2 control
    if out2 >= 0:
        pwm['out2_positive'].ChangeDutyCycle(out2 / 255 * 100)
        pwm['out2_negative'].ChangeDutyCycle(0)
    else:
        pwm['out2_positive'].ChangeDutyCycle(0)
        pwm['out2_negative'].ChangeDutyCycle(abs(out2) / 255 * 100)

    # Motor 3 control
    if out3 >= 0:
        pwm['out3_positive'].ChangeDutyCycle(out3 / 255 * 100)
        pwm['out3_negative'].ChangeDutyCycle(0)
    else:
        pwm['out3_positive'].ChangeDutyCycle(0)
        pwm['out3_negative'].ChangeDutyCycle(abs(out3) / 255 * 100)

# Main function
def main():
    try:
        print("Starting the program...")
        # Example: Test each direction in sequence
        move_forward(200)  # Move forward at speed 200
        time.sleep(2)      # Wait 2 seconds
        stop()             # Stop
        time.sleep(1)      # Pause for 1 second

        move_backward(200) # Move backward
        time.sleep(2)
        stop()
        time.sleep(1)

        move_left(200)     # Move left
        time.sleep(2)
        stop()
        time.sleep(1)

        move_right(200)    # Move right
        time.sleep(2)
        stop()
        time.sleep(1)

    except KeyboardInterrupt:
        print("Program stopped")
    finally:
        stop()          # Ensure all motors stop
        for p in pwm.values():
            p.stop()    # Stop PWM signals
        GPIO.cleanup()  # Clean up GPIO resources

if __name__ == "__main__":
    main()