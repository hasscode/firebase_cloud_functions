from flask import jsonify
from google.cloud import firestore


ALLOWED_FIELDS = {
    # Schedule
    "weekNumber", "timezone", "startAt", "dueAt", "endAt",
    # Priority
    "taskPriority", "courseTaskOrder", "thisCourseTaskCurrentPriority",
    "priorityScore", "priorityReasonCodes", "priorityLastCalculatedAt",
    # Task config
    "taskAllowSkip", "taskLateAllowed", "taskLatePenaltyPercent",
    "taskPassScorePercent", "taskMaxAttempts", "taskTimeLimitSeconds",
    "taskShuffleQuestions",
    # Quiz
    "quizInstanceId", "quizVersion", "quizMinQuestionsToAsk",
    "quizMinScorePercentToPass", "quizLaunchUrl",
    # Video
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
    "schemaVersion", "scheduledTaskId", "studentUid",
    "courseId", "taskId", "unitId", "lessonId",
    "createdAt", "generatedAt", "auditSourceTemplateId"
}


def upsertStudentTask(req, db: firestore.Client):
    try:
        data = req.get_json()

        if not data:
            return jsonify({"error": "Missing request body"}), 400

        student_uid = data.get("studentUid")
        task_id     = data.get("taskId")
        course_id   = data.get("courseId")
        doc_id      = data.get("scheduledTaskId") or (
            f"{student_uid}_{course_id}_{task_id}"
            if student_uid and course_id and task_id else None
        )

        if not doc_id:
            return jsonify({
                "error": "scheduledTaskId or (studentUid + courseId + taskId) required"
            }), 400

        task_ref = db.collection("tasks").document(doc_id)
        task_doc = task_ref.get()

        if not task_doc.exists:
            return jsonify({"error": f"Task {doc_id} not found"}), 404

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

        task_ref.update(updates)

        return jsonify({
            "success":       True,
            "docId":         doc_id,
            "updatedFields": list(updates.keys()),
            "rejectedFields": rejected
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500