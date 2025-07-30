import os
import subprocess
import time
import json

# หาตำแหน่งโฟลเดอร์ของสคริปต์หลัก
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ระบุพาธของ ADB (อ้างอิงตำแหน่งโฟลเดอร์ adb)
ADB_PATH = os.path.join(BASE_DIR, "adb", "platform-tools")
os.environ["PATH"] = f"{ADB_PATH};{os.environ['PATH']}"

# โหลดค่า config
CONFIG_PATH = os.path.join(BASE_DIR, 'config.json')
with open(CONFIG_PATH, 'r') as f:
    config = json.load(f)

MUMU_PATH = config['mumu_path']
PLACE_ID = config['place_id']
CHECK_INTERVAL = config['check_interval']

def is_process_running(process_name):
    """ตรวจสอบว่ามีโปรเซสทำงานอยู่หรือไม่"""
    try:
        result = subprocess.run(['tasklist'], stdout=subprocess.PIPE, text=True)
        return process_name.lower() in result.stdout.lower()
    except Exception as e:
        print(f"Error checking process: {e}")
        return False

def run_mumu():
    """เปิด MuMu Player"""
    print("กำลังเปิด MuMu Player...")
    subprocess.Popen([MUMU_PATH], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(10)  # รอให้ MuMu เปิดตัว

def adb_connect():
    """เชื่อมต่อ ADB กับ MuMu"""
    adb_path = os.path.join(ADB_PATH, "adb.exe")  # ระบุ path เต็มของ adb.exe
    if not os.path.exists(adb_path):
        print(f"Error: ADB not found at {adb_path}. Please ensure 'adb.exe' exists.")
        return

    print("กำลังเชื่อมต่อกับ MuMu...")
    try:
        result = subprocess.run([adb_path, 'connect', '127.0.0.1:7555'], stdout=subprocess.PIPE, text=True)
        if "connected" in result.stdout or "already connected" in result.stdout:
            print("เชื่อมต่อสำเร็จ")
        else:
            print("ไม่สามารถเชื่อมต่อ ADB ได้")
    except subprocess.CalledProcessError as e:
        print(f"Error connecting ADB: {e}")

def is_package_running(package_name):
    """ตรวจสอบว่าแพ็กเกจ (เช่น Roblox) ทำงานอยู่หรือไม่"""
    adb_path = os.path.join(ADB_PATH, "adb.exe")
    try:
        # ปรับปรุงการตรวจสอบด้วยการใช้คำสั่ง 'dumpsys activity activities'
        result = subprocess.run([adb_path, 'shell', 'dumpsys', 'activity', 'activities'], stdout=subprocess.PIPE, text=True)
        return package_name in result.stdout
    except Exception as e:
        print(f"Error checking package: {e}")
        return False

def open_roblox(place_id):
    """เปิด Roblox และเข้าเกมตาม place_id"""
    adb_path = os.path.join(ADB_PATH, "adb.exe")
    print("กำลังเปิด Roblox...")
    time.sleep(3)
    try:
        # เพิ่มการดีบักพิมพ์คำสั่งที่ใช้จริง
        adb_command = [
            adb_path, 'shell', 'am', 'start',
            '-n', 'com.roblox.client/.ActivityProtocolLaunch',
            '-d', f'roblox://placeID={place_id}'
        ]
        subprocess.run(adb_command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("Roblox กำลังทำงาน")
    except subprocess.CalledProcessError as e:
        print(f"Error opening Roblox: {e}")

def main():
    try:
        while True:
            os.system('cls')  # ล้างหน้าจอ (Windows)
            print("--- ระบบกำลังทำงาน ---")
            print("กด Ctrl+C เพื่อหยุดโปรแกรม")
            
            # ตรวจสอบว่า MuMu ทำงานหรือไม่
            if not is_process_running("MuMuPlayer"):
                print("MuMu Player ไม่ได้ทำงานอยู่")
                run_mumu()
            else:
                print("MuMu Player ทำงานอยู่แล้ว")
            
            # เชื่อมต่อ ADB
            adb_connect()

            # ตรวจสอบว่า Roblox กำลังทำงานหรือไม่
            if not is_package_running("com.roblox.client"):
                print("Roblox ไม่ได้ทำงานอยู่")
                open_roblox(PLACE_ID)
            else:
                print("Roblox กำลังทำงานอยู่แล้ว")

            print(f"\nรอ {CHECK_INTERVAL} วินาทีเพื่อตรวจสอบอีกครั้ง...")
            time.sleep(CHECK_INTERVAL)
    except KeyboardInterrupt:
        os.system('cls')  # ล้างหน้าจอ
        print("--- หยุดการทำงานแล้ว ---\n")
        return  # กลับไปยังเมนูหลัก

if __name__ == "__main__":
    while True:
        print("\nMade by x_Cusive ตึงมาก❤️")
        print("\n--- เมนูหลัก ---")
        print("1. เริ่มทำงาน")
        print("2. ปิดโปรแกรม")
        choice = input("กรุณาเลือก (1 หรือ 2): ")

        if choice == '1':
            print("เริ่มทำงาน...")
            main()
        elif choice == '2':
            print("ปิดโปรแกรม...")
            break
        else:
            print("ตัวเลือกไม่ถูกต้อง กรุณาเลือกใหม่")
