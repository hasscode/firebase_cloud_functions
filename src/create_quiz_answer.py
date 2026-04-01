from flask import jsonify
from datetime import datetime

def createQuizAnswer(req, db):
    try:
        data = req.get_json()

        quiz_id = data.get("quizInstanceId")
        student_email = data.get("studentEmail")
        answers = data.get("questionAnswers")

        if not quiz_id or not student_email or not answers:
            return jsonify({"error": "quizInstanceId, studentEmail, questionAnswers required"}), 400

        doc_data = {
            "schemaVersion": data.get("schemaVersion", "QuizAnswers-1.0"),
            "quizInstanceId": quiz_id,
            "studentEmail": student_email,
            "submittedAt": datetime.utcnow().isoformat(),
            "questionAnswers": answers
        }

        doc_ref = db.collection("quiz_answers").document()
        doc_ref.set(doc_data)

        return jsonify({
            "success": True,
            "id": doc_ref.id
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500