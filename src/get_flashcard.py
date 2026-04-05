from flask import jsonify
from google.cloud import firestore

def getFlashcards(req, db: firestore.Client):
    try:
        data = req.get_json(silent=True) or {}
        flashcard_id = data.get("quizInstanceId")

        if flashcard_id:
            doc = db.collection("flashcards").document(flashcard_id).get()

            if not doc.exists:
                return jsonify({"error": "Flashcards not found"}), 404

            doc_data = doc.to_dict()

            return jsonify({
                "success": True,
                "quizInstanceId": flashcard_id,
                "flashcards": doc_data.get("flashcards", {}) # هترجع nested ومش flat
            })

        # ====================================
        # 🔹 Get list of Flashcards
        # ====================================
        limit = data.get("limit", 10)
        docs = db.collection("flashcards").limit(limit).stream()

        results = []
        for doc in docs:
            d = doc.to_dict()
            results.append({
                "quizInstanceId": d.get("quizInstanceId"),
                "flashcards": d.get("flashcards", {})
            })

        return jsonify({
            "success": True,
            "count": len(results),
            "flashcards": results
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500