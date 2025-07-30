import os
import subprocess
import time
import json
import threading
from screen_detector import ScreenDetector

class RobloxRejoinerBot:
    def __init__(self, config, log_callback=None):
        """Initialize the Roblox Rejoiner Bot"""
        self.config = config
        self.log_callback = log_callback or print
        self.running = False
        self.stop_event = threading.Event()
        
        # Setup ADB path
        self.BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        self.ADB_PATH = os.path.join(self.BASE_DIR, "adb", "platform-tools")
        
        # Add ADB to PATH if exists
        if os.path.exists(self.ADB_PATH):
            os.environ["PATH"] = f"{self.ADB_PATH};{os.environ['PATH']}"
        
        self.MUMU_PATH = self.config['mumu_path']
        self.PLACE_ID = self.config['place_id']
        self.CHECK_INTERVAL = self.config['check_interval']
        self.USE_VIP_SERVER = self.config.get('use_vip_server', False)
        self.VIP_SERVER_CODE = self.config.get('vip_server_code', '')
        
        # Initialize screen detector
        self.screen_detector = ScreenDetector(self.get_adb_path(), self.log)
        self.auto_actions = self.config.get('auto_actions', {})
        self.enable_screen_detection = self.config.get('enable_screen_detection', False)

    def log(self, message):
        """Log a message using the callback function"""
        if self.log_callback:
            self.log_callback(message)

    def is_process_running(self, process_name):
        """Check if a process is running"""
        try:
            if os.name == 'nt':  # Windows
                result = subprocess.run(['tasklist'], stdout=subprocess.PIPE, text=True, timeout=10)
                return process_name.lower() in result.stdout.lower()
            else:  # Linux/Mac
                # In demo environment, simulate MuMu check
                if process_name == "MuMuPlayer":
                    self.log("Demo mode: MuMu Player check simulated")
                    return False  # Simulate MuMu not running
                result = subprocess.run(['pgrep', '-f', process_name], stdout=subprocess.PIPE, text=True, timeout=10)
                return bool(result.stdout.strip())
        except Exception as e:
            self.log(f"Error checking process {process_name}: {e}")
            return False

    def run_mumu(self):
        """Start MuMu Player"""
        self.log("Attempting to start MuMu Player...")
        
        # Check if we're in Windows environment
        if os.name != 'nt':
            self.log("คำแนะนำ: โปรแกรมนี้ถูกออกแบบมาสำหรับ Windows")
            self.log("หากต้องการใช้งานจริง กรุณา:")
            self.log("1. ติดตั้ง MuMu Player ในเครื่อง Windows ของคุณ")
            self.log("2. ตั้งค่า path ของ MuMu Player ให้ถูกต้อง")
            self.log("3. เปิดใช้งาน Developer Options และ USB Debugging ใน MuMu")
            return False
        
        try:
            if not os.path.exists(self.MUMU_PATH):
                self.log(f"ไม่พบ MuMu Player ที่: {self.MUMU_PATH}")
                self.log("กรุณาตรวจสอบ path ในส่วน Configuration")
                self.log("หรือติดตั้ง MuMu Player จาก: https://www.mumuplayer.com/")
                return False
            
            subprocess.Popen([self.MUMU_PATH], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            self.log("กำลังเปิด MuMu Player...")
            time.sleep(15)  # Wait for MuMu to fully start
            return True
        except Exception as e:
            self.log(f"เกิดข้อผิดพลาดในการเปิด MuMu Player: {e}")
            return False

    def get_adb_path(self):
        """Get the full path to adb.exe"""
        if os.name == 'nt':  # Windows
            adb_path = os.path.join(self.ADB_PATH, "adb.exe")
            if os.path.exists(adb_path):
                return adb_path
            # Try system PATH
            return "adb"
        else:
            adb_path = "adb"  # Assume it's in PATH on Linux/Mac
        
        return adb_path

    def adb_connect(self):
        """Connect ADB to MuMu"""
        adb_path = self.get_adb_path()
        
        # Check if ADB exists
        try:
            subprocess.run([adb_path, '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=5)
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError) as e:
            self.log(f"ADB ไม่พร้อมใช้งาน: {e}")
            self.log("หากใช้งานจริงในเครื่อง Windows:")
            self.log("1. ติดตั้ง Android SDK Platform Tools")
            self.log("2. เปิด MuMu Player และเปิดใช้งาน ADB debugging")
            self.log("3. เชื่อมต่อผ่าน port 7555")
            return False

        self.log("กำลังเชื่อมต่อ ADB กับ MuMu...")
        try:
            # Try to connect to MuMu Player (default port 7555)
            result = subprocess.run([adb_path, 'connect', '127.0.0.1:7555'], 
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=30)
            
            if "connected" in result.stdout or "already connected" in result.stdout:
                self.log("เชื่อมต่อ ADB สำเร็จ")
                return True
            else:
                self.log(f"การเชื่อมต่อ ADB ล้มเหลว: {result.stdout} {result.stderr}")
                self.log("ตรวจสอบว่า MuMu Player เปิดอยู่และเปิดใช้งาน ADB debugging")
                return False
        except subprocess.TimeoutExpired:
            self.log("การเชื่อมต่อ ADB หมดเวลา")
            return False
        except Exception as e:
            self.log(f"เกิดข้อผิดพลาดในการเชื่อมต่อ ADB: {e}")
            return False

    def check_adb_connection(self):
        """Check if ADB is connected"""
        adb_path = self.get_adb_path()
        try:
            # First check if ADB is available
            subprocess.run([adb_path, '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=5)
            
            # Check devices
            result = subprocess.run([adb_path, 'devices'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=10)
            return "127.0.0.1:7555" in result.stdout and "device" in result.stdout
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError) as e:
            self.log(f"ADB not available: {e}")
            return False
        except Exception as e:
            self.log(f"Error checking ADB connection: {e}")
            return False

    def is_package_running(self, package_name):
        """Check if a package (like Roblox) is running"""
        adb_path = self.get_adb_path()
        try:
            # First check if ADB is available
            subprocess.run([adb_path, '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=5)
            
            # Check if the package is running using dumpsys
            result = subprocess.run([adb_path, 'shell', 'dumpsys', 'activity', 'activities'], 
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=15)
            return package_name in result.stdout
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError) as e:
            self.log(f"ADB not available: {e}")
            return False
        except Exception as e:
            self.log(f"Error checking package {package_name}: {e}")
            return False

    def open_roblox(self, place_id):
        """Open Roblox and join the specified place"""
        adb_path = self.get_adb_path()
        self.log("Opening Roblox...")
        
        try:
            # First check if ADB is available
            subprocess.run([adb_path, '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=5)
            
            # Determine the URL based on VIP server settings
            if self.USE_VIP_SERVER and self.VIP_SERVER_CODE:
                roblox_url = self.VIP_SERVER_CODE
                self.log(f"Using VIP server: {roblox_url}")
            else:
                roblox_url = f'roblox://placeID={place_id}'
                self.log(f"Using place ID: {place_id}")
            
            # Open Roblox with the specified URL
            adb_command = [
                adb_path, 'shell', 'am', 'start',
                '-n', 'com.roblox.client/.ActivityProtocolLaunch',
                '-d', roblox_url
            ]
            
            result = subprocess.run(adb_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
                                  text=True, timeout=30)
            
            if result.returncode == 0:
                self.log("Roblox opened successfully")
                return True
            else:
                self.log(f"Error opening Roblox: {result.stderr}")
                return False
                
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError) as e:
            self.log(f"ADB not available: {e}")
            return False
        except Exception as e:
            self.log(f"Error opening Roblox: {e}")
            return False

    def stop(self):
        """Stop the bot"""
        self.log("Stopping bot...")
        self.running = False
        self.stop_event.set()

    def run(self):
        """Main bot loop"""
        self.log("=== Roblox Rejoiner Bot Started ===")
        self.running = True
        self.stop_event.clear()
        
        while self.running and not self.stop_event.is_set():
            try:
                self.log("--- Checking system status ---")
                
                # Check if MuMu is running
                if not self.is_process_running("MuMuPlayer"):
                    self.log("MuMu Player is not running")
                    if not self.run_mumu():
                        self.log("Failed to start MuMu Player")
                        self.stop_event.wait(self.CHECK_INTERVAL)
                        continue
                else:
                    self.log("MuMu Player is running")
                
                # Connect ADB
                if not self.adb_connect():
                    self.log("Failed to connect ADB, retrying in next cycle")
                    self.stop_event.wait(self.CHECK_INTERVAL)
                    continue

                # Check if Roblox is running
                if not self.is_package_running("com.roblox.client"):
                    self.log("Roblox is not running")
                    if not self.open_roblox(self.PLACE_ID):
                        self.log("Failed to open Roblox")
                else:
                    self.log("Roblox is running")

                # Wait for next check
                self.log(f"Next check in {self.CHECK_INTERVAL} seconds...")
                if self.stop_event.wait(self.CHECK_INTERVAL):
                    break  # Stop event was set
                    
            except KeyboardInterrupt:
                self.log("Bot stopped by user")
                break
            except Exception as e:
                self.log(f"Unexpected error: {e}")
                self.stop_event.wait(5)  # Wait 5 seconds before retrying
        
        self.running = False
        self.log("=== Roblox Rejoiner Bot Stopped ===")
