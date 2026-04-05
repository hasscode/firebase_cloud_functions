from flask import jsonify
from google.cloud import firestore


def getTasks(req, db):
    try:
        data = req.get_json(silent=True) or {}

        student_uid = data.get("studentUid")
        course_id   = data.get("courseId")
        status      = data.get("progressStatus")

        deprioritize_optional = data.get("deprioritizeOptionalTasks", False)
        limit = data.get("limit")

        if not student_uid:
            return jsonify({"error": "studentUid is required"}), 400

        # 1️⃣ Query
        query = db.collection("tasks").where("studentUid", "==", student_uid)

        if course_id:
            query = query.where("scheduledCourseId", "==", course_id)

        if status:
            query = query.where("taskStatus", "==", status)

        docs = query.stream()

        tasks = []
        for doc in docs:
            task = doc.to_dict()
            task["id"] = doc.id
            tasks.append(task)

        # 2️⃣ Sorting logic
        def sort_key(task):
            priority = task.get("taskPriority", "").lower()
            is_optional = task.get("isOptional", False)

            order = task.get("courseTaskOrder", 9999)
            task_id = task.get("scheduledTaskId", "")

           
            is_critical = priority in ["critical", "verycritical"]

       
            if is_critical:
                bucket = 0
            elif deprioritize_optional and is_optional:
                bucket = 2
            else:
                bucket = 1

       
            return (bucket, order, task_id)

        tasks.sort(key=sort_key)

        # 3️⃣ Limit
        if limit:
            tasks = tasks[:limit]

        return jsonify({
            "success": True,
            "tasksCount": len(tasks),
            "tasks": tasks
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500