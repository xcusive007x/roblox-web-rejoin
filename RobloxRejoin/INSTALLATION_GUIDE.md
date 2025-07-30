# คู่มือการติดตั้งและใช้งาน Roblox Rejoiner Bot

## ข้อกำหนดระบบ
- Windows 10/11 (64-bit)
- MuMu Player หรือ Android Emulator อื่นๆ
- Android SDK Platform Tools (ADB)
- Python 3.11 หรือสูงกว่า

## การติดตั้ง

### 1. ติดตั้ง MuMu Player
1. ดาวน์โหลด MuMu Player จาก: https://www.mumuplayer.com/
2. ติดตั้งตามขั้นตอนปกติ
3. เปิด MuMu Player และตั้งค่าเบื้องต้น

### 2. เปิดใช้งาน Developer Options ใน MuMu
1. เปิด MuMu Player
2. ไปที่ Settings > About Phone
3. แตะ "Build Number" 7 ครั้งเพื่อเปิดใช้งาน Developer Options
4. กลับไปที่ Settings > Developer Options
5. เปิดใช้งาน "USB Debugging"
6. เปิดใช้งาน "Stay Awake"

### 3. ติดตั้ง Android SDK Platform Tools
1. ดาวน์โหลด Platform Tools จาก: https://developer.android.com/studio/releases/platform-tools
2. แตกไฟล์ไปที่โฟลเดอร์ที่ต้องการ (เช่น `C:\platform-tools`)
3. เพิ่ม path ของ platform-tools ลงใน Environment Variables ของ Windows

### 4. ติดตั้ง Roblox ใน MuMu Player
1. เปิด Google Play Store ใน MuMu Player
2. ดาวน์โหลดและติดตั้ง Roblox
3. เข้าสู่ระบบ Roblox ด้วยบัญชีของคุณ

## การตั้งค่าโปรแกรม

### ตั้งค่าใน Configuration Panel:

1. **Place ID**: รหัสเกม Roblox ที่ต้องการให้ Bot เข้าเล่น
2. **MuMu Player Path**: path ไฟล์ MuMuPlayer.exe (ปกติจะอยู่ที่ `C:\Program Files\Netease\MuMuPlayerGlobal-12.0\shell\MuMuPlayer.exe`)
3. **Check Interval**: ระยะเวลาในการตรวจสอบสถานะ (แนะนำ 5-10 วินาที)
4. **VIP Server**: หากต้องการเข้า VIP Server ให้เปิดใช้งานและใส่ URL
5. **Cookie**: Roblox Cookie สำหรับการเข้าสู่ระบบ (ไม่บังคับ)

## การใช้งาน

### เริ่มต้นใช้งาน:
1. เปิดเว็บแอปพลิเคชัน
2. ตรวจสอบ Configuration ให้ถูกต้อง
3. กด "Test MuMu Connection" เพื่อทดสอบการเชื่อมต่อ
4. กด "Test ADB Connection" เพื่อทดสอบ ADB
5. กด "Start Bot" เพื่อเริ่มการทำงาน

### การตรวจสอบสถานะ:
- **Bot Status**: สถานะการทำงานของ Bot
- **MuMu Player**: สถานะ MuMu Player
- **Roblox**: สถานะแอป Roblox
- **ADB**: สถานะการเชื่อมต่อ ADB

## การแก้ไขปัญหา

### ADB ไม่เชื่อมต่อ:
1. ตรวจสอบว่า MuMu Player เปิดอยู่
2. ตรวจสอบว่าเปิดใช้งาน USB Debugging แล้ว
3. รีสตาร์ท MuMu Player
4. ลองรันคำสั่ง `adb connect 127.0.0.1:7555` ใน Command Prompt

### MuMu Player ไม่เจอ:
1. ตรวจสอบ path ใน Configuration
2. ตรวจสอบว่าติดตั้ง MuMu Player แล้ว
3. อาจจะต้องเปลี่ยน path ให้ตรงกับเวอร์ชันที่ติดตั้ง

### Roblox ไม่เปิด:
1. ตรวจสอบว่า Roblox ติดตั้งใน MuMu Player แล้ว
2. ตรวจสอบ Place ID ให้ถูกต้อง
3. ตรวจสอบการเชื่อมต่ออินเทอร์เน็ต

## หมายเหตุความปลอดภัย
- ใช้งานด้วยความระมัดระวัง
- อย่าใช้กับบัญชีหลักของคุณ
- ปฏิบัติตาม Terms of Service ของ Roblox
- โปรแกรมนี้เป็นเครื่องมือช่วยเหลือเท่านั้น

## การสนับสนุน
หากมีปัญหาในการใช้งาน กรุณาตรวจสอบ System Logs ในเว็บแอปพลิเคชันเพื่อดูรายละเอียดข้อผิดพลาด