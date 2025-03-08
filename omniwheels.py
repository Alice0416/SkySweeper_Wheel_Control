import serial  # Import serial library for communication with iBus receiver
import time  # Import time library for delays
import pigpio  # Import pigpio library for PWM control on Raspberry Pi

# Initialize pigpio library (needed for controlling PWM signals)
pi = pigpio.pi()

# Define motor control GPIO pins on Raspberry Pi
MOTOR1_PWM = 2   # Motor 1 speed (PWM signal)
MOTOR1_DIR = 3   # Motor 1 direction
MOTOR2_PWM = 4   # Motor 2 speed (PWM signal)
MOTOR2_DIR = 5   # Motor 2 direction
MOTOR3_PWM = 6   # Motor 3 speed (PWM signal)
MOTOR3_DIR = 7   # Motor 3 direction

# Set GPIO pins as OUTPUT (like pinMode() in Arduino)
for pin in [MOTOR1_PWM, MOTOR1_DIR, MOTOR2_PWM, MOTOR2_DIR, MOTOR3_PWM, MOTOR3_DIR]:
    pi.set_mode(pin, pigpio.OUTPUT)

# Open iBus receiver serial connection (adjust port if needed)
# - '/dev/ttyS0' is the Raspberry Pi UART port
# - 115200 is the baud rate (matches iBus communication speed)
# - timeout=0.1 ensures we don't get stuck waiting for data
ser = serial.Serial('/dev/ttyS0', 115200, timeout=0.1)

# Function to read iBus channel data
def read_ibus():
    data = ser.read(32)  # Read 32 bytes of iBus packet data
    if len(data) < 32:
        return [1500] * 10  # Return default neutral values if no data received
    
    # Extract 10 channel values from the iBus packet
    channels = [int.from_bytes(data[i*2+2:i*2+4], 'little') for i in range(10)]
    return channels  # Return the list of 10 channel values

# Function to limit values within a specified range (equivalent to constrain() in Arduino)
def constrain(value, min_val, max_val):
    return max(min_val, min(max_val, value))

# Low-pass filter function to smooth out noisy stick inputs
def filter(value, prev_value, alpha=30):
    return (alpha * prev_value + value) / (alpha + 1)

# Function to set motor speed and direction
def set_motor(pwm_pin, dir_pin, speed):
    speed = constrain(speed, -255, 255)  # Limit speed between -255 and 255
    if speed >= 0:
        pi.write(dir_pin, 1)  # Set direction forward
        pi.set_PWM_dutycycle(pwm_pin, speed)  # Apply PWM signal
    else:
        pi.write(dir_pin, 0)  # Set direction reverse
        pi.set_PWM_dutycycle(pwm_pin, abs(speed))  # Apply PWM signal (absolute value)

# Initialize filtered values for smooth control
drive1_filtered = drive2_filtered = drive3_filtered = 0

# Track the last loop time (equivalent to millis() in Arduino)
previous_time = time.time()

# Main control loop (runs continuously)
while True:
    # Read RC controller stick values from iBus
    ch_values = read_ibus()

    # Extract relevant stick values (matching original C++ logic)
    ch4, ch2, ch5 = ch_values[3], ch_values[1], ch_values[4]

    # Convert iBus stick values (range: ~1000-2000) to centered values (-500 to 500)
    drive1 = ch4 - 1500  # Left/right movement
    drive2 = ch2 - 1500  # Forward/backward movement
    drive3 = ch5 - 1500  # Rotation movement

    # Apply filtering for smoother control
    drive1_filtered = filter(drive1, drive1_filtered)
    drive2_filtered = filter(drive2, drive2_filtered)
    drive3_filtered = filter(drive3, drive3_filtered)

    # Compute motor outputs using omnidirectional drive equations
    out1 = drive1 + (drive2 * 0.66) - drive3
    out2 = drive1 - (drive2 * 0.66) + drive3
    out3 = drive2 + drive3

    # Set motor speeds and directions
    set_motor(MOTOR1_PWM, MOTOR1_DIR, out1)
    set_motor(MOTOR2_PWM, MOTOR2_DIR, out2)
    set_motor(MOTOR3_PWM, MOTOR3_DIR, out3)

    # Run loop every 10 milliseconds (same as original C++ timing)
    time.sleep(0.01)
