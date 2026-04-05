from flask import jsonify
from google.cloud import firestore

def update_student_running_status(req, db: firestore.Client):
    try:
        data = req.get_json(silent=True) or {}
        student_uid = data.get("studentUid")

        if not student_uid:
            return jsonify({"error": "studentUid is required"}), 400

        # 🔒 1. القائمة المحدثة بالكامل بناءً على Schema 1.2
        ALLOWED_FIELDS = {
            "schemaVersion",
            "statusStartAt",
            "statusEndAt",
            "currentOverallStatus",
            "currentMood",
            "availableTimeMinutes",
            "engagementStatus",
            "goalByStudent",
            "goalByAI",
            "activityNarrative",
            "barriersAndRecoveryNarrative",
            "interventionsNarrative",
            "periodSummaryNarrative",
            "tasksStarted",      # بيحدثها الـ App
            "tasksCompleted",    # بيحدثها الـ Agent
            "interventions"      # بيحدثها الـ Agent
        }

    
        updates = data.get("runningStatus") if "runningStatus" in data else data

        # فلترة الداتا للحفاظ على الـ Schema
        filtered_updates = {
            key: value for key, value in updates.items() 
            if key in ALLOWED_FIELDS
        }

        if not filtered_updates:
            return jsonify({
                "error": "No valid or allowed update fields provided based on Schema 1.2"
            }), 400

        doc_ref = db.collection("student_running_status").document(student_uid)

        from datetime import datetime, timezone
        
        doc_ref.update({
            **filtered_updates,
            "lastUpdatedAt": datetime.now(timezone.utc).isoformat()
        })

        return jsonify({
            "success": True,
            "message": "Status updated successfully with Schema 1.2",
            "studentUid": student_uid,
            "updatedFields": list(filtered_updates.keys())
        })

    except Exception as e:
        if "NOT_FOUND" in str(e):
             return jsonify({"error": "Student document not found."}), 404
        return jsonify({"error": str(e)}), 500