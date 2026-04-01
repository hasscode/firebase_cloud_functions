from flask import jsonify

def getFlashcards(req, db):
    try:
        data = req.get_json(silent=True) or {}

        flashcard_id = data.get("quizInstanceId")

        if flashcard_id:
            doc = db.collection("flashcards").document(flashcard_id).get()

            if not doc.exists:
                return jsonify({"error": "not found"}), 404

            result = doc.to_dict()
            result["id"] = doc.id

            return jsonify({
                "success": True,
                "data": result
            })

        # get all
        docs = db.collection("flashcards").stream()

        results = []
        for doc in docs:
            item = doc.to_dict()
            item["id"] = doc.id
            results.append(item)

        return jsonify({
            "success": True,
            "count": len(results),
            "data": results
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500