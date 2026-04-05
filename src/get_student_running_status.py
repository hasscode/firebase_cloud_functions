from flask import jsonify
from google.cloud import firestore


def getStudentRunningStatus(req, db: firestore.Client):
    try:
        data = req.get_json(silent=True) or {}

        student_uid = data.get("studentUid")

        if not student_uid:
            return jsonify({"error": "studentUid is required"}), 400

        
        query = db.collection("student_running_status") \
                  .where("studentUid", "==", student_uid) \
                  .limit(1)

        docs = query.stream()

        status = None

        for doc in docs:
            status = doc.to_dict()
            status["id"] = doc.id
            break

        if not status:
            return jsonify({
                "success": True,
                "message": "No active running status found",
                "studentUid": student_uid,
                "runningStatus": None
            })

        return jsonify({
            "success": True,
            "studentUid": student_uid,
            "runningStatus": status
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500