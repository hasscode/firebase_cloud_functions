from flask import jsonify
from google.cloud import firestore
from datetime import datetime, timezone

# القائمة النهائية للحقول المسموح بتحديثها بناءً على طلب المدير
ALLOWED_RUNNING_FIELDS = {
    "currentMood",
    "availableTimeMinutes",
    "goalByStudent",
    "goalByAI",
    "activityNarrative",
    "recentPedagogicalContext"
}

def update_student_running_status(req, db: firestore.Client):
    """
    تحديث حالة الطالب الجارية (Running Status).
    يقبل أي تشكيلة من الحقول الستة المسموحة فقط.
    """
    try:
        # استلام البيانات
        data = req.get_json(silent=True) or {}
        
        # 1. التحقق من وجود المعرف الفريد للطالب
        student_uid = data.get("studentUid")
        if not student_uid:
            return jsonify({"error": "studentUid is required"}), 400

        # 2. فلترة البيانات (Whitelist) بناءً على طلب المدير
        clean_updates = {}
        for key in ALLOWED_RUNNING_FIELDS:
            if key in data:
                clean_updates[key] = data[key]

        # إذا لم يرسل الـ Agent أي حقل من الستة المسموحة
        if not clean_updates:
            allowed_str = ", ".join(sorted(ALLOWED_RUNNING_FIELDS))
            return jsonify({"error": f"No valid fields provided. Allowed fields are: {allowed_str}"}), 400

        # 3. مرجع المستند في مجموعة student_running_status
        doc_ref = db.collection("student_running_status").document(student_uid)
        
        # 4. تحديث وقت التعديل تلقائياً (ISO format)
        clean_updates["lastUpdatedAt"] = datetime.now(timezone.utc).isoformat()

        # 5. تنفيذ التحديث (Set مع merge=True) 
        # لضمان تحديث الحقول المبعوثة فقط وعدم التأثير على باقي البيانات أو الـ Arrays
        doc_ref.set(clean_updates, merge=True)

        return jsonify({
            "success": True,
            "studentUid": student_uid,
            "updatedFields": list(clean_updates.keys())
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500