from flask import jsonify
from google.cloud import firestore
from datetime import datetime, timezone

def upload_curriculum(req, db: firestore.Client):
    try:
        data = req.get_json(silent=True) or {}
        
        # التأكد من وجود البيانات الأساسية حسب الـ Schema
        if "curriculum" not in data or "courseId" not in data["curriculum"]:
            return jsonify({"error": "Missing curriculum or courseId"}), 400

        curriculum_data = data["curriculum"]
        course_id = curriculum_data["courseId"]

        # إضافة بيانات ميتا (Meta Data) للرفع
        data["uploadedAt"] = datetime.now(timezone.utc).isoformat()
        data["status"] = "draft" # أو active حسب الرغبة

        # التخزين في Firestore
        # نستخدم الـ courseId كـ Document ID لسهولة الوصول
        doc_ref = db.collection("curriculums").document(course_id)
        doc_ref.set(data)

        return jsonify({
            "success": True,
            "courseId": course_id,
            "message": f"Curriculum '{curriculum_data.get('courseDisplayName')}' uploaded successfully."
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500