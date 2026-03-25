from flask import jsonify
from google.cloud import firestore


def getStudentProfile(req, db: firestore.Client):
    try:
        data = req.get_json(silent=True) or {}

        email = data.get("email")

        if not email:
            return jsonify({"error": "email is required"}), 400

        
        query = db.collection("students") \
                  .where("email", "==", email) \
                  .limit(1)

        docs = query.stream()

        student = None

        for doc in docs:
            student = doc.to_dict()
            student["id"] = doc.id  
            break

        if not student:
            return jsonify({"error": "Student not found"}), 404

        
        return jsonify({
            "success": True,
            "studentUid": student.get("studentUid", student["id"]),
            "profile": student
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500