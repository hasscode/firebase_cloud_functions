from flask import jsonify
from google.cloud import firestore
from datetime import datetime, timezone

# 1. الحقول الأربعة المسموح للـ Agent بتعديلها فقط
ALLOWED_TASK_FIELDS = {
    "taskStatus",
    "engagementResults",
    "recentPedagogicalContext",
    "taskCurrentRunningGuidance"
}

def update_task(req, db: firestore.Client):
    try:
        data = req.get_json(silent=True) or {}
        
        
        scheduled_task_id = data.get("scheduledTaskId")
        if not scheduled_task_id:
            return jsonify({"error": "scheduledTaskId is required"}), 400

      
        clean_update = {}
        for key, value in data.items():
            if key in ALLOWED_TASK_FIELDS:
              
                if key == "taskStatus":
                    allowed_statuses = {"notStarted", "inProgress", "completed", "cancelled"}
                    if value not in allowed_statuses:
                        continue
                
                clean_update[key] = value

        if not clean_update:
            return jsonify({"error": "No valid fields provided for update (Allowed: taskStatus, engagementResults, recentPedagogicalContext, taskCurrentRunningGuidance)"}), 400

       
        doc_ref = db.collection("tasks").document(scheduled_task_id)
        
     
        clean_update["updatedAt"] = firestore.SERVER_TIMESTAMP
        clean_update["engagementLastUpdatedAt"] = datetime.now(timezone.utc).isoformat()

       
        doc_ref.update(clean_update)

        return jsonify({
            "success": True,
            "updatedTaskId": scheduled_task_id,
            "fields": list(clean_update.keys())
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500