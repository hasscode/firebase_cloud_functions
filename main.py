from firebase_functions import https_fn, firestore_fn, scheduler_fn
import firebase_admin
from firebase_admin import firestore
from flask import jsonify

# تهيئة التطبيق مرة واحدة فقط
if not firebase_admin._apps:
    firebase_admin.initialize_app()

# =========================================================
# 🔹 1. مشغلات محرك الأولويات (Background Triggers)
# هذه الدوال تعمل تلقائياً في الخلفية عند إضافة أو تعديل أي Task
# =========================================================

# from src.task_priority_engine import (
#     on_task_create, 
#     on_task_update, 
#     recalculate_all_tasks_daily
# )

# # تصدير المشغلات لكي يتعرف عليها Firebase عند الـ Deploy
# task_priority_on_create = on_task_create
# task_priority_on_update = on_task_update
# task_priority_daily_sync = recalculate_all_tasks_daily



@https_fn.on_request()
def get_tasks(req: https_fn.Request) -> https_fn.Response:
    from src.get_tasks import getTasks
    db = firestore.client()
    return getTasks(req, db)

# @https_fn.on_request()
# def update_tasks(req: https_fn.Request) -> https_fn.Response:
#     from src.update_task import upsertStudentTask
#     db = firestore.client()
#     return upsertStudentTask(req, db)

@https_fn.on_request()
def get_courses(req: https_fn.Request) -> https_fn.Response:
    from src.get_courses import getCourses
    db = firestore.client()
    return getCourses(req, db)

@https_fn.on_request()
def get_quizzes(req: https_fn.Request) -> https_fn.Response:
    from src.get_quizzes import getQuizzes
    db = firestore.client()
    return getQuizzes(req, db)    

@https_fn.on_request()
def update_quiz(req: https_fn.Request) -> https_fn.Response:
    from src.update_quiz import updateQuiz
    db = firestore.client()
    return updateQuiz(req, db)  

@https_fn.on_request()
def get_quiz_answer(req: https_fn.Request) -> https_fn.Response:
    from src.get_quiz_answer import getQuizAnswers
    db = firestore.client()
    return getQuizAnswers(req, db)

@https_fn.on_request()
def create_quiz_answer(req: https_fn.Request) -> https_fn.Response:
    from src.create_quiz_answer import createQuizAnswer
    db = firestore.client()
    return createQuizAnswer(req, db) 

@https_fn.on_request()
def create_flashcard(req: https_fn.Request) -> https_fn.Response:
    from src.create_flashcard import createFlashcardSet
    db = firestore.client()
    return createFlashcardSet(req, db) 

@https_fn.on_request()
def get_flashcard(req: https_fn.Request) -> https_fn.Response:
    from src.get_flashcard import getFlashcards
    db = firestore.client()
    return getFlashcards(req, db) 

@https_fn.on_request()
def update_flashcard(req: https_fn.Request) -> https_fn.Response:
    from src.update_flashcards import updateFlashcards
    db = firestore.client()
    return updateFlashcards(req, db)     

@https_fn.on_request()
def create_tasks(req: https_fn.Request) -> https_fn.Response:
    from src.create_tasks import createTasks
    db = firestore.client()
    return createTasks(req, db)

@https_fn.on_request()
def create_quiz(req: https_fn.Request) -> https_fn.Response:
    from src.create_quiz import createQuiz
    db = firestore.client()
    return createQuiz(req, db)

@https_fn.on_request()
def create_course(req: https_fn.Request) -> https_fn.Response:
    from src.create_course import createCourse
    db = firestore.client()
    return createCourse(req, db)

@https_fn.on_request()
def update_course(req: https_fn.Request) -> https_fn.Response:
    from src.update_course import updateCourse
    db = firestore.client()
    return updateCourse(req, db)

@https_fn.on_request()
def get_student_profile(req: https_fn.Request) -> https_fn.Response:
    from src.get_student_profile import getStudentProfile
    db = firestore.client()
    return getStudentProfile(req, db)    

@https_fn.on_request()
def get_student_running_status(req: https_fn.Request) -> https_fn.Response:
    from src.get_student_running_status import getStudentRunningStatus
    db = firestore.client()
    return getStudentRunningStatus(req, db)  

@https_fn.on_request()
def set_student_running_status(req: https_fn.Request) -> https_fn.Response:
    from src.set_student_running_status import set_student_running_status
    db = firestore.client()
    return set_student_running_status(req, db)

@https_fn.on_request()
def update_student_running_status(req: https_fn.Request) -> https_fn.Response:
    from src.update_student_running_status import update_student_running_status
    db = firestore.client()
    return update_student_running_status(req, db)

@https_fn.on_request()
def set_student_profile(req: https_fn.Request) -> https_fn.Response:
    from src.set_student_profile import set_student_profile
    db = firestore.client()
    return set_student_profile(req, db)    

@https_fn.on_request()
def get_quiz_with_flashcards(req: https_fn.Request) -> https_fn.Response:
    from src.get_quiz_with_flashcards import getQuizAndFlashcards
    db = firestore.client()
    return getQuizAndFlashcards(req, db)       


# دالة يدوية لتجربة محرك الأولويات عبر HTTP (اختياري)
@https_fn.on_request()
def manual_task_priority_engine(req: https_fn.Request) -> https_fn.Response:
    from src.task_priority_engine import calculate_priority
    try:
        data = req.get_json(silent=True) or {}
        score, reasons = calculate_priority(data)
        return https_fn.Response(
            jsonify({"priorityScore": score, "reasons": reasons}).data,
            status=200,
            mimetype='application/json'
        )
    except Exception as e:
        return https_fn.Response(str(e), status=500)