import serial
import time
import RPi.GPIO as GPIO

# 初始化串口（Raspberry Pi的默认串口为/dev/ttyS0，波特率115200）
serial_port = serial.Serial('/dev/ttyS0', 115200, timeout=1)

# 设置GPIO模式为BCM编号
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)  # 禁用GPIO警告

# 定义GPIO引脚（对应电机控制）
pins = {
    'out1_positive': 17,  # GPIO17 - 电机1正转
    'out1_negative': 18,  # GPIO18 - 电机1反转
    'out2_positive': 27,  # GPIO27 - 电机2正转
    'out2_negative': 22,  # GPIO22 - 电机2反转
    'out3_positive': 23,  # GPIO23 - 电机3正转
    'out3_negative': 24   # GPIO24 - 电机3反转
}

# 设置GPIO为输出并初始化PWM（频率100Hz）
pwm = {}
for name, pin in pins.items():
    GPIO.setup(pin, GPIO.OUT)
    pwm[name] = GPIO.PWM(pin, 100)  # 100Hz PWM频率
    pwm[name].start(0)              # 初始占空比为0

# 模拟IBus通道读取（需要根据实际IBus协议实现）
def read_channel(channel):
    # 占位函数：假设返回1000-2000范围的值
    # 实际需要从serial_port读取IBus数据并解析
    # 这里仅返回模拟值，需替换为真实逻辑
    serial_port.write(f"read_ch{channel}\n".encode())  # 示例命令
    time.sleep(0.01)  # 等待响应
    response = serial_port.readline().decode().strip()
    try:
        return int(response)  # 假设返回值为数值
    except ValueError:
        return 1500  # 默认中间值

# 阈值处理函数
def threshold_stick(value):
    # 将1000-2000范围映射到-255到255
    value = max(1000, min(2000, value))  # 限制输入范围
    return (value - 1500) / 500 * 255   # 标准化输出

# 滤波函数（指数平滑滤波）
def filter(new_value, old_value, strength):
    return (new_value * (100 - strength) + old_value * strength) / 100

# 主循环
def main():
    drive1_filtered = 0
    drive2_filtered = 0
    drive3_filtered = 0
    previous_time = time.time() * 1000  # 毫秒

    try:
        while True:
            current_time = time.time() * 1000
            if current_time - previous_time >= 10:  # 每10毫秒执行一次
                previous_time = current_time

                # 读取IBus通道数据
                ch2 = read_channel(1)  # 通道1
                ch4 = read_channel(3)  # 通道3
                ch5 = read_channel(4)  # 通道4

                # 处理信号
                drive1 = threshold_stick(ch4)
                drive2 = threshold_stick(ch2)
                drive3 = threshold_stick(ch5)

                # 应用滤波
                drive1_filtered = filter(drive1, drive1_filtered, 30)
                drive2_filtered = filter(drive2, drive2_filtered, 30)
                drive3_filtered = filter(drive3, drive3_filtered, 30)

                # 信号混合
                out1 = drive1_filtered + (drive2_filtered * 0.66) - drive3_filtered
                out2 = drive1_filtered - (drive2_filtered * 0.66) + drive3_filtered
                out3 = drive2_filtered + drive3_filtered

                # 限制输出范围
                out1 = max(-255, min(255, out1))
                out2 = max(-255, min(255, out2))
                out3 = max(-255, min(255, out3))

                # 控制电机
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

                # 可选：调试输出
                # print(f"out1: {out1:.1f}, out2: {out2:.1f}, out3: {out3:.1f}")

    except KeyboardInterrupt:
        print("程序已终止")
    finally:
        # 清理GPIO资源
        for p in pwm.values():
            p.stop()
        GPIO.cleanup()
        serial_port.close()

if __name__ == "__main__":
    main()