from flask import jsonify
from google.cloud import firestore

def updateQuiz(req, db: firestore.Client):
    try:
        data = req.get_json()

        if not data:
            return jsonify({"error": "Missing request body"}), 400

        quiz_meta = data.get("quizMeta")
        quiz_id   = quiz_meta.get("quizInstanceId") if quiz_meta else None

        if not quiz_id:
            return jsonify({"error": "quizInstanceId is required"}), 400

        doc_ref = db.collection("quizzes").document(quiz_id)
        doc     = doc_ref.get()

        if not doc.exists:
            return jsonify({"error": "Quiz not found"}), 404

        updates = {}

        if "quizMeta" in data:
            updates["quizMeta"] = data["quizMeta"]

        if "questions" in data:
            updates["questions"] = data["questions"]

        if not updates:
            return jsonify({"error": "No fields to update"}), 400

        updates["updatedAt"] = firestore.SERVER_TIMESTAMP

        doc_ref.update(updates)

        return jsonify({
            "success": True,
            "message": "Quiz updated successfully",
            "updatedFields": list(updates.keys())
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500