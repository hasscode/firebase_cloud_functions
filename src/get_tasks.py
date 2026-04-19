from flask import jsonify
from google.cloud import firestore

def getTasks(req, db: firestore.Client):
    try:
        data = req.get_json(silent=True) or {}
        student_uid = data.get("studentUid")
        course_id = data.get("courseId")
        # الـ Statuses المتوافقة مع الـ Schema
        statuses = data.get("progressStatus", ["notStarted", "inProgress"])
        limit = data.get("limit")

        if not student_uid:
            return jsonify({"error": "studentUid is required"}), 400

        # 1. Query الأساسي
        query = db.collection("tasks").where("studentUid", "==", student_uid)

        if course_id:
            query = query.where("scheduledCourseId", "==", course_id)

        # فلترة الـ Status (Firestore بيقبل "in" للـ lists)
        if isinstance(statuses, list) and len(statuses) > 0:
            query = query.where("taskStatus", "in", statuses)

        docs = query.stream()
        tasks_list = []

        for doc in docs:
            task_data = doc.to_dict()
            tasks_list.append(task_data)

        # 2. Sorting Logic (محرك الأولوية لـ Boraq)
        def sort_key(t):
            # ترتيب الـ Priority حسب الـ Schema
            priority_map = {
                "veryHigh": 0, "high": 1, "medium": 2, 
                "low": 3, "veryLow": 4
            }
            p_val = priority_map.get(t.get("taskPriority"), 2)
            score = t.get("priorityScore", 0)
            
            # بنرتب بالـ Priority الأول، وبعدين الـ Score الأعلى (Descending)
            return (p_val, -score)

        tasks_list.sort(key=sort_key)

        if limit:
            tasks_list = tasks_list[:limit]

        # الرد مطابق للـ Schema النهائية
        return jsonify({
            "schemaVersion": "priorityTasksFlatReadable_v1",
            "tasks": tasks_list
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500