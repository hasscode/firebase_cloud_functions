from flask import jsonify

def updateFlashcards(req, db):
    try:
        data = req.get_json()

        flashcard_id = data.get("quizMeta", {}).get("quizInstanceId")

        if not flashcard_id:
            return jsonify({"error": "quizInstanceId required"}), 400

        doc_ref = db.collection("flashcards").document(flashcard_id)

        if not doc_ref.get().exists:
            return jsonify({"error": "not found"}), 404

        doc_ref.set(data, merge=True)

        return jsonify({
            "success": True
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500