#  AI Students — Cloud Functions & MCP Tools Layer

A backend system that connects AI agents to Firestore through structured, validated Cloud Functions. Built with **Python (Flask)** on **Firebase Cloud Functions (2nd Gen)** and exposed to AI agents via an **MCP (Model Context Protocol) server**.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Cloud Functions](#cloud-functions)
  - [Tasks](#tasks)
  - [Courses](#courses)
  - [Students](#students)
  - [Running Status](#running-status)
- [MCP Server](#mcp-server)
- [Data Schemas](#data-schemas)
- [Priority System](#priority-system)
- [Deployment](#deployment)
- [Environment Variables](#environment-variables)

---

## Overview

This layer acts as a **controlled bridge** between AI agents and Firestore. Instead of letting AI access the database directly, we expose structured tools with validation rules and field protection.

```
User → AI Agent → MCP Tools → Cloud Functions → Firestore
```

**Why this approach?**
- AI understands available actions through structured tool definitions
- Incoming data is validated (required fields, enums, immutable field protection)
- Database operations are auditable and consistent
- Schema is enforced at the function level

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
│              Express + StreamableHTTP Transport           │
│                     Hosted on Cloud Run                  │
└──────────────────────┬──────────────────────────────────┘
                       │ HTTP Requests
┌──────────────────────▼──────────────────────────────────┐
│             Firebase Cloud Functions (Python)            │
│                  Flask · 2nd Gen · GCP                   │
│                                                          │
│   get_tasks  create_tasks  update_tasks                  │
│   get_courses  create_course  update_course              │
│   get_student_profile  get/set_student_running_status    │
└──────────────────────┬──────────────────────────────────┘
                       │ Firestore SDK
┌──────────────────────▼──────────────────────────────────┐
│                  Cloud Firestore                         │
│   tasks · courses · students · student_running_status   │
│   courseCurriculum · courseCurriculum                    │
└─────────────────────────────────────────────────────────┘
```

---

## Project Structure

```
functions/
├── main.py                        # Entry point — registers all Cloud Functions
└── src/
    ├── create_tasks.py            # Generate tasks from curriculum
    ├── get_tasks.py               # Fetch student tasks
    ├── update_tasks.py            # Update task fields (validated)
    ├── create_course.py           # Create a scheduled course document
    ├── get_courses.py             # Fetch courses for a student
    ├── update_course.py           # Update course fields (validated)
    ├── get_student_profile.py     # Fetch student profile by email
    ├── get_student_running_status.py  # Get active running status
    └── set_student_running_status.py  # Save running status

mcp-server/
└── index.js                       # MCP server — exposes all tools to AI agents
```

---

## Cloud Functions

All functions are registered in `main.py` and use the **Firebase Functions Python SDK (2nd Gen)**.

### Tasks

#### `POST /create_tasks`

Reads the course curriculum from `courseCurriculum/{courseId}` and generates `StudentSchedule-2.2` task documents in the `tasks` collection.

**Request Body:**
```json
{
  "studentUid": "STU_0001",
  "courseId": "MATH-S1",
  "scheduledCourseId": "MATH-S1-STU_0001",
  "timezone": "Africa/Cairo",
  "weekStartAt": "2026-03-17T00:00:00Z",
  "weekEndAt": "2026-03-23T23:59:59Z"
}
```

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

Fetches tasks for a student with optional filters.

**Request Body:**
```json
{
  "studentUid": "STU_0001",
  "courseId": "MATH-S1",
  "progressStatus": "notStarted"
}
```

**Filters:**
| Field | Required | Description |
|---|---|---|
| `studentUid` | ✅ | Student identifier |
| `courseId` | optional | Filter by course |
| `progressStatus` | optional | `notStarted` / `inProgress` / `completed` / `blocked` / `skipped` |

---

#### `POST /update_tasks`

Updates allowed fields on a task document. Immutable fields are rejected.

**Request Body:**
```json
{
  "studentUid": "STU_0001",
  "taskId": "TASK_001",
  "courseId": "MATH-S1",
  "progressStatus": "inProgress",
  "progressStartedAt": "2026-03-17T09:05:00Z"
}
```

**Document lookup priority:**
1. `scheduledTaskId` (if provided)
2. `{studentUid}_{courseId}_{taskId}` (fallback)

**Allowed fields (subset):**
```
progressStatus, progressStartedAt, progressCompletedAt,
taskPriority, priorityScore, priorityReasonCodes,
agentChatSessionId, agentChatStatus, quizInstanceId, ...
```

**Immutable fields (always rejected):**
```
schemaVersion, scheduledTaskId, studentUid,
courseId, taskId, unitId, lessonId, createdAt, generatedAt
```

---

### Courses

#### `POST /create_course`

Creates a new `ScheduledCourse-1.1` document in the `courses` collection.

**Request Body:** Full `ScheduledCourse-1.1` object.

**Document ID format:** `scheduledCourseId` or `{studentUid}_{courseId}`

---

#### `POST /get_courses`

Fetches all course documents for a student.

**Request Body:**
```json
{
  "studentUid": "STU_0001"
}
```

---

#### `POST /update_course`

Updates allowed fields on a course document with immutable field protection.

**Request Body:**
```json
{
  "studentUid": "STU_0001",
  "courseId": "MATH-S1",
  "progressStatus": "active",
  "coursePriorityScore": 85.0
}
```

---

### Students

#### `POST /get_student_profile`

Looks up a student document by email.

**Request Body:**
```json
{
  "email": "student@example.com"
}
```

**Response:**
```json
{
  "success": true,
  "studentUid": "STU_0001",
  "profile": { ... }
}
```

---

### Running Status

The `student_running_status` collection tracks a student's **current active state** — which task they are on, what agent is active, etc.

#### `POST /get_student_running_status`

Returns the active running status for a student.

**Request Body:**
```json
{
  "studentUid": "STU_0001"
}
```

**Response:**
```json
{
  "success": true,
  "studentUid": "STU_0001",
  "runningStatus": {
    "isActive": true,
    "activeTaskId": "TASK_001",
    ...
  }
}
```

---

#### `POST /set_student_running_status`

Saves or overwrites the running status for a student. Document ID = `studentUid`.

**Request Body:**
```json
{
  "studentUid": "STU_0001",
  "runningStatus": {
    "isActive": true,
    "activeTaskId": "TASK_001",
    "activeCourseId": "MATH-S1"
  }
}
```

---

## MCP Server

The MCP server (`mcp-server/index.js`) runs on **Cloud Run** and exposes all Cloud Functions as structured AI tools.

**Registered tools:**

| Tool | Maps to |
|---|---|
| `get_tasks` | `GET_TASKS` |
| `create_tasks` | `CREATE_TASKS` |
| `update_task` | `UPDATE_TASK` |
| `get_course` | `GET_COURSE` |
| `create_course` | `CREATE_COURSE` |
| `update_course` | `UPDATE_COURSE` |
| `get_student` | `GET_STUDENT_BASE` |
| `upsert_student` | `UPSERT_STUDENT_URL` |
| `save_course_curriculum` | Direct Firestore write |
| `get_student_learning_context` | Direct Firestore read |

**Session management:** Each `initialize` request creates a new isolated session with its own transport and MCP server instance. Sessions are cleaned up after 1 hour of inactivity.

**Allowed origins:**
```
https://chatgpt.com
https://platform.openai.com
```

---

## Data Schemas

### `tasks` collection — `StudentSchedule-2.2`

| Field | Type | Description |
|---|---|---|
| `scheduledTaskId` | string | Unique task ID — `{studentUid}_{courseId}_{taskId}` |
| `studentUid` | string | Student identifier |
| `courseId` | string | Course identifier |
| `taskType` | enum | `lectureVideo` / `explorationChat` / `quiz` / `reviewPractice` / ... |
| `taskPriority` | enum | `low` / `normal` / `high` / `urgent` |
| `progressStatus` | enum | `notStarted` / `inProgress` / `completed` / `blocked` / `skipped` |
| `priorityScore` | number | 0–100, computed automatically |
| `priorityReasonCodes` | array | e.g. `["dueSoon", "examSoon"]` |
| `dueAt` | string (ISO 8601) | Task deadline |
| `startAt` | string (ISO 8601) | When task becomes available |

### `courses` collection — `ScheduledCourse-1.1`

| Field | Type | Description |
|---|---|---|
| `scheduledCourseId` | string | Unique course ID — `{courseId}-{studentUid}` |
| `studentUid` | string | Student identifier |
| `status` | enum | `planned` / `active` / `paused` / `completed` / `archived` |
| `courseHealthStatus` | enum | `onTrack` / `watch` / `needsAttention` / `critical` |
| `progressPercentComplete` | number | 0–100 |
| `overdueStatus` | enum | `ok` / `warning` / `critical` |

### `courseCurriculum` collection — `Curriculum-1.7`

Document ID = `courseId`. Contains the full curriculum blueprint read by `create_tasks`.

```json
{
  "schemaVersion": "Curriculum-1.7",
  "curriculum": {
    "courseId": "MATH-S1",
    "units": [
      {
        "unitId": "UNIT_001",
        "lessons": [
          {
            "lessonId": "LESSON_001",
            "tasks": [ { "taskId": "TASK_001", ... } ]
          }
        ]
      }
    ]
  }
}
```

---

## Priority System

Task priority is calculated automatically via **Firebase Cloud Functions triggers** and a **daily scheduled function**.

### Formula

```
priority_score = (urgency × 0.45) + (importance × 0.35) + (order × 0.15) + (flags × 0.05)
```

### Urgency (based on `dueAt`)

| Days to deadline | Score |
|---|---|
| Overdue + late NOT allowed | 1.0 |
| Overdue + late allowed | 0.6 |
| 0–1 days | 0.9 |
| 2–5 days | 0.8 |
| 6–10 days | 0.6 |
| 11–14 days | 0.4 |
| 15+ days | 0.2 |

### Importance (based on `taskPriority`)

| Priority | Score |
|---|---|
| `urgent` (very_critical) | 1.0 → score = 100 immediately |
| `high` (critical) | 0.8 |
| `high` | 0.6 |
| `normal` | 0.4 |
| `low` | 0.2 |

### Triggers

**Scheduled:** Runs daily at **12:00 AM Cairo time** — recalculates all `notStarted` and `inProgress` tasks.

**Real-time:** Fires immediately when `taskPriority`, `dueAt`, or `courseTaskOrder` changes on any task document.

---

## Deployment

```bash
# Deploy all functions
firebase deploy --only functions

# Deploy a specific function
firebase deploy --only functions:create_tasks
```

**Runtime:** Python 3.13 (2nd Gen)

**Function URLs after deploy:**
```
create_tasks  → https://create-tasks-<hash>-uc.a.run.app
get_tasks     → https://get-tasks-<hash>-uc.a.run.app
update_tasks  → https://update-tasks-<hash>-uc.a.run.app
update_course → https://update-course-<hash>-uc.a.run.app
create_course → https://us-central1-<project>.cloudfunctions.net/create_course
get_courses   → https://us-central1-<project>.cloudfunctions.net/get_courses
```

---

## Environment Variables

For the **MCP server** (`mcp-server/`):

| Variable | Description |
|---|---|
| `PORT` | Server port (default: `8080`) |
| `UPSTASH_REDIS_REST_URL` | Redis URL for session caching (optional) |
| `UPSTASH_REDIS_REST_TOKEN` | Redis auth token (optional) |
| `MCP_DEBUG` | Set to `"1"` to enable verbose session logging |
| `SESSION_WINDOW_SIZE` | Max messages per session cache (default: `20`) |
| `SESSION_TTL_SECONDS` | Session cache TTL (default: `86400`) |
| `DEDUPE_WINDOW_MS` | Duplicate call window in ms (default: `5000`) |

---

## Notes

- **Validation:** All update functions filter incoming fields against an `ALLOWED_FIELDS` set. Fields in `IMMUTABLE_FIELDS` are silently rejected and returned in `rejectedFields`.
- **Batching:** `create_tasks` uses Firestore batch writes for efficiency.
- **Schema version:** All task documents use `schemaVersion: "StudentSchedule-2.2"`. Course documents use `schemaVersion: "ScheduledCourse-1.1"`.
- **MCP transport:** Uses `StreamableHTTPServerTransport` — each session is isolated with its own server instance.
