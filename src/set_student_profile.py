from flask import jsonify
from google.cloud import firestore


IMMUTABLE_FIELDS = {
    "studentUid", "email", "createdAt"
}


def set_student_profile(req, db: firestore.Client):
    try:
        data = req.get_json(silent=True) or {}

        student_uid = data.get("studentUid")

        if not student_uid:
            return jsonify({"error": "studentUid is required"}), 400

        profile = data.get("profile") or data

        # احذف الـ immutable fields من الـ payload
        clean_profile = {
            k: v for k, v in profile.items()
            if k not in IMMUTABLE_FIELDS
        }

        doc_ref = db.collection("students").document(student_uid)
        doc     = doc_ref.get()

        payload = {
            **clean_profile,
            "studentUid": student_uid,
            "updatedAt": firestore.SERVER_TIMESTAMP
        }

        if not doc.exists:
            payload["createdAt"] = firestore.SERVER_TIMESTAMP

        doc_ref.set(payload, merge=True)

        return jsonify({
            "success":    True,
            "message":    "Student profile saved successfully",
            "studentUid": student_uid
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500