from flask import jsonify
from google.cloud import firestore
from datetime import datetime, timezone


VALID_TASK_TYPES = [
    "lectureVideo", "explorationChat", "quiz",
    "reviewPractice", "reviewQuiz", "reviewSummary",
    "assignment", "liveSession", "examMarker", "holidayMarker"
]

PRIORITY_HINT_MAP = {
    "low":           "low",
    "normal":        "normal",
    "high":          "high",
    "urgent":        "urgent",
    "critical":      "urgent",
    "very_critical": "urgent",
}


def createTasks(req, db: firestore.Client):
    try:
        data = req.get_json()

        if not data:
            return jsonify({"error": "Missing request body"}), 400

        student_uid         = data.get("studentUid")
        course_id           = data.get("courseId")
        scheduled_course_id = data.get("scheduledCourseId")
        timezone_str        = data.get("timezone", "UTC")
        week_start_at       = data.get("weekStartAt")
        week_end_at         = data.get("weekEndAt")

        if not student_uid:
            return jsonify({"error": "studentUid is required"}), 400
        if not course_id:
            return jsonify({"error": "courseId is required"}), 400

        curriculum_doc = db.collection("courseCurriculum").document(course_id).get()

        if not curriculum_doc.exists:
            return jsonify({"error": f"Curriculum not found for courseId: {course_id}"}), 404

        curriculum_data = curriculum_doc.to_dict()
        curriculum      = curriculum_data.get("curriculum", {})
        units           = curriculum.get("units", [])

        if not units:
            return jsonify({"error": "Curriculum has no units"}), 400

        course_name    = curriculum.get("courseName")
        course_subject = curriculum.get("courseSubject")
        now_iso        = datetime.now(timezone.utc).isoformat()

        batch         = db.batch()
        created_tasks = []

        for unit in units:
            unit_id  = unit.get("unitId")
            lessons  = unit.get("lessons", [])

            for lesson in lessons:
                lesson_id  = lesson.get("lessonId")
                tasks_list = lesson.get("tasks", [])

                for task in tasks_list:
                    task_id           = task.get("taskId")
                    task_type         = task.get("taskType")
                    course_task_order = task.get("courseTaskOrder", 1)
                    week_number       = task.get("recommendedWeekNumber", 1)
                    task_content      = task.get("taskContent", {})

                    if not task_id or not task_type:
                        continue

                    if task_type not in VALID_TASK_TYPES:
                        continue

                    scheduled_task_id = f"{student_uid}_{course_id}_{task_id}"
                    start_at          = week_start_at or now_iso
                    due_at            = week_end_at or now_iso
                    priority_hint     = task.get("defaultTaskPriorityHint", "normal")
                    task_priority     = PRIORITY_HINT_MAP.get(priority_hint, "normal")

                    task_doc = {
                        # ── Identity ──
                        "schemaVersion": "StudentSchedule-2.2",
                        "scheduledTaskId": scheduled_task_id,
                        "scheduledCourseId": scheduled_course_id,
                        "studentUid": student_uid,
                        "courseId": course_id,
                        "courseName": course_name,
                        "courseSubject": course_subject,
                        "unitId": unit_id,
                        "lessonId": lesson_id,
                        "taskId": task_id,
                        "taskName": task.get("taskName"),

                        # ── Schedule ──
                        "weekNumber": week_number,
                        "timezone": timezone_str,
                        "startAt": start_at,
                        "dueAt": due_at,
                        "endAt": None,
                        "generatedAt": now_iso,

                        # ── Priority ──
                        "taskPriority": task_priority,
                        "courseTaskOrder": course_task_order,
                        "thisCourseTaskCurrentPriority": course_task_order,
                        "priorityScore": None,
                        "priorityReasonCodes": [],
                        "priorityLastCalculatedAt": None,

                        # 🆕 NEW FIELDS
                        "taskRunningReadableNarrative": None,
                        "taskMetaReadableNarrative": None,
                        "isEligibleNow": True,
                        "engagementStatus": None,

                        # ── Task Type ──
                        "taskType": task_type,

                        # ── Quiz ──
                        "quizInstanceId": task_content.get("quizId"),

                        # ── Video ──
                        "videoUrl": task_content.get("videoUrl"),

                        # ── Agent ──
                        "agentTaskPrompt": task_content.get("prompt"),

                        # ── Progress ──
                        "progressStatus": "notStarted",
                        "progressAttemptCount": 0,

                        # ── Audit ──
                        "auditGeneratedBy": "createTasks",
                        "auditSourceTemplateId": course_id,

                        # ── Timestamps ──
                        "createdAt": firestore.SERVER_TIMESTAMP,
                        "updatedAt": firestore.SERVER_TIMESTAMP,
                    }

                    ref = db.collection("tasks").document(scheduled_task_id)
                    batch.set(ref, task_doc, merge=True)
                    created_tasks.append(scheduled_task_id)

        batch.commit()

        return jsonify({
            "success": True,
            "tasksCreated": len(created_tasks),
            "taskIds": created_tasks
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500