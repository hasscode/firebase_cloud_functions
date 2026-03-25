from flask import jsonify
from google.cloud import firestore

def set_student_running_status(req, db: firestore.Client):
    try:
        data = req.get_json(silent=True) or {}

        student_uid = data.get("studentUid")

        if not student_uid:
            return jsonify({"error": "studentUid is required"}), 400

        running_status = data.get("runningStatus") or data

        doc_ref = db.collection("student_running_status").document(student_uid)

        doc_ref.set({
            **running_status,
            "studentUid": student_uid,
            "updatedAt": firestore.SERVER_TIMESTAMP
        })

        return jsonify({
            "success": True,
            "message": "Running status saved successfully",
            "studentUid": student_uid
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500