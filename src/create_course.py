from flask import jsonify
from google.cloud import firestore
from datetime import datetime, timezone

def create_course(req, db: firestore.Client):
    try:
        data = req.get_json(silent=True) or {}
        student_uid = data.get("studentUid")
        course_id = data.get("courseId") # الـ ID بتاع المنهج في collection curriculums

        if not student_uid or not course_id:
            return jsonify({"error": "studentUid and courseId are required"}), 400

        # 1. جلب بيانات المنهج
        curriculum_ref = db.collection("curriculums").document(course_id)
        curr_doc = curriculum_ref.get()

        if not curr_doc.exists:
            return jsonify({"error": "Curriculum not found"}), 404
        
        # بنوصل للـ curriculum object جوه الدوكومنت
        curr_data = curr_doc.to_dict().get("curriculum", {})

        # 2. حساب عدد التاسكات الكلي من المنهج
        total_tasks = 0
        for unit in curr_data.get("units", []):
            for lesson in unit.get("lessons", []):
                total_tasks += len(lesson.get("tasks", []))

        # 3. تجهيز أوبجكت الكورس حسب الـ Student Course Schema
        new_student_course = {
            "courseCanonicalName": curr_data.get("courseCanonicalName"),
            "courseDisplayName": curr_data.get("courseDisplayName"),
            "courseCategory": curr_data.get("courseSubject"), # Mapping subject to category
            "courseLevel": curr_data.get("courseLevel"),
            "courseStatus": "active",
            "targetCompletionPercent": curr_data.get("targetCompletionPercent", 100),
            "expectedCompletionPercentByThisWeek": 0,
            "actualCompletionPercent": 0,
            "goalStatus": "onTrack",
            "courseHealthStatus": "healthy",
            "engagementCurrentValue": "none",
            "engagementTrend": "stable",
            "engagementPreviousValue": "none",
            "averageDailyEngagementMinutes": 0,
            "targetWeeklyStudyHours": curr_data.get("targetWeeklyStudyHours", 0),
            "assessmentAveragePercent": 0,
            "lastAssessmentPercent": 0,
            "assessmentPassRatePercent": 0,
            "completedTaskCount": 0,
            "pendingTaskCount": total_tasks,
            "overdueTaskCount": 0,
            "nextPriorityFocus": "Begin the first lesson and engage with the introductory tasks.",
            "courseStatusNarrative": f"Course {curr_data.get('courseDisplayName')} initialized for student.",
            "engagementNarrative": "No engagement recorded yet.",
            "performanceNarrative": "No assessments completed yet.",
            "supportFocusNarrative": "Standard path. No specific support needed at this stage.",
            "courseSummaryNarrative": "New course started. Ready for the first step."
        }

        # 4. تحديث أو إنشاء دوكومنت الطالب في student_courses
        # هنستخدم الـ studentUid كـ Document ID ونحدث الـ array اللي جواه
        student_courses_ref = db.collection("courses").document(student_uid)
        
        # بنستخدم arrayUnion عشان لو الطالب عنده كورسات تانية متمسحش
        student_courses_ref.set({
            "schemaVersion": "CoursesForStudentNarrativeLite",
            "studentUid": student_uid,
            "courses": firestore.ArrayUnion([new_student_course])
        }, merge=True)

        return jsonify({
            "success": True,
            "message": f"Course {course_id} successfully assigned to student {student_uid}",
            "totalTasksAssigned": total_tasks
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500