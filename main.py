import os
import time
from dotenv import load_dotenv
from google import genai

# 1. โหลด Environment Variables
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY") # หรือ GEMINI_API_KEY

# 2. ฟังก์ชันสำหรับบันทึก ID (โค้ดที่คุณให้มา อยู่ในนี้)
def save_job_id(batch_job):
    output_filename = "latest_job_id.txt"
    try:
        with open(output_filename, "w", encoding="utf-8") as f:
            # ใช้ .name ตามโครงสร้าง Object ของ Google GenAI SDK
            f.write(batch_job.name.strip())
            f.flush()
            os.fsync(f.fileno())
        print(f"💾 บันทึก Job ID ไว้ที่ '{output_filename}' แล้ว")
    except Exception as e:
        print(f"❌ บันทึกไฟล์ไม่สำเร็จ: {e}")

# 3. ฟังก์ชันหลัก (Main Execution)
def main():
    if not API_KEY:
        print("❌ ไม่พบ API Key จบการทำงาน")
        return

    print("🚀 กำลังเชื่อมต่อกับ Google Gemini...")
    client = genai.Client(api_key=API_KEY)

    # --- ส่วนสร้าง Job (ตัวอย่าง) ---
    # คุณต้องใส่ Logic การสร้าง Job ของคุณตรงนี้
    # ตัวอย่างเช่น:
    try:
        # สมมติการสร้าง Job (ต้องแก้ให้ตรงกับงานจริงของคุณ)
        # training_data = ...
        # model = ...
        
        # สมมติว่าสร้างเสร็จแล้วได้ตัวแปร batch_job กลับมา
        # batch_job = client.batches.create(...) 
        
        # *เนื่องจากผมไม่มีโค้ดส่วน create ของคุณ ผมจะจำลอง Object เพื่อทดสอบ*
        class MockJob:
            def __init__(self, name): self.name = name
        
        batch_job = MockJob("batches/sample-job-id-12345") # <--- ของจริงคือค่าที่ได้จาก create()
        
        print(f"✅ สร้างงานสำเร็จ ID: {batch_job.name}")
        
        # เรียกใช้ฟังก์ชันบันทึก (ที่คุณให้มา)
        save_job_id(batch_job)

    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการสร้างงาน: {e}")

if __name__ == '__main__':
    main()
