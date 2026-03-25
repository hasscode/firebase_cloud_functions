from flask import jsonify
from google.cloud import firestore


def getTasks(req, db):
    try:
        data = req.get_json(silent=True) or {}

        student_uid = data.get("studentUid")
        course_id   = data.get("courseId")
        status      = data.get("progressStatus")

        # 🔥 default = True (important for AI)
        sort_by_priority = data.get("sortByPriority", True)
        limit            = data.get("limit")

        if not student_uid:
            return jsonify({"error": "studentUid is required"}), 400

        query = db.collection("tasks").where("studentUid", "==", student_uid)

        # optional filters
        if course_id:
            query = query.where("courseId", "==", course_id)

        if status:
            query = query.where("progressStatus", "==", status)

        # 🔥 FIXED sorting logic
        if sort_by_priority:
            query = query.order_by("priorityScore", direction=firestore.Query.DESCENDING)
        else:
            query = query.order_by("createdAt", direction=firestore.Query.DESCENDING)

        # pagination / limit
        if limit:
            query = query.limit(limit)

        docs = query.stream()

        tasks = []
        for doc in docs:
            task = doc.to_dict()
            task["id"] = doc.id
            tasks.append(task)

        return jsonify({
            "success": True,
            "tasksCount": len(tasks),
            "tasks": tasks
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500