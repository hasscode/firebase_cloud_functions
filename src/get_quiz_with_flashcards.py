from flask import jsonify
from google.cloud import firestore

def getQuizAndFlashcards(req, db: firestore.Client):
    try:
        data = req.get_json(silent=True) or {}
        instance_id = data.get("quizInstanceId")

        if not instance_id:
            return jsonify({"error": "quizInstanceId is required"}), 400

        # 1. بنجيب الـ Quiz
        quiz_doc = db.collection("quizzes").document(instance_id).get()
        quiz_data = quiz_doc.to_dict().get("quiz", {}) if quiz_doc.exists else None

        # 2. بنجيب الـ Flashcards
        fc_doc = db.collection("flashcards").document(instance_id).get()
        fc_data = fc_doc.to_dict().get("flashcards", {}) if fc_doc.exists else None

        # لو ملقيناش الاتنين
        if not quiz_data and not fc_data:
            return jsonify({"error": "No quiz or flashcards found for this ID"}), 404

        return jsonify({
            "success": True,
            "quizInstanceId": instance_id,
            "quiz": quiz_data or {},
            "flashcards": fc_data or {}
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500