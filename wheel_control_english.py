import serial
import time
import RPi.GPIO as GPIO

# Set up the serial connection to the IBus receiver
serial_port = serial.Serial('/dev/ttyS0', 115200, timeout=1)
# The Raspberry Pi listens to the IBus receiver through its serial port (/dev/ttyS0) at 115200 baud. This is how it gets joystick data.

# Configure GPIO pins using BCM numbering
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)  # Ignore GPIO warnings
# The Pi uses BCM numbering (e.g., GPIO17) for its pins, not physical pin numbers. Warnings are turned off to avoid clutter.

# Define GPIO pins for motor control
pins = {
    'out1_positive': 17,  # Motor 1 forward
    'out1_negative': 18,  # Motor 1 reverse
    'out2_positive': 27,  # Motor 2 forward
    'out2_negative': 22,  # Motor 2 reverse
    'out3_positive': 23,  # Motor 3 forward
    'out3_negative': 24   # Motor 3 reverse
}
# Each motor has two pins: one for forward (positive) and one for reverse (negative). These are wired to a motor driver (e.g., H-bridge).

# Set up PWM on each pin
pwm = {}
for name, pin in pins.items():
    GPIO.setup(pin, GPIO.OUT)
    pwm[name] = GPIO.PWM(pin, 100)  # 100Hz PWM
    pwm[name].start(0)              # Start at 0% duty cycle
# The Pi sets these pins as outputs and creates PWM signals at 100Hz (100 pulses per second). Initially, all motors are off (0% duty cycle).

# Function to read IBus channels (placeholder)
def read_channel(channel):
    serial_port.write(f"read_ch{channel}\n".encode())
    time.sleep(0.01)
    response = serial_port.readline().decode().strip()
    try:
        return int(response)
    except ValueError:
        return 1500  # Default neutral value
# This function is meant to get joystick data (1000-2000) from the IBus receiver. Right now, it’s a dummy—it sends a command and expects a number back. If it fails, it assumes neutral (1500). You’d replace this with real IBus parsing.

# Adjust raw IBus values to motor range
def threshold_stick(value):
    value = max(1000, min(2000, value))  # Limit to 1000-2000
    return (value - 1500) / 500 * 255   # Map to -255 to 255
# Takes IBus values (1000-2000, where 1500 is neutral) and converts them to -255 (full reverse) to 255 (full forward) for motor control.

# Smooth the signal to avoid sudden jumps
def filter(new_value, old_value, strength):
    return (new_value * (100 - strength) + old_value * strength) / 100
# Smooths the signal so the motors don’t jerk. It blends 70% of the new value with 30% of the old value (strength=30).

# Main control loop
def main():
    drive1_filtered = 0
    drive2_filtered = 0
    drive3_filtered = 0
    previous_time = time.time() * 1000  # Start time in milliseconds
    # Initialize filtered values at 0 and set up timing.

    try:
        while True:
            current_time = time.time() * 1000
            if current_time - previous_time >= 10:  # Run every 10ms
                previous_time = current_time
                # Check the clock. If 10ms have passed, update everything.

                # Get joystick inputs
                ch2 = read_channel(1)  # Channel 1
                ch4 = read_channel(3)  # Channel 3
                ch5 = read_channel(4)  # Channel 4
                # Read three channels from the IBus receiver (e.g., joystick axes).

                # Process the inputs
                drive1 = threshold_stick(ch4)
                drive2 = threshold_stick(ch2)
                drive3 = threshold_stick(ch5)
                # Convert raw inputs to motor-friendly values (-255 to 255).

                # Smooth the inputs
                drive1_filtered = filter(drive1, drive1_filtered, 30)
                drive2_filtered = filter(drive2, drive2_filtered, 30)
                drive3_filtered = filter(drive3, drive3_filtered, 30)
                # Smooth the signals to make motion less twitchy.

                # Mix signals for motor outputs
                out1 = drive1_filtered + (drive2_filtered * 0.66) - drive3_filtered
                out2 = drive1_filtered - (drive2_filtered * 0.66) + drive3_filtered
                out3 = drive2_filtered + drive3_filtered
                # Combine the inputs to control three motors. This “mixing” decides how each motor contributes to movement (e.g., for a three-wheeled robot).

                # Limit motor values
                out1 = max(-255, min(255, out1))
                out2 = max(-255, min(255, out2))
                out3 = max(-255, min(255, out3))
                # Keep motor signals between -255 and 255 so they don’t exceed PWM limits.

                # Drive Motor 1
                if out1 >= 0:
                    pwm['out1_positive'].ChangeDutyCycle(out1 / 255 * 100)
                    pwm['out1_negative'].ChangeDutyCycle(0)
                else:
                    pwm['out1_positive'].ChangeDutyCycle(0)
                    pwm['out1_negative'].ChangeDutyCycle(abs(out1) / 255 * 100)
                # If out1 is positive, spin Motor 1 forward (0-100% speed). If negative, spin it backward.

                # Drive Motor 2
                if out2 >= 0:
                    pwm['out2_positive'].ChangeDutyCycle(out2 / 255 * 100)
                    pwm['out2_negative'].ChangeDutyCycle(0)
                else:
                    pwm['out2_positive'].ChangeDutyCycle(0)
                    pwm['out2_negative'].ChangeDutyCycle(abs(out2) / 255 * 100)
                # Same for Motor 2.

                # Drive Motor 3
                if out3 >= 0:
                    pwm['out3_positive'].ChangeDutyCycle(out3 / 255 * 100)
                    pwm['out3_negative'].ChangeDutyCycle(0)
                else:
                    pwm['out3_positive'].ChangeDutyCycle(0)
                    pwm['out3_negative'].ChangeDutyCycle(abs(out3) / 255 * 100)
                # Same for Motor 3. Duty cycle (0-100%) controls speed.

    except KeyboardInterrupt:
        print("Program terminated")
    finally:
        for p in pwm.values():
            p.stop()
        GPIO.cleanup()
        serial_port.close()
        # If you press Ctrl+C, stop the motors, free the GPIO pins, and close the serial port cleanly.

if __name__ == "__main__":
    main()
# Start the program.