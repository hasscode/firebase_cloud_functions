from flask import jsonify
from google.cloud import firestore


REQUIRED_FIELDS = [
    "schemaVersion", "scheduledTaskId", "studentUid",
    "courseId", "courseName", "unitId", "lessonId",
    "taskId", "taskName", "weekNumber", "taskPriority",
    "courseTaskOrder", "thisCourseTaskCurrentPriority",
    "taskType", "timezone", "startAt", "dueAt",
    "generatedAt", "progressStatus", "progressAttemptCount",
    "progressCheckerType", "progressCheckerName"
]

VALID_TASK_PRIORITY = ["low", "normal", "high", "urgent"]

VALID_TASK_TYPES = [
    "lectureVideo", "explorationChat", "quiz",
    "reviewPractice", "reviewQuiz", "reviewSummary",
    "assignment", "liveSession", "examMarker", "holidayMarker"
]

VALID_PROGRESS_STATUS = [
    "notStarted", "inProgress", "completed", "blocked", "skipped"
]

VALID_CHECKER_TYPES = ["agent", "human", "platform", "system"]


def createCourse(req, db: firestore.Client):
    try:
        data = req.get_json()

        if not data:
            return jsonify({"error": "Missing request body"}), 400

        # ── Validate required fields ──
        missing = [f for f in REQUIRED_FIELDS if f not in data or data[f] is None]
        if missing:
            return jsonify({
                "error": "Missing required fields",
                "missingFields": missing
            }), 400

        # ── Validate schemaVersion ──
        if data.get("schemaVersion") != "StudentSchedule-2.1":
            return jsonify({
                "error": "Invalid schemaVersion",
                "expected": "StudentSchedule-2.1"
            }), 400

        # ── Validate enums ──
        if data.get("taskPriority") not in VALID_TASK_PRIORITY:
            return jsonify({
                "error": f"Invalid taskPriority. Must be one of: {VALID_TASK_PRIORITY}"
            }), 400

        if data.get("taskType") not in VALID_TASK_TYPES:
            return jsonify({
                "error": f"Invalid taskType. Must be one of: {VALID_TASK_TYPES}"
            }), 400

        if data.get("progressStatus") not in VALID_PROGRESS_STATUS:
            return jsonify({
                "error": f"Invalid progressStatus. Must be one of: {VALID_PROGRESS_STATUS}"
            }), 400

        if data.get("progressCheckerType") not in VALID_CHECKER_TYPES:
            return jsonify({
                "error": f"Invalid progressCheckerType. Must be one of: {VALID_CHECKER_TYPES}"
            }), 400

        # ── Validate taskType-specific required fields ──
        task_type = data.get("taskType")

        if task_type == "quiz":
            quiz_required = [
                "quizInstanceId", "quizVersion",
                "quizMinQuestionsToAsk", "quizMinScorePercentToPass"
            ]
            missing_quiz = [f for f in quiz_required if not data.get(f)]
            if missing_quiz:
                return jsonify({
                    "error": "Missing required quiz fields",
                    "missingFields": missing_quiz
                }), 400

        elif task_type == "lectureVideo":
            if not data.get("videoUrl"):
                return jsonify({
                    "error": "videoUrl is required for lectureVideo taskType"
                }), 400

        elif task_type == "liveSession":
            live_required = [
                "liveSessionJoinUrl",
                "liveSessionStartsAt",
                "liveSessionDurationMinutes"
            ]
            missing_live = [f for f in live_required if not data.get(f)]
            if missing_live:
                return jsonify({
                    "error": "Missing required liveSession fields",
                    "missingFields": missing_live
                }), 400

        # ── Build doc_id ──
        student_uid = data["studentUid"]
        course_id   = data["courseId"]
        doc_id      = data.get("scheduledTaskId") or f"{student_uid}_{course_id}"

        # ── Save to Firestore ──
        doc_ref = db.collection("courses").document(doc_id)
        doc     = doc_ref.get()

        payload = {**data, "updatedAt": firestore.SERVER_TIMESTAMP}

        if not doc.exists:
            payload["createdAt"] = firestore.SERVER_TIMESTAMP

        doc_ref.set(payload, merge=True)

        return jsonify({
            "success": True,
            "message": "Course created/updated successfully",
            "docId": doc_id,
            "studentUid": student_uid,
            "courseId": course_id
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500