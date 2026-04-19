from flask import jsonify
from google.cloud import firestore

def createQuiz(req, db: firestore.Client):
    try:
        data = req.get_json()

        if not data:
            return jsonify({"error": "Missing request body"}), 400

        quiz_meta = data.get("quizMeta")
        questions = data.get("questions")

        if not quiz_meta or not questions:
            return jsonify({"error": "quizMeta and questions are required"}), 400

        quiz_id = quiz_meta.get("quizInstanceId")

        if not quiz_id:
            return jsonify({"error": "quizInstanceId is required"}), 400

        doc_ref = db.collection("quizzes").document(quiz_id)

        # 👇 التعديل هنا
        doc_ref.set({
            "quizInstanceId": quiz_id,
            "quiz": {   # 🔥 كله متحط هنا
                "quizMeta": quiz_meta,
                "questions": questions
            },
            "createdAt": firestore.SERVER_TIMESTAMP,
            "updatedAt": firestore.SERVER_TIMESTAMP
        })

        return jsonify({
            "success": True,
            "message": "Quiz created successfully",
            "quizInstanceId": quiz_id
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500