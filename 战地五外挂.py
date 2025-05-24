import pyautogui
import time
from pynput import keyboard, mouse
from threading import Thread, Lock

# 全局控制变量
clicking = False          # 连点状态
long_press_threshold = 0.3  # 长按判定时间（秒）
physical_mouse = mouse.Controller()  # 物理鼠标状态检测
lock = Lock()            # 线程锁

def on_key_press(key):
    global clicking
    if key == keyboard.Key.f2:  # 修改为F2键
        with lock:
            clicking = not clicking
            status = "启动" if clicking else "停止"
            print(f"键盘模式：连点器已{status}")

def on_mouse_click(btn, pressed):
    if btn != mouse.Button.left:
        return

    if pressed:
        # 记录按下时间并启动长按检测线程
        Thread(target=check_long_press, daemon=True).start()
    else:
        # 松开时立即停止连点
        with lock:
            global clicking
            clicking = False

def check_long_press():
    start_time = time.time()
    while physical_mouse.pressed(mouse.Button.left):
        if time.time() - start_time > long_press_threshold:
            with lock:
                global clicking
                if not clicking:
                    clicking = True
                    print("鼠标模式：长按左键触发连点")
            break
        time.sleep(0.000000001)

def clicker():
    while True:
        with lock:
            if clicking:
                # 执行点击但忽略监听事件（速度提升2倍）
                pyautogui.mouseDown()
                pyautogui.mouseUp()
                time.sleep(0.0000000000001)  # 原0.1秒改为0.05秒
        time.sleep(0.001)

if __name__ == "__main__":
    print("连点器优化版（解决左键冲突）")
    print("- 短按左键: 正常单击")
    print("- 长按左键(0.3秒): 触发连点")
    print("- 按 F2 键: 切换持续连点模式")

    # 启动监听器
    mouse_listener = mouse.Listener(on_click=on_mouse_click)
    keyboard_listener = keyboard.Listener(on_press=on_key_press)
    mouse_listener.daemon = True
    keyboard_listener.daemon = True
    mouse_listener.start()
    keyboard_listener.start()

    # 启动点击线程
    Thread(target=clicker, daemon=True).start()

    # 主线程保活
    try:
        while True: time.sleep(1)
    except KeyboardInterrupt:
        print("\n程序已安全退出")