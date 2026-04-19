from flask import jsonify
from google.cloud import firestore

def getTask(req, db: firestore.Client):
    try:
        data = req.get_json(silent=True) or {}
        scheduled_task_id = data.get("scheduledTaskId")

        if not scheduled_task_id:
            return jsonify({"error": "scheduledTaskId is required"}), 400

        task_ref = db.collection("tasks").document(scheduled_task_id)
        task_doc = task_ref.get()

        if not task_doc.exists:
            return jsonify({"error": "Task not found"}), 404

        task_data = task_doc.to_dict()

        # بنرجعها برضه جوه Array اسمه tasks عشان نلتزم بالـ Schema
        return jsonify({
            "schemaVersion": "priorityTasksFlatReadable_v1",
            "tasks": [task_data]
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500