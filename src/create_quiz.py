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

            doc_data = doc.to_dict()

            return jsonify({
                "success": True,
                "quizInstanceId": quiz_id,
                "quiz": doc_data.get("quiz", {})  # 👈 رجع الـ JSON زي ما هو
            })

        # =========================
        # 🔹 Get list of quizzes
        # =========================
        limit = data.get("limit", 10)

        docs = db.collection("quizzes").limit(limit).stream()

        quizzes = []
        for doc in docs:
            d = doc.to_dict()

            quizzes.append({
                "quizInstanceId": d.get("quizInstanceId"),
                "quiz": d.get("quiz", {})
            })

        return jsonify({
            "success": True,
            "count": len(quizzes),
            "quizzes": quizzes
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500