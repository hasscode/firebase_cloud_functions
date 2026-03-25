import json
def simplify_curriculum(data):

    curriculum = data.get("curriculum", {})
    units = curriculum.get("units", [])

    clean_units = []

    for unit in units:

        clean_lessons = []

        for lesson in unit.get("lessons", []):

            lesson_context = lesson.get("lessonContext", {})

            clean_tasks = []

            for task in lesson.get("tasks", []):

                clean_tasks.append({
                    "taskId": task.get("taskId"),
                    "taskName": task.get("taskName"),
                    "taskType": task.get("taskType"),
                    "estimatedMinutes": task.get("estimatedMinutes"),
                    "recommendedWeek": task.get("recommendedWeekNumber")
                })

            clean_lessons.append({
                "lessonId": lesson.get("lessonId"),
                "lessonName": lesson.get("lessonName"),
                "lessonOrder": lesson.get("lessonOrder"),
                "learningGoal": lesson_context.get("learningGoal"),
                "theme": lesson_context.get("theme"),
                "tasks": clean_tasks
            })

        clean_units.append({
            "unitId": unit.get("unitId"),
            "unitName": unit.get("unitName"),
            "unitOrder": unit.get("unitOrder"),
            "lessons": clean_lessons
        })

    return clean_units


def getCurriculum(req, db):

    if req.method != "POST":
        return (
            json.dumps({"error": "POST required"}),
            400,
            {"Content-Type": "application/json"},
        )

    data = req.get_json()

    if not data or "courseId" not in data:
        return (
            json.dumps({"error": "Missing courseId"}),
            400,
            {"Content-Type": "application/json"},
        )

    course_id = data["courseId"]

    try:

        doc = db.collection("courseCurriculum").document(course_id).get()

        if not doc.exists:
            return (
                json.dumps({"error": "Curriculum not found"}),
                404,
                {"Content-Type": "application/json"},
            )

        raw = doc.to_dict()

        cleaned_units = simplify_curriculum(raw)

        result = {
            "courseId": course_id,
            "schemaVersion": raw.get("schemaVersion"),
            "units": cleaned_units
        }

        return (
            json.dumps(result),
            200,
            {"Content-Type": "application/json"},
        )

    except Exception as e:

        return (
            json.dumps({"error": str(e)}),
            500,
            {"Content-Type": "application/json"},
        )