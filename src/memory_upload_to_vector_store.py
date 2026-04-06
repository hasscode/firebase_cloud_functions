import os
import uuid
import requests
from flask import jsonify, request

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
VECTOR_STORE_ID = os.getenv("VECTOR_STORE_ID")

OPENAI_HEADERS = {
    "Authorization": f"Bearer {OPENAI_API_KEY}",
    "OpenAI-Beta": "assistants=v2"  
}

def upload_to_vector_store(request):
    try:
        data = request.get_json()
        text = data.get("text", "")

        if not text:
            return jsonify({"error": "No text provided"}), 400

        # 1️⃣ Create temporary file
        file_content = text.encode("utf-8")
        filename = f"memory_{uuid.uuid4()}.txt"
        files = {
            "file": (filename, file_content),
            "purpose": (None, "assistants")
        }

        # 2️⃣ Upload file to OpenAI
        upload_res = requests.post(
            "https://api.openai.com/v1/files",
            headers=OPENAI_HEADERS,
            files=files
        )

        if upload_res.status_code != 200:
            return jsonify({"error": upload_res.text}), 500

        file_id = upload_res.json()["id"]

        # 3️⃣ Attach file to vector store
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
            return jsonify({"error": attach_res.text}), 500

        return jsonify({
            "status": "success",
            "file_id": file_id
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500