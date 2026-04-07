from flask import jsonify
from google.cloud import firestore
from datetime import datetime, timezone


def createTasks(req, db: firestore.Client):
    try:
        data = req.get_json(silent=True) or {}

        if not data:
            return jsonify({"error": "Missing request body"}), 400

        schema_version = data.get("schemaVersion")
        tasks = data.get("tasks")

        if schema_version != "tasksFlatReadable_v1":
            return jsonify({"error": "Invalid schemaVersion"}), 400

        if not tasks or not isinstance(tasks, list):
            return jsonify({"error": "tasks array is required"}), 400

        batch = db.batch()
        created_tasks = []

        now_iso = datetime.now(timezone.utc).isoformat()

        for task in tasks:
            scheduled_task_id = task.get("scheduledTaskId")

            if not scheduled_task_id:
                # skip invalid task
                continue

            # 🔥 نضيف timestamps لو مش موجودة
            task["createdAt"] = firestore.SERVER_TIMESTAMP
            task["updatedAt"] = firestore.SERVER_TIMESTAMP

          
            task.setdefault("taskStatus", "notStarted")
            task.setdefault("taskScorePercent", 0)
            task.setdefault("isEligibleNow", True)
            task.setdefault("isOverdue", False)
            task.setdefault("priorityScore", 0)
            task.setdefault("lastCalculatedAt", now_iso)

          
            ref = db.collection("tasks").document(scheduled_task_id)
            batch.set(ref, task, merge=True)

            created_tasks.append(scheduled_task_id)

        batch.commit()

        return jsonify({
            "success": True,
            "tasksCreated": len(created_tasks),
            "taskIds": created_tasks
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500