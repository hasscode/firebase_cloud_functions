from flask import jsonify
from google.cloud import firestore

def createFlashcardSet(req, db: firestore.Client):
    try:
        data = req.get_json(silent=True) or {}

        flashcard_id = data.get("quizInstanceId")
  
        flashcard_data = data.get("flashcards")

        if not flashcard_id or not flashcard_data:
            return jsonify({"error": "quizInstanceId and flashcards object are required"}), 400

        doc_ref = db.collection("flashcards").document(flashcard_id)

      
        doc_ref.set({
            "quizInstanceId": flashcard_id,
            "flashcards": flashcard_data
        })

        return jsonify({
            "success": True,
            "quizInstanceId": flashcard_id
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500