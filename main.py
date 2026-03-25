from firebase_functions import https_fn
import firebase_admin
from firebase_admin import firestore

if not firebase_admin._apps:
    firebase_admin.initialize_app()

@https_fn.on_request()
def get_tasks(req: https_fn.Request) -> https_fn.Response:
    from src.get_tasks import getTasks
    db = firestore.client()
    return getTasks(req, db)

@https_fn.on_request()
def update_tasks(req: https_fn.Request) -> https_fn.Response:
    from src.update_tasks import upsertStudentTask
    db = firestore.client()
    return upsertStudentTask(req, db)


@https_fn.on_request()
def get_courses(req: https_fn.Request) -> https_fn.Response:
      from src.get_courses import getCourses
      db = firestore.client()
      return getCourses(req, db)


@https_fn.on_request()
def create_tasks(req: https_fn.Request) -> https_fn.Response:
    from src.create_tasks import createTasks

    db = firestore.client()

    return createTasks(req, db)


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