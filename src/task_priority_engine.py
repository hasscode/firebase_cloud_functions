import math
from datetime import datetime, timezone, timedelta
from firebase_admin import firestore
from firebase_functions import firestore_fn, scheduler_fn

# 1. الإعدادات (Weights)
IMPORTANCE_WEIGHTS = {
    "very_critical": 1.0,
    "critical": 0.8,
    "high": 0.6,
    "normal": 0.4,
    "low": 0.2,
}

# 2. الدوال المساعدة (Helpers)
def map_priority(task_priority: str) -> str:
    mapping = {
        "urgent": "very_critical",
        "high": "high",
        "normal": "normal",
        "low": "low"
    }
    return mapping.get(task_priority, "normal")

def get_urgency_score(days_to_deadline: int, task_late_allowed: bool) -> float:
    if days_to_deadline < 0:
        return 0.6 if task_late_allowed else 1.0
    if days_to_deadline == 0: return 0.9
    if days_to_deadline <= 2: return 0.8
    if days_to_deadline <= 5: return 0.6
    if days_to_deadline <= 10: return 0.4
    return 0.2

def get_order_score(order: int) -> float:
    #
    return max(0.5, 1 / (1 + math.exp(0.35 * (order - 6))))

def get_flags_modifier(task: dict, days_to_deadline: int) -> float:
    if days_to_deadline <= 1:
        return 1.0
    modifier = 1.0
    if task.get("taskAllowSkip"): modifier *= 0.85
    if task.get("taskLateAllowed"): modifier *= 0.90
    return modifier

# 3. المحرك الرئيسي للحساب (Core Engine)
def calculate_priority(task: dict):
    mapped_priority = map_priority(task.get("taskPriority", "normal"))

    if mapped_priority == "very_critical":
        return 100, ["manualBoost"]

    now = datetime.now(timezone.utc)
    due_at = task.get("dueAt")
    
 
    days_to_deadline = None
    if due_at:
        if isinstance(due_at, str):
            due = datetime.fromisoformat(due_at.replace('Z', '+00:00'))
        else:
            due = due_at 
        
        delta = due - now
        days_to_deadline = math.ceil(delta.total_seconds() / (24 * 3600))

    importance = IMPORTANCE_WEIGHTS.get(mapped_priority, 0.4)
    urgency = get_urgency_score(days_to_deadline, task.get("taskLateAllowed", False)) if days_to_deadline is not None else 0.2
    order = get_order_score(task.get("courseTaskOrder", 1))
    flags = get_flags_modifier(task, days_to_deadline) if days_to_deadline is not None else 1.0

 
    score = (urgency * 0.45) + (importance * 0.35) + (order * 0.15) + (flags * 0.05)
    
    if days_to_deadline is not None and days_to_deadline < 0:
        score += 0.05

    final_score = min(1.0, score)
    
    reasons = []
    if days_to_deadline is not None:
        if days_to_deadline < 0: reasons.append("overdue")
        elif days_to_deadline <= 2: reasons.append("dueSoon")
    
    if task.get("courseTaskOrder", 100) <= 3:
        reasons.append("lessonSequence")

    return round(final_score * 100), reasons

# 4. معالج البيانات الضخمة (Paginated Processor)
async def process_tasks_with_pagination(db):
    query = db.collection("tasks").where("progressStatus", "in", ["notStarted", "inProgress"])
    PAGE_SIZE = 500
    last_doc = None

    while True:
        current_query = query.limit(PAGE_SIZE)
        if last_doc:
            current_query = current_query.start_after(last_doc)
        
        docs = current_query.get()
        if not docs:
            break

        batch = db.batch()
        for doc in docs:
            task_data = doc.to_dict()
            score, reasons = calculate_priority(task_data)
            
            batch.update(doc.reference, {
                "priorityScore": score,
                "priorityReasonCodes": reasons,
                "priorityLastCalculatedAt": firestore.SERVER_TIMESTAMP
            })

        batch.commit()
        print(f"Processed {len(docs)} tasks")
        
        if len(docs) < PAGE_SIZE:
            break
        last_doc = docs[-1]


@firestore_fn.on_document_created(document="tasks/{taskId}")
def on_task_create(event: firestore_fn.Event[firestore_fn.DocumentSnapshot]):
    task_data = event.data.to_dict()
    score, reasons = calculate_priority(task_data)
    event.data.reference.update({
        "priorityScore": score,
        "priorityReasonCodes": reasons,
        "priorityLastCalculatedAt": firestore.SERVER_TIMESTAMP
    })

@firestore_fn.on_document_updated(document="tasks/{taskId}")
def on_task_update(event: firestore_fn.Event[firestore_fn.Change[firestore_fn.DocumentSnapshot]]):
    before = event.data.before.to_dict()
    after = event.data.after.to_dict()

    
    changed = (before.get("taskPriority") != after.get("taskPriority") or 
               before.get("dueAt") != after.get("dueAt") or 
               before.get("courseTaskOrder") != after.get("courseTaskOrder"))

    if not changed or after.get("progressStatus") in ["completed", "skipped"]:
        return

    score, reasons = calculate_priority(after)
    event.data.after.reference.update({
        "priorityScore": score,
        "priorityReasonCodes": reasons,
        "priorityLastCalculatedAt": firestore.SERVER_TIMESTAMP
    })

@scheduler_fn.on_schedule(schedule="0 0 * * *", timezone="Africa/Cairo")
def recalculate_all_tasks_daily(event: scheduler_fn.ScheduledEvent):
    db = firestore.client()
    import asyncio
    asyncio.run(process_tasks_with_pagination(db))
    print("Daily priority recalculation done")