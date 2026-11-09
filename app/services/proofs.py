from __future__ import annotations
import base64
import binascii
import json
from pathlib import Path
from datetime import datetime
from app.db import DATA_DIR, connection, event

MAX_IMAGE_BYTES = 10 * 1024 * 1024

def submit_proof(topic_id: str, proof_text: str | None = None, proof_image_data: str | None = None, proof_pages_data: str | None = None) -> dict:
    if proof_pages_data:
        try:
            pages = json.loads(proof_pages_data)
        except json.JSONDecodeError as exc:
            raise ValueError("증명 페이지 데이터를 읽을 수 없습니다.") from exc
        if not isinstance(pages, list) or not pages or len(pages) > 20:
            raise ValueError("증명 페이지는 1~20장이어야 합니다.")
    elif proof_image_data:
        pages = [proof_image_data]
    else:
        raise ValueError("증명 페이지를 하나 이상 작성해야 합니다.")
    image_dir = DATA_DIR / "proofs"
    image_dir.mkdir(parents=True, exist_ok=True)
    image_paths = []
    for page_number, page_data in enumerate(pages, start=1):
        if not isinstance(page_data, str) or not page_data.startswith("data:image/png;base64,"):
            raise ValueError("증명 페이지는 PNG 캔버스 데이터만 허용됩니다.")
        try:
            image = base64.b64decode(page_data.split(",", 1)[1], validate=True)
        except (ValueError, binascii.Error) as exc:
            raise ValueError("손글씨 이미지 데이터를 읽을 수 없습니다.") from exc
        if len(image) > MAX_IMAGE_BYTES:
            raise ValueError("손글씨 이미지가 너무 큽니다.")
        image_path = image_dir / f"{topic_id}-{datetime.now().strftime('%Y%m%d%H%M%S%f')}-p{page_number}.png"
        image_path.write_bytes(image)
        image_paths.append(image_path)
    submitted_at = datetime.now().astimezone().isoformat(timespec="seconds")
    with connection() as conn:
        if conn.execute("SELECT 1 FROM topics WHERE id=?", (topic_id,)).fetchone() is None:
            raise ValueError("존재하지 않는 명제/정리입니다.")
        cur = conn.execute("INSERT INTO proofs(topic_id,proof_text,image_path,submitted_at,verification_status) VALUES(?,?,?,?,?)", (topic_id, None, str(image_paths[0]), submitted_at, "PENDING_REVIEW"))
        proof_id = cur.lastrowid
        conn.executemany("INSERT INTO proof_pages(proof_id,page_number,image_path) VALUES(?,?,?)", [(proof_id, index, str(path)) for index, path in enumerate(image_paths, start=1)])
    result = {"id": proof_id, "topic_id": topic_id, "page_count": len(image_paths), "verification_status": "PENDING_REVIEW", "submitted_at": submitted_at}
    event("PROOF_SUBMITTED", str(proof_id), result)
    return result
