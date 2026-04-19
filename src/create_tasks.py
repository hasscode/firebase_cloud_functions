from flask import jsonify
from google.cloud import firestore
from datetime import datetime, timezone

def createTasks(req, db: firestore.Client):
    try:
        data = req.get_json(silent=True) or {}

        # 1. التحقق من المدخلات الأساسية
        student_uid = data.get("studentUid")
        course_id = data.get("courseId")

        if not student_uid or not course_id:
            return jsonify({"error": "studentUid and courseId are required"}), 400

        # 2. جلب بيانات الـ Curriculum من Firestore
        # بنفترض إن اسم الدوكومنت هو نفسه الـ courseId
        curriculum_ref = db.collection("curriculums").document(course_id)
        curriculum_doc = curriculum_ref.get()

        if not curriculum_doc.exists:
            return jsonify({"error": f"Curriculum for course '{course_id}' not found"}), 404

        curriculum_data = curriculum_doc.to_dict().get("curriculum", {})
        
        # استخراج بيانات الكورس العامة لاستخدامها في كل Task
        course_name = curriculum_data.get("courseDisplayName", "")
        course_subject = curriculum_data.get("courseSubject", "")
        units = curriculum_data.get("units", [])

        # 3. تجهيز الـ Batch والبيانات الزمنية
        batch = db.batch()
        created_task_ids = []
        now_iso = datetime.now(timezone.utc).isoformat()

        # 4. الـ Flattening (تفكيك الوحدات والدروس للوصول للتاسكات)
        for unit in units:
            lessons = unit.get("lessons", [])
            for lesson in lessons:
                tasks_blueprint = lesson.get("tasks", [])
                
                for task_bp in tasks_blueprint:
                    # إنشاء ID فريد للتاسك الخاصة بهذا الطالب (دمج الـ Student UID مع الـ Task ID الأصلي)
                    original_task_id = task_bp.get("taskId")
                    scheduled_task_id = f"{student_uid}_{original_task_id}"

                    # 5. بناء الـ Task حسب الـ Final Schema (بدمج بيانات المنهج مع بيانات الطالب)
                    final_task = {
                        "scheduledTaskId": scheduled_task_id,
                        "studentUid": student_uid,
                        "scheduledCourseId": course_id,
                        "courseName": course_name,
                        "courseSubject": course_subject,
                        "taskTitle": task_bp.get("taskTitle", ""),
                        "taskType": task_bp.get("taskType", "chat"),
                        "taskStudentFacingInstruction": task_bp.get("taskStudentFacingInstruction", ""),
                        "taskTutorFacingInstruction": task_bp.get("taskTutorFacingInstruction", ""),
                        "taskDurationMinutes": task_bp.get("taskDurationMinutes", 0),
                        "taskDifficulty": task_bp.get("taskDifficulty", "medium"),
                        "taskUrl": task_bp.get("taskUrl", ""),
                        "taskApplicableCanonicalSkills": task_bp.get("taskApplicableCanonicalSkills", []),
                        
                        # حقول الحالة والتشغيل (Default values)
                        "taskStatus": "notStarted",
                        "isEligibleNow": True,
                        "isOverdue": False,
                        "taskPriority": task_bp.get("taskPriority", "medium"),
                        "priorityScore": 0,
                        
                        # حقول الـ Engagement والـ AI Context
                        "engagementLastUpdatedAt": "",
                        "engagementResults": "",
                        "quizInstanceId": task_bp.get("quizInstanceId", ""),
                        "recentPedagogicalContext": "",
                        "taskChatPrompt": task_bp.get("taskChatPrompt", ""),
                        "taskContents": str(task_bp.get("taskContents", "")), # تحويل لـ String حسب الـ Schema الجديدة
                        "taskCurrentRunningGuidance": "",
                        
                        # Timestamps
                        "createdAt": firestore.SERVER_TIMESTAMP,
                        "updatedAt": firestore.SERVER_TIMESTAMP,
                        "lastCalculatedAt": now_iso
                    }

                    # إضافة العملية للـ Batch
                    task_ref = db.collection("tasks").document(scheduled_task_id)
                    batch.set(task_ref, final_task, merge=True)
                    created_task_ids.append(scheduled_task_id)

        # 6. تنفيذ الـ Batch
        if created_task_ids:
            batch.commit()

        return jsonify({
            "success": True,
            "course": course_name,
            "student": student_uid,
            "tasksCreated": len(created_task_ids),
            "taskIds": created_task_ids
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500