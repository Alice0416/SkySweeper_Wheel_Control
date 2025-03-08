import serial
import time
import pigpio

# Initialize pigpio library for PWM
pi = pigpio.pi()

# Define motor control GPIO pins
MOTOR1_PWM = 2
MOTOR1_DIR = 3
MOTOR2_PWM = 4
MOTOR2_DIR = 5
MOTOR3_PWM = 6
MOTOR3_DIR = 7

# Set GPIO modes
for pin in [MOTOR1_PWM, MOTOR1_DIR, MOTOR2_PWM, MOTOR2_DIR, MOTOR3_PWM, MOTOR3_DIR]:
    pi.set_mode(pin, pigpio.OUTPUT)

# Open iBus receiver (adjust port if needed)
ser = serial.Serial('/dev/ttyS0', 115200, timeout=0.1)

# Function to read iBus channel data
def read_ibus():
    data = ser.read(32)  # Read iBus packet
    if len(data) < 32:
        return [1500] * 10  # Default values if no data received
    channels = [int.from_bytes(data[i*2+2:i*2+4], 'little') for i in range(10)]
    return channels

# Function to limit values
def constrain(value, min_val, max_val):
    return max(min_val, min(max_val, value))

# Low-pass filter function
def filter(value, prev_value, alpha=30):
    return (alpha * prev_value + value) / (alpha + 1)

# Motor control function
def set_motor(pwm_pin, dir_pin, speed):
    speed = constrain(speed, -255, 255)
    if speed >= 0:
        pi.write(dir_pin, 1)
        pi.set_PWM_dutycycle(pwm_pin, speed)
    else:
        pi.write(dir_pin, 0)
        pi.set_PWM_dutycycle(pwm_pin, abs(speed))

# Main loop
drive1_filtered = drive2_filtered = drive3_filtered = 0
previous_time = time.time()

while True:
    ch_values = read_ibus()
    
    ch4, ch2, ch5 = ch_values[3], ch_values[1], ch_values[4]  # Stick values

    drive1 = ch4 - 1500
    drive2 = ch2 - 1500
    drive3 = ch5 - 1500

    drive1_filtered = filter(drive1, drive1_filtered)
    drive2_filtered = filter(drive2, drive2_filtered)
    drive3_filtered = filter(drive3, drive3_filtered)

    out1 = drive1 + (drive2 * 0.66) - drive3
    out2 = drive1 - (drive2 * 0.66) + drive3
    out3 = drive2 + drive3

    # Set motors
    set_motor(MOTOR1_PWM, MOTOR1_DIR, out1)
    set_motor(MOTOR2_PWM, MOTOR2_DIR, out2)
    set_motor(MOTOR3_PWM, MOTOR3_DIR, out3)

    time.sleep(0.01)  # 10ms loop
