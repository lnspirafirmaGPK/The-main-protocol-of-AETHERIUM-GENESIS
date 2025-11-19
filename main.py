print(f"🚀 สร้างงานสำเร็จ ID: {batch_job.name}")

job_file = "latest_job_id.txt"
with open(job_file, "w", encoding="utf-8") as f:
    f.write(batch_job.name.strip())
    f.flush()
    os.fsync(f.fileno())

print(f"💾 บันทึก Job ID ไว้ที่ '{job_file}' แล้ว (ใช้ check_job.py เพื่อติดตาม)")

