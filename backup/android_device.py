import subprocess
import re


def run_cmd(cmd: str) -> str:
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout.strip()


def get_connected_devices():
    output = run_cmd("adb devices")
    lines = output.splitlines()[1:]  # skip header
    devices = []

    for line in lines:
        if "device" in line and "unauthorized" not in line:
            devices.append(line.split()[0])

    return devices


def get_current_focus(udid: str):
    cmd = f"adb -s {udid} shell dumpsys window | grep mCurrentFocus"
    output = run_cmd(cmd)

    # 範例格式:
    # mCurrentFocus=Window{... com.asus.asusrouter/.MainActivity}
    match = re.search(r"([a-zA-Z0-9_.]+)/([a-zA-Z0-9_.$]+)", output)
    if match:
        return match.group(1), match.group(2)

    return None, None


def main():
    devices = get_connected_devices()

    if not devices:
        print("❌ 沒有偵測到 Android 裝置")
        return

    print("🔌 已連接裝置：")
    for i, d in enumerate(devices):
        print(f"{i}: {d}")

    index = 0
    if len(devices) > 1:
        index = int(input("請選擇裝置編號: "))

    udid = devices[index]

    package, activity = get_current_focus(udid)

    print("\n==============================")
    print("📱 Appium Android 設定建議：")
    print("==============================")

    print(f'"platform_name": "Android",')
    print(f'"automation_name": "UiAutomator2",')
    print(f'"device_name": "Android Device",')
    print(f'"udid": "{udid}",')

    if package and activity:
        print(f'"app_package": "{package}",')
        print(f'"app_activity": "{activity}",')
    else:
        print("\n⚠️  無法抓到前景 App，請先打開你的 App 再執行此腳本")

    print("==============================\n")


if __name__ == "__main__":
    main()
