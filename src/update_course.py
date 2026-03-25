from flask import jsonify
from google.cloud import firestore


ALLOWED_FIELDS = {
    # Identity
    "courseName", "courseSubject", "scheduledCourseId",

    # Scheduling
    "weekNumber", "timezone", "startAt", "dueAt", "endAt",

    # Priority
    "taskPriority", "courseTaskOrder", "thisCourseTaskCurrentPriority",
    "priorityScore", "priorityReasonCodes", "priorityLastCalculatedAt",

    # Task config
    "taskType", "taskMaxAttempts", "taskTimeLimitSeconds",
    "taskShuffleQuestions", "taskAllowSkip", "taskLateAllowed",
    "taskLatePenaltyPercent", "taskPassScorePercent",

    # Quiz
    "quizInstanceId", "quizVersion", "quizMinQuestionsToAsk",
    "quizMinScorePercentToPass", "quizLaunchUrl",

   
    "videoAssetId", "videoUrl", "videoCaptionsUrl",

    # Live session
    "liveSessionPlatform", "liveSessionId", "liveSessionJoinUrl",
    "liveSessionStartsAt", "liveSessionDurationMinutes",

    # Agent
    "agentId", "agentName", "agentRole", "agentPersonaVersion",
    "agentSystemPrompt", "agentTaskPrompt", "agentTone", "agentLanguage",
    "agentChatSessionId", "agentChatStatus",
    "agentChatStartedAt", "agentChatLastMessageAt",

    # Progress
    "progressStatus", "progressStartedAt", "progressCompletedAt",
    "progressLastActivityAt", "progressAttemptCount",
    "progressScorePercent", "progressCheckedInAt",
    "progressCheckerType", "progressCheckerName", "progressCheckerNotes",
}


IMMUTABLE_FIELDS = {
    "studentUid", "courseId", "scheduledTaskId",
    "schemaVersion", "createdAt", "generatedAt",
    "taskId", "unitId", "lessonId"
}


def updateCourse(req, db: firestore.Client):
    try:
        data = req.get_json()

        if not data:
            return jsonify({"error": "Missing request body"}), 400

        student_uid = data.get("studentUid")
        course_id   = data.get("courseId")
        doc_id      = data.get("scheduledTaskId") or (
            f"{student_uid}_{course_id}" if student_uid and course_id else None
        )

        if not doc_id:
            return jsonify({
                "error": "scheduledTaskId or (studentUid + courseId) required"
            }), 400

        doc_ref = db.collection("courses").document(doc_id)

        if not doc_ref.get().exists:
            return jsonify({"error": f"Course {doc_id} not found"}), 404

       
        updates = {
            k: v for k, v in data.items()
            if k in ALLOWED_FIELDS
        }

     
        rejected = [
            k for k in data.keys()
            if k in IMMUTABLE_FIELDS
        ]

        if not updates:
            return jsonify({
                "error": "No valid fields to update",
                "rejectedFields": rejected
            }), 400

        updates["updatedAt"] = firestore.SERVER_TIMESTAMP

        doc_ref.update(updates)

        return jsonify({
            "success": True,
            "docId": doc_id,
            "updatedFields": list(updates.keys()),
            "rejectedFields": rejected
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500