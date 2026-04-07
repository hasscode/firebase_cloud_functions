import os
import uuid
import requests
from flask import jsonify

VECTOR_STORE_ID = "vs_69d2d2a37fa081918c35da8785601d94"

def upload_to_vector_store(request):
    try:
        
        OPENAI_API_KEY = os.getenv("MEMORY_CONVERSATION_OPENAI_API_KEY")

        if not OPENAI_API_KEY:
            return jsonify({"error": "API key not loaded"}), 500

        OPENAI_HEADERS = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "OpenAI-Beta": "assistants=v2"
        }

        # ✅ 2. قراءة البيانات
        data = request.get_json(silent=True) or {}
        text = data.get("text", "")

        if not text:
            return jsonify({"error": "No text provided"}), 400

        # ✅ 3. إنشاء file مؤقت
        file_content = text.encode("utf-8")
        filename = f"memory_{uuid.uuid4()}.txt"

        files = {
            "file": (filename, file_content),
            "purpose": (None, "assistants")
        }

        # ✅ 4. رفع الملف
        upload_res = requests.post(
            "https://api.openai.com/v1/files",
            headers=OPENAI_HEADERS,
            files=files
        )

        if upload_res.status_code != 200:
            return jsonify({
                "step": "upload_file_failed",
                "error": upload_res.text
            }), 500

        file_id = upload_res.json().get("id")

        # ✅ 5. ربط الملف بالـ vector store
        attach_res = requests.post(
            f"https://api.openai.com/v1/vector_stores/{VECTOR_STORE_ID}/files",
            headers={
                **OPENAI_HEADERS,
                "Content-Type": "application/json"
            },
            json={
                "file_id": file_id
            }
        )

        if attach_res.status_code != 200:
            return jsonify({
                "step": "attach_file_failed",
                "error": attach_res.text
            }), 500

        # ✅ 6. نجاح
        return jsonify({
            "status": "success",
            "file_id": file_id
        }), 200

    except Exception as e:
        return jsonify({
            "step": "exception",
            "error": str(e)
        }), 500