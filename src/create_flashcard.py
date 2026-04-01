from flask import jsonify

def createFlashcardSet(req, db):
    try:
        data = req.get_json()

        quiz_meta = data.get("quizMeta")
        questions = data.get("questions")

        if not quiz_meta or not questions:
            return jsonify({"error": "quizMeta and questions required"}), 400

        flashcard_id = quiz_meta.get("quizInstanceId")

        if not flashcard_id:
            return jsonify({"error": "quizInstanceId required in quizMeta"}), 400

        doc_ref = db.collection("flashcards").document(flashcard_id)

        doc_ref.set(data)

        return jsonify({
            "success": True,
            "id": flashcard_id
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500