from flask import jsonify
from google.cloud import firestore


def getCourses(req, db: firestore.Client):
    try:
        data = req.get_json(silent=True) or {}

        student_uid = data.get("studentUid")

        if not student_uid:
            return jsonify({"error": "studentUid is required"}), 400

        query = db.collection("courses") \
                  .where("studentUid", "==", student_uid)

        docs = query.stream()

        courses = []
        for doc in docs:
            course = doc.to_dict()
            course["id"] = doc.id
            courses.append(course)

        return jsonify({
            "success": True,
            "studentUid": student_uid,
            "coursesCount": len(courses),
            "courses": courses
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500