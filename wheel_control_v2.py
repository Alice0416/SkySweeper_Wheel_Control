import time
import RPi.GPIO as GPIO

# 设置GPIO模式为BCM编号
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# 定义GPIO引脚
pins = {
    'out1_positive': 17,  # 电机1正转
    'out1_negative': 18,  # 电机1反转
    'out2_positive': 27,  # 电机2正转
    'out2_negative': 22,  # 电机2反转
    'out3_positive': 23,  # 电机3正转
    'out3_negative': 24   # 电机3反转
}

# 初始化PWM（频率100Hz）
pwm = {}
for name, pin in pins.items():
    GPIO.setup(pin, GPIO.OUT)
    pwm[name] = GPIO.PWM(pin, 100)
    pwm[name].start(0)

# 停止所有电机
def stop():
    for name in pwm:
        pwm[name].ChangeDutyCycle(0)

# 往前走
def move_forward(speed=255):
    # speed: 0到255，控制速度
    out1 = speed   # 电机1正转
    out2 = speed   # 电机2正转
    out3 = speed   # 电机3正转
    control_motors(out1, out2, out3)

# 往后走
def move_backward(speed=255):
    out1 = -speed  # 电机1反转
    out2 = -speed  # 电机2反转
    out3 = -speed  # 电机3反转
    control_motors(out1, out2, out3)

# 往左走
def move_left(speed=255):
    out1 = speed   # 电机1正转
    out2 = -speed  # 电机2反转
    out3 = 0       # 电机3停止
    control_motors(out1, out2, out3)

# 往右走
def move_right(speed=255):
    out1 = -speed  # 电机1反转
    out2 = speed   # 电机2正转
    out3 = 0       # 电机3停止
    control_motors(out1, out2, out3)

# 控制电机输出的通用函数
def control_motors(out1, out2, out3):
    # 限制范围
    out1 = max(-255, min(255, out1))
    out2 = max(-255, min(255, out2))
    out3 = max(-255, min(255, out3))

    # 电机1
    if out1 >= 0:
        pwm['out1_positive'].ChangeDutyCycle(out1 / 255 * 100)
        pwm['out1_negative'].ChangeDutyCycle(0)
    else:
        pwm['out1_positive'].ChangeDutyCycle(0)
        pwm['out1_negative'].ChangeDutyCycle(abs(out1) / 255 * 100)

    # 电机2
    if out2 >= 0:
        pwm['out2_positive'].ChangeDutyCycle(out2 / 255 * 100)
        pwm['out2_negative'].ChangeDutyCycle(0)
    else:
        pwm['out2_positive'].ChangeDutyCycle(0)
        pwm['out2_negative'].ChangeDutyCycle(abs(out2) / 255 * 100)

    # 电机3
    if out3 >= 0:
        pwm['out3_positive'].ChangeDutyCycle(out3 / 255 * 100)
        pwm['out3_negative'].ChangeDutyCycle(0)
    else:
        pwm['out3_positive'].ChangeDutyCycle(0)
        pwm['out3_negative'].ChangeDutyCycle(abs(out3) / 255 * 100)

# 主函数
def main():
    try:
        print("开始运行...")
        # 示例：按顺序测试每个方向
        move_forward(200)  # 前进，速度200
        time.sleep(2)      # 等2秒
        stop()             # 停下来
        time.sleep(1)

        move_backward(200) # 后退
        time.sleep(2)
        stop()
        time.sleep(1)

        move_left(200)     # 左移
        time.sleep(2)
        stop()
        time.sleep(1)

        move_right(200)    # 右移
        time.sleep(2)
        stop()
        time.sleep(1)

    except KeyboardInterrupt:
        print("程序停止")
    finally:
        stop()          # 确保停止所有电机
        for p in pwm.values():
            p.stop()
        GPIO.cleanup()

if __name__ == "__main__":
    main()