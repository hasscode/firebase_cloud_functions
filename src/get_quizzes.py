from flask import jsonify
from google.cloud import firestore

def getQuizzes(req, db: firestore.Client):
    try:
        data = req.get_json(silent=True) or {}

        quiz_id = data.get("quizInstanceId")

      
        if quiz_id:
            doc = db.collection("quizzes").document(quiz_id).get()

            if not doc.exists:
                return jsonify({"error": "Quiz not found"}), 404

            quiz = doc.to_dict()
            quiz["id"] = doc.id

            return jsonify({
                "success": True,
                "quiz": quiz
            })

        limit = data.get("limit", 10)

        docs = db.collection("quizzes").limit(limit).stream()

        quizzes = []
        for doc in docs:
            q = doc.to_dict()
            q["id"] = doc.id
            quizzes.append(q)

        return jsonify({
            "success": True,
            "count": len(quizzes),
            "quizzes": quizzes
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500