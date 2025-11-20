import os
import time
import json
import argparse
from dotenv import load_dotenv
from google import genai

# โหลดตัวแปรสภาพแวดล้อม
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    raise ValueError("❌ ไม่พบ GOOGLE_API_KEY ในไฟล์ .env")

client = genai.Client(api_key=API_KEY)

# ชื่อไฟล์มาตรฐานสำหรับเก็บ Job ID ล่าสุด (เชื่อมโยงกับ main.py)
DEFAULT_JOB_FILE = "latest_job_id.txt"

def get_job_name(args):
    """
    The Selector Logic:
    ลำดับความสำคัญ: 1. Argument -> 2. File -> 3. Input
    """
    
    # 1. รับผ่าน Argument (--job)
    if args.job:
        return args.job.strip()
    
    # 2. รับผ่านไฟล์บันทึก (latest_job_id.txt)
    job_file = args.job_file
    if os.path.exists(job_file):
        with open(job_file, "r", encoding="utf-8") as f:
            saved_id = f.read().strip()
        if saved_id:
            print(f"📂 พบ Job ID จากไฟล์ '{job_file}': {saved_id}")
            # ถ้ามี flag --yes ให้ข้ามการถาม
            if args.yes or input(f"   ต้องการตรวจสอบงานนี้หรือไม่? (Y/n): ").lower() in ('', 'y'):
                return saved_id

    # 3. ถามผู้ใช้โดยตรง (Interactive Mode)
    return input("✍️  กรุณากรอก Job Name (เช่น batches/xxxx): ").strip()

def get_job_status(job_name):
    """ตรวจสอบสถานะปัจจุบันจาก Google Cloud"""
    try:
        job = client.batches.get(name=job_name)
        state = job.state.name
        return job, state
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการดึงข้อมูลงาน: {e}")
        return None, "UNKNOWN"

def download_results(job, output_filename="batch_results.jsonl"):
    """ดาวน์โหลดผลลัพธ์และบันทึกไฟล์ (The Materialization)"""
    try:
        result_file_name = None
        # พยายามหาชื่อไฟล์ผลลัพธ์ (รองรับความเปลี่ยนแปลงของ SDK)
        if hasattr(job, 'output_files') and job.output_files:
             result_file_name = job.output_files[0].name
        elif hasattr(job, 'dest') and hasattr(job.dest, 'file_name'):
             result_file_name = job.dest.file_name

        if not result_file_name:
            print("⚠️ ไม่พบชื่อไฟล์ผลลัพธ์ในข้อมูล Job")
            return None

        print(f"⬇️  กำลังดาวน์โหลด: {result_file_name}...")
        content = client.files.download(file=result_file_name)
        
        with open(output_filename, "wb") as f:
            f.write(content)
            
        print(f"✅ บันทึกผลลัพธ์เรียบร้อยที่: {output_filename}")
        return content
    except Exception as e:
        print(f"❌ ดาวน์โหลดล้มเหลว: {e}")
        return None

def preview_content(content_bytes, lines=2):
    """แสดงตัวอย่างข้อมูล (The Glimpse)"""
    if not content_bytes: return
    print("\n--- 👁️ ตัวอย่างผลลัพธ์ (Preview) ---")
    try:
        decoded = content_bytes.decode('utf-8')
        for i, line in enumerate(decoded.splitlines()[:lines]):
            print(f"[{i+1}] {json.dumps(json.loads(line), indent=2, ensure_ascii=False)}")
    except Exception:
        print("   (ไม่สามารถแสดงตัวอย่าง JSON ได้)")

def main():
    parser = argparse.ArgumentParser(description="AGIOpg: The Retrieval Ritual (check_job)")
    parser.add_argument("--job", help="ระบุ Job ID โดยตรง")
    parser.add_argument("--job-file", default=DEFAULT_JOB_FILE, help=f"ไฟล์เก็บ ID (Default: {DEFAULT_JOB_FILE})")
    parser.add_argument("--wait", action="store_true", help="รอจนกว่างานจะเสร็จ (Polling Mode)")
    parser.add_argument("--download", action="store_true", default=True, help="ดาวน์โหลดผลลัพธ์อัตโนมัติเมื่อเสร็จ")
    parser.add_argument("--yes", "-y", action="store_true", help="ตอบตกลงทุกคำถามอัตโนมัติ")
    args = parser.parse_args()

    print("--- 🔮 เริ่มต้นพิธีกรรมกู้คืนข้อมูล (Retrieval Ritual) ---")
    
    job_name = get_job_name(args)
    if not job_name:
        print("❌ ไม่ระบุ Job Name จบการทำงาน")
        return

    print(f"📡 เชื่อมต่อกับ: {job_name}")

    # Loop การเฝ้ารอ (The Vigil)
    while True:
        job, state = get_job_status(job_name)
        print(f"   -> สถานะ: {state}")

        if state == "JOB_STATE_SUCCEEDED":
            if args.download:
                content = download_results(job)
                preview_content(content)
            
                # หมายเหตุ: หากต้องการลบไฟล์ ID เมื่อเสร็จงาน ให้เปิดคอมเมนต์ด้านล่าง
                if os.path.exists(args.job_file):
                    # os.remove(args.job_file) 
                    pass
            break
        
        elif state in ("JOB_STATE_FAILED", "JOB_STATE_CANCELLED"):
            print(f"❌ งานจบลงด้วยสถานะ: {state}")
            if hasattr(job, 'error') and job.error:
                print(f"   สาเหตุ: {job.error}")
            break
            
        else:
            # กรณีงานยังไม่เสร็จ (CREATING, ACTIVE)
            if not args.wait:
                print("⏳ งานยังไม่เสร็จ (ใช้ --wait หากต้องการรอ)")
                break
            print("   ...รอ 30 วินาที...")
            time.sleep(30)

if __name__ == "__main__":
    main()

                break
            print("   ...รอ 30 วินาที...")
            time.sleep(30)

if __name__ == "__main__":
    main()

