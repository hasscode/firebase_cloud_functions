from flask import jsonify
from google.cloud import firestore
from jsonschema import ValidationError, validate


COURSES_SCHEMA = {
    "type": "object",
    "properties": {
        "schemaVersion": {
            "type": "string",
            "const": "CoursesForStudentNarrativeLite"
        },
        "studentUid": {
            "type": "string"
        },
        "courses": {
            "type": "array",
            "default": [],
            "items": {
                "$ref": "#/$defs/course"
            }
        }
    },
    "$defs": {
        "course": {
            "type": "object",
            "properties": {
                "courseCanonicalName": {"type": "string"},
                "courseDisplayName": {"type": "string"},
                "courseCategory": {"type": "string"},
                "courseLevel": {"type": "string"},
                "courseStatus": {"type": "string"},
                "targetCompletionPercent": {"type": "number", "minimum": 0, "maximum": 100},
                "expectedCompletionPercentByThisWeek": {"type": "number", "minimum": 0, "maximum": 100},
                "actualCompletionPercent": {"type": "number", "minimum": 0, "maximum": 100},
                "goalStatus": {"type": "string"},
                "courseHealthStatus": {"type": "string"},
                "engagementCurrentValue": {"type": "string"},
                "engagementTrend": {"type": "string"},
                "engagementPreviousValue": {"type": "string"},
                "averageDailyEngagementMinutes": {"type": "number", "minimum": 0},
                "targetWeeklyStudyHours": {"type": "number", "minimum": 0},
                "assessmentAveragePercent": {"type": "number", "minimum": 0, "maximum": 100},
                "lastAssessmentPercent": {"type": "number", "minimum": 0, "maximum": 100},
                "assessmentPassRatePercent": {"type": "number", "minimum": 0, "maximum": 100},
                "completedTaskCount": {"type": "integer", "minimum": 0},
                "pendingTaskCount": {"type": "integer", "minimum": 0},
                "overdueTaskCount": {"type": "integer", "minimum": 0},
                "nextPriorityFocus": {"type": "string"},
                "courseStatusNarrative": {"type": "string"},
                "engagementNarrative": {"type": "string"},
                "performanceNarrative": {"type": "string"},
                "supportFocusNarrative": {"type": "string"},
                "courseSummaryNarrative": {"type": "string"}
            },
            "additionalProperties": False,
            "required": [
                "courseCanonicalName", "courseDisplayName", "courseCategory", "courseLevel",
                "courseStatus", "targetCompletionPercent", "expectedCompletionPercentByThisWeek",
                "actualCompletionPercent", "goalStatus", "courseHealthStatus", "engagementCurrentValue",
                "engagementTrend", "engagementPreviousValue", "averageDailyEngagementMinutes",
                "targetWeeklyStudyHours", "assessmentAveragePercent", "lastAssessmentPercent",
                "assessmentPassRatePercent", "completedTaskCount", "pendingTaskCount", "overdueTaskCount",
                "nextPriorityFocus", "courseStatusNarrative", "engagementNarrative", "performanceNarrative",
                "supportFocusNarrative", "courseSummaryNarrative"
            ]
        }
    },
    "additionalProperties": False,
    "required": [
        "schemaVersion", "studentUid", "courses"
    ]
}

def create_course(req, db: firestore.Client):
    try:
        data = req.get_json()

        if not data:
            return jsonify({"error": "Missing request body"}), 400

        validate(instance=data, schema=COURSES_SCHEMA)
        
       
        student_uid = data["studentUid"]
        
        doc_id = f"summary_{student_uid}"

        doc_ref = db.collection("student_courses_summaries").document(doc_id)
        doc = doc_ref.get()

        payload = {**data, "updatedAt": firestore.SERVER_TIMESTAMP}

        if not doc.exists:
            payload["createdAt"] = firestore.SERVER_TIMESTAMP

        doc_ref.set(payload, merge=True)

        return jsonify({
            "success": True,
            "message": "Student courses summary created/updated successfully",
            "docId": doc_id,
            "studentUid": student_uid
        })

    except ValidationError as e:
    
        return jsonify({
            "error": "Invalid schema data",
            "details": e.message
        }), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500
