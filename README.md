#  AI Students — Firebase Cloud Functions

A backend system that connects AI agents to Firestore through structured, validated Cloud Functions. Built with **Python (Flask)** on **Firebase Cloud Functions (2nd Gen)**.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [What's New](#whats-new)
- [Cloud Functions](#cloud-functions)
  - [Tasks](#tasks)
  - [Courses](#courses)
  - [Students](#students)
  - [Running Status](#running-status)
  - [Quizzes](#quizzes)
  - [Flashcards](#flashcards)
  - [Priority Engine](#priority-engine)
- [Data Schemas](#data-schemas)
- [Priority System](#priority-system)
- [Deployment](#deployment)

---

## Overview

This layer acts as a **controlled bridge** between AI agents and Firestore. Instead of letting AI access the database directly, we expose structured HTTP endpoints with validation rules and field protection.

```
User → AI Agent → MCP Tools → Cloud Functions → Firestore
```

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     AI Agent Layer                       │
│          (OpenAI Agent Builder / Custom Agent)           │
└──────────────────────┬──────────────────────────────────┘
                       │ MCP Tool Calls
┌──────────────────────▼──────────────────────────────────┐
│                    MCP Server (Node.js)                  │
│              Express + StreamableHTTP Transport          │
│                     Hosted on Cloud Run                  │
└──────────────────────┬──────────────────────────────────┘
                       │ HTTP POST Requests
┌──────────────────────▼──────────────────────────────────┐
│             Firebase Cloud Functions (Python)            │
│                  Flask · 2nd Gen · GCP                   │
└──────────────────────┬──────────────────────────────────┘
                       │ Firestore SDK
┌──────────────────────▼──────────────────────────────────┐
│                     Cloud Firestore                      │
│  tasks · courses · students · student_running_status    │
│  quizzes · quiz_answers · flashcards · courseCurriculum │
└─────────────────────────────────────────────────────────┘
```

---

## Project Structure

```
firebase_cloud_functions/
├── main.py                            # Entry point — registers all Cloud Functions
├── requirements.txt
└── src/
    ├── create_tasks.py                # Generate tasks from curriculum
    ├── get_tasks.py                   # Fetch student tasks
    ├── create_course.py               # Create a scheduled course
    ├── get_courses.py                 # Fetch courses for a student
    ├── update_course.py               # Update course fields (validated)
    ├── get_student_profile.py         # Fetch student profile by email
    ├── set_student_profile.py         # Save/update student profile      🆕
    ├── get_student_running_status.py  # Get active running status
    ├── set_student_running_status.py  # Save running status
    ├── create_quiz.py                 # Create a quiz document           🆕
    ├── update_quiz.py                 # Update quiz fields               🆕
    ├── get_quizzes.py                 # Fetch quiz by ID or list         🆕
    ├── create_quiz_answer.py          # Save student quiz answers        🆕
    ├── get_quiz_answer.py             # Fetch quiz answers               🆕
    ├── create_flashcard.py            # Create a flashcard set           🆕
    ├── update_flashcards.py           # Update flashcard set             🆕
    ├── get_flashcard.py               # Fetch flashcard by ID or list    🆕
    └── task_priority_engine.py        # Priority calculation logic       🆕
```

---

## What's New

Compared to the previous version, the following functions were **added**:

| Function | Description |
|---|---|
| `set_student_profile` | Save or update student profile document |
| `create_quiz` | Create a new quiz with questions |
| `update_quiz` | Update quiz metadata or questions |
| `get_quizzes` | Fetch a single quiz or list quizzes |
| `create_quiz_answer` | Submit student answers for a quiz |
| `get_quiz_answer` | Retrieve answers by student or quiz |
| `create_flashcard` | Create a flashcard set |
| `update_flashcard` | Update an existing flashcard set |
| `get_flashcard` | Fetch a flashcard set |
| `manual_task_priority_engine` | Manually test the priority calculation |

The following are currently **commented out** (disabled):

| Function | Status |
|---|---|
| `update_tasks` | Under revision |
| Background priority triggers | Pending re-enable after testing |

---

## Cloud Functions

All functions accept `POST` requests with a JSON body.

---

### Tasks

#### `POST /create_tasks`

Reads the course curriculum from `courseCurriculum/{courseId}` and generates `StudentSchedule-2.2` task documents in the `tasks` collection.

**Request Body:**

| Field | Type | Required | Description |
|---|---|---|---|
| `studentUid` | string | ✅ | Student identifier |
| `courseId` | string | ✅ | Must match a doc in `courseCurriculum` |
| `scheduledCourseId` | string | optional | Links task to a course dashboard |
| `timezone` | string | optional | Default: `"UTC"` |
| `weekStartAt` | ISO 8601 string | optional | Start of the week window |
| `weekEndAt` | ISO 8601 string | optional | End of the week window |

**Response:**
```json
{
  "success": true,
  "tasksCreated": 3,
  "taskIds": ["STU_0001_MATH-S1_TASK_001", "..."]
}
```

**Document ID format:** `{studentUid}_{courseId}_{taskId}`

---

#### `POST /get_tasks`

Fetches tasks for a student with optional filters and sorting.

**Request Body:**

| Field | Type | Required | Description |
|---|---|---|---|
| `studentUid` | string | ✅ | Student identifier |
| `scheduledCourseId` | string | optional | Filter by course |
| `taskStatus` | string | optional | `available` / `inProgress` / `completed` / `paused` / `skipped` |
| `sortByPriority` | boolean | optional | Default: `true` — sorts by `priorityScore` descending |
| `limit` | integer | optional | Max results to return |

**Response:**
```json
{
  "success": true,
  "tasksCount": 5,
  "tasks": [ { "scheduledTaskId": "...", "taskStatus": "available", ... } ]
}
```

---

### Courses

#### `POST /create_course`

Creates a new `ScheduledCourse-1.1` document in the `courses` collection.

**Request Body:** Full `ScheduledCourse-1.1` object.

| Field | Type | Required |
|---|---|---|
| `schemaVersion` | `"ScheduledCourse-1.1"` | ✅ |
| `scheduledCourseId` | string | ✅ |
| `studentUid` | string | ✅ |
| `courseId` | string | ✅ |
| `courseName` | string | ✅ |
| `status` | `planned/active/paused/completed/archived` | ✅ |

**Response:**
```json
{
  "success": true,
  "message": "Course created/updated successfully",
  "docId": "MATH-S1-STU_0001"
}
```

---

#### `POST /get_courses`

Fetches all course documents for a student.

**Request Body:**

| Field | Type | Required |
|---|---|---|
| `studentUid` | string | ✅ |

**Response:**
```json
{
  "success": true,
  "studentUid": "STU_0001",
  "coursesCount": 2,
  "courses": [ { ... }, { ... } ]
}
```

---

#### `POST /update_course`

Updates allowed fields on a course document. Immutable fields are rejected.

**Request Body:**

| Field | Type | Required | Description |
|---|---|---|---|
| `studentUid` | string | ✅ | |
| `courseId` | string | ✅ | |
| `scheduledTaskId` | string | optional | Use as doc ID directly |
| any allowed field | — | optional | Fields to update |

**Immutable fields (always rejected):** `studentUid`, `courseId`, `scheduledTaskId`, `schemaVersion`, `createdAt`, `generatedAt`, `taskId`, `unitId`, `lessonId`

**Response:**
```json
{
  "success": true,
  "docId": "MATH-S1-STU_0001",
  "updatedFields": ["progressStatus", "updatedAt"],
  "rejectedFields": []
}
```

---

### Students

#### `POST /get_student_profile`

Looks up a student document by email.

**Request Body:**

| Field | Type | Required |
|---|---|---|
| `email` | string | ✅ |

**Response:**
```json
{
  "success": true,
  "studentUid": "STU_0001",
  "profile": { ... }
}
```

---

#### `POST /set_student_profile` 🆕

Saves or updates a student profile. Document ID = `studentUid`.

**Request Body:**

| Field | Type | Required | Description |
|---|---|---|---|
| `studentUid` | string | ✅ | |
| `profile` | object | optional | Profile fields. If omitted, the full body is used. |

**Profile fields (all optional):**

| Field | Type |
|---|---|
| `email` | string |
| `fullName` | string |
| `displayName` | string |
| `dob` | string (YYYY-MM-DD) |
| `primaryLanguage` | string |
| `livingLocation` | string |
| `personaNarrative` | string |
| `skillsNarrative` | string |
| `studyConditionsNarrative` | string |
| `goalsNarrative` | string |
| `progressAndEngagementNarrative` | string |
| `needsReminders` | boolean |
| `needsTutorSupport` | boolean |
| `needsCoachSupport` | boolean |
| `needsParentSupport` | boolean |
| `weeklyStudyMinutesTarget` | integer |
| `weeklyPracticeMinutesTarget` | integer |
| `assessmentPassRateTargetPercent` | number |

**Immutable fields (always protected):** `studentUid`, `email`, `createdAt`

**Response:**
```json
{
  "success": true,
  "message": "Student profile saved successfully",
  "studentUid": "STU_0001"
}
```

---

### Running Status

Tracks a student's **current active state**. Collection: `student_running_status`. Document ID = `studentUid`.

#### `POST /get_student_running_status`

| Field | Type | Required |
|---|---|---|
| `studentUid` | string | ✅ |

**Response:**
```json
{
  "success": true,
  "studentUid": "STU_0001",
  "runningStatus": { "isActive": true, "activeTaskId": "TASK_001", ... }
}
```

Returns `"runningStatus": null` if no active status found.

---

#### `POST /set_student_running_status`

| Field | Type | Required | Description |
|---|---|---|---|
| `studentUid` | string | ✅ | |
| `runningStatus` | object | optional | If omitted, the full body is used |

**Response:**
```json
{
  "success": true,
  "message": "Running status saved successfully",
  "studentUid": "STU_0001"
}
```

---

### Quizzes

#### `POST /create_quiz` 🆕

Creates a quiz in the `quizzes` collection. Document ID = `quizInstanceId`.

**Request Body:**

| Field | Type | Required |
|---|---|---|
| `quizMeta` | object | ✅ |
| `quizMeta.quizInstanceId` | string | ✅ |
| `quizMeta.schemaVersion` | `"generic-1.2"` | ✅ |
| `quizMeta.assignmentName` | string | ✅ |
| `quizMeta.quizName` | string | ✅ |
| `quizMeta.quizSubject` | string | ✅ |
| `quizMeta.studentEmail` | email string | ✅ |
| `quizMeta.overallDifficultyLevel` | integer (1–5) | ✅ |
| `quizMeta.totalNumberOfQuestions` | integer | ✅ |
| `questions` | array (min 1) | ✅ |

**Response:**
```json
{
  "success": true,
  "message": "Quiz created successfully",
  "quizInstanceId": "quiz-MATH-S1-STU_0001-W01-v1"
}
```

---

#### `POST /update_quiz` 🆕

| Field | Type | Required |
|---|---|---|
| `quizMeta` | object | ✅ |
| `quizMeta.quizInstanceId` | string | ✅ |
| `questions` | array | optional |

**Response:**
```json
{
  "success": true,
  "message": "Quiz updated successfully",
  "updatedFields": ["quizMeta", "updatedAt"]
}
```

---

#### `POST /get_quizzes` 🆕

| Field | Type | Required | Description |
|---|---|---|---|
| `quizInstanceId` | string | optional | If provided, returns single quiz |
| `limit` | integer | optional | Default: `10` (for list mode) |

**Response (single):**
```json
{ "success": true, "quiz": { ... } }
```

**Response (list):**
```json
{ "success": true, "count": 5, "quizzes": [ ... ] }
```

---

#### `POST /create_quiz_answer` 🆕

| Field | Type | Required |
|---|---|---|
| `quizInstanceId` | string | ✅ |
| `studentEmail` | email string | ✅ |
| `questionAnswers` | array (min 1) | ✅ |
| `schemaVersion` | string | optional — default: `"QuizAnswers-1.0"` |

**Response:**
```json
{ "success": true, "id": "auto-generated-doc-id" }
```

---

#### `POST /get_quiz_answer` 🆕

| Field | Type | Required |
|---|---|---|
| `studentEmail` | string | optional |
| `quizInstanceId` | string | optional |

**Response:**
```json
{ "success": true, "count": 2, "data": [ ... ] }
```

---

### Flashcards

Same schema as quizzes (`quizMeta` + `questions`). Collection: `flashcards`. Document ID = `quizMeta.quizInstanceId`.

#### `POST /create_flashcard` 🆕

| Field | Type | Required |
|---|---|---|
| `quizMeta.quizInstanceId` | string | ✅ |
| `questions` | array | ✅ |

**Response:** `{ "success": true, "id": "flashcard-set-id" }`

---

#### `POST /update_flashcard` 🆕

| Field | Type | Required |
|---|---|---|
| `quizMeta.quizInstanceId` | string | ✅ |
| `questions` | array | optional |

**Response:** `{ "success": true }`

---

#### `POST /get_flashcard` 🆕

| Field | Type | Required | Description |
|---|---|---|---|
| `quizInstanceId` | string | optional | If omitted, returns all |

**Response (single):** `{ "success": true, "data": { ... } }`

**Response (all):** `{ "success": true, "count": 3, "data": [ ... ] }`

---

### Priority Engine

#### `POST /manual_task_priority_engine` 🆕

Test the priority logic without updating Firestore.

**Request Body:** Any task object with fields like `taskPriority`, `dueAt`, `courseTaskOrder`, `taskAllowSkip`, `taskLateAllowed`.

**Response:**
```json
{ "priorityScore": 87, "reasons": ["dueSoon", "lessonSequence"] }
```

---

## Data Schemas

### `tasks` — `tasksFlatReadable_v1`

| Field | Type | Description |
|---|---|---|
| `scheduledTaskId` | string | Unique ID |
| `studentUid` | string | Student identifier |
| `scheduledCourseId` | string | Links to course dashboard |
| `taskType` | string | `speakingPractice` / `quiz` / `practice` / `coachSupport` / ... |
| `taskStatus` | string | `available` / `inProgress` / `completed` / `paused` / `skipped` |
| `taskPriority` | string | `low` / `medium` / `high` / `veryHigh` / `urgent` |
| `priorityScore` | number | 0–100 |
| `isEligibleNow` | boolean | Can the student start now |
| `isOverdue` | boolean | Has the deadline passed |

### `courses` — `ScheduledCourse-1.1`

| Field | Type | Description |
|---|---|---|
| `scheduledCourseId` | string | Unique course ID |
| `status` | string | `planned/active/paused/completed/archived` |
| `courseHealthStatus` | string | `onTrack/watch/needsAttention/critical` |
| `progressPercentComplete` | number | 0–100 |
| `overdueStatus` | string | `ok/warning/critical` |

### `courseCurriculum` — `Curriculum-1.7`

Document ID = `courseId`. Blueprint read by `create_tasks`.

```json
{
  "schemaVersion": "Curriculum-1.7",
  "curriculum": {
    "courseId": "MATH-S1",
    "units": [
      { "unitId": "UNIT_001", "lessons": [
          { "lessonId": "LESSON_001", "tasks": [ { "taskId": "TASK_001", ... } ] }
      ]}
    ]
  }
}
```

---

## Priority System

### Formula

```
priority_score = (urgency × 0.45) + (importance × 0.35) + (order × 0.15) + (flags × 0.05)
```

Result × 100, capped at 100.

### Urgency

| Condition | Score |
|---|---|
| Overdue + late NOT allowed | 1.0 |
| Overdue + late allowed | 0.6 |
| 0–1 days | 0.9 |
| 2–5 days | 0.8 |
| 6–10 days | 0.6 |
| 11–14 days | 0.4 |
| 15+ days | 0.2 |
| No deadline | 0.2 |

### Importance

| `taskPriority` | Score |
|---|---|
| `urgent` | 1.0 → returns **100** immediately |
| `high` | 0.6–0.8 |
| `normal` | 0.4 |
| `low` | 0.2 |

### Flags

| Flag | Effect |
|---|---|
| `taskAllowSkip = true` | × 0.85 |
| `taskLateAllowed = true` (not yet overdue) | × 0.90 |
| Overdue task | +0.05 boost |

---

## Deployment

```bash
# Deploy all functions
firebase deploy --only functions

# Deploy a specific function
firebase deploy --only functions:create_quiz
```

**Runtime:** Python 3.13 (2nd Gen)

### Function URLs

| Function | URL |
|---|---|
| `create_tasks` | `https://create-tasks-klhq2j3aja-uc.a.run.app` |
| `get_tasks` | `https://get-tasks-klhq2j3aja-uc.a.run.app` |
| `create_course` | `https://create-course-klhq2j3aja-uc.a.run.app` |
| `get_courses` | `https://get-courses-klhq2j3aja-uc.a.run.app` |
| `update_course` | `https://update-course-klhq2j3aja-uc.a.run.app` |
| `get_student_profile` | `https://get-student-profile-klhq2j3aja-uc.a.run.app` |
| `set_student_profile` | `https://set-student-profile-klhq2j3aja-uc.a.run.app` |
| `get_student_running_status` | `https://get-student-running-status-klhq2j3aja-uc.a.run.app` |
| `set_student_running_status` | `https://set-student-running-status-klhq2j3aja-uc.a.run.app` |
| `manual_task_priority_engine` | `https://manual-task-priority-engine-klhq2j3aja-uc.a.run.app` |
| `create_quiz` | `https://us-central1-ai-students-85242.cloudfunctions.net/create_quiz` |
| `update_quiz` | `https://us-central1-ai-students-85242.cloudfunctions.net/update_quiz` |
| `get_quizzes` | `https://us-central1-ai-students-85242.cloudfunctions.net/get_quizzes` |
| `create_quiz_answer` | `https://us-central1-ai-students-85242.cloudfunctions.net/create_quiz_answer` |
| `get_quiz_answer` | `https://us-central1-ai-students-85242.cloudfunctions.net/get_quiz_answer` |
| `create_flashcard` | `https://us-central1-ai-students-85242.cloudfunctions.net/create_flashcard` |
| `update_flashcard` | `https://us-central1-ai-students-85242.cloudfunctions.net/update_flashcard` |
| `get_flashcard` | `https://us-central1-ai-students-85242.cloudfunctions.net/get_flashcard` |
