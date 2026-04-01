from flask import jsonify

def getQuizAnswers(req, db):
    try:
        data = req.get_json(silent=True) or {}

        student_email = data.get("studentEmail")
        quiz_id       = data.get("quizInstanceId")

        query = db.collection("quiz_answers")

        if student_email:
            query = query.where("studentEmail", "==", student_email)

        if quiz_id:
            query = query.where("quizInstanceId", "==", quiz_id)

        docs = query.stream()

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