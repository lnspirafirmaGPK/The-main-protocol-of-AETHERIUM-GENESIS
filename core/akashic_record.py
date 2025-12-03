import hashlib
import json
import time
from pydantic import BaseModel, Field
from typing import Dict, Any

# 🔒 The Immutable Envelope
class AkashicEnvelope(BaseModel):
    artifact_id: str = Field(..., description="ID ของสิ่งประดิษฐ์ เช่น res_001_genesis")
    content_hash: str = Field(..., description="SHA-256 Hash ของเนื้อหา (Digital Fingerprint)")
    timestamp: float = Field(default_factory=time.time, description="เวลาที่ทำการจารึก (Unix Timestamp)")
    payload: Dict[str, Any] = Field(..., description="ข้อมูล Manifest ทั้งหมด")
    
    class Config:
        frozen = True  # ❄️ ห้ามแก้ไขหลังจากสร้าง Instance แล้ว (Immutability)

def calculate_hash(data: dict) -> str:
    """สร้าง Digital Fingerprint จากข้อมูล JSON"""
    encoded = json.dumps(data, sort_keys=True).encode()
    return hashlib.sha256(encoded).hexdigest()

def seal_artifact(manifest_data: dict) -> AkashicEnvelope:
    """พิธีกรรมการปิดผนึก (Sealing Ritual)"""
    # 1. คำนวณ Hash ของ Manifest
    content_hash = calculate_hash(manifest_data)
    
    # 2. สร้างซองจดหมาย (Envelope)
    envelope = AkashicEnvelope(
        artifact_id=manifest_data["artifact_identity"]["resonance_id"],
        content_hash=content_hash,
        payload=manifest_data
    )
    
    return envelope
