# AI Students - API Integration Documentation

> **Author:** Hassan H Hassan

> **General Note:** All functions accept POST requests with a JSON body and return a JSON response.

## Table of Contents
1. [Task Management](#task-management)
    - [get_tasks](#get_tasks)
    - [get_task](#get_task)
    - [create_tasks](#create_tasks)
    - [update_tasks](#update_tasks)
2. [Course & Curriculum Management](#course--curriculum-management)
    - [create_curriculum](#create_curriculum)
    - [get_curriculum](#get_curriculum)
    - [get_courses](#get_courses)
    - [create_course](#create_course)
    - [update_course](#update_course)
3. [Quiz & Flashcard Management](#quiz--flashcard-management)
    - [get_quizzes](#get_quizzes)
    - [update_quiz](#update_quiz)
    - [create_quiz](#create_quiz)
    - [get_quiz_answer](#get_quiz_answer)
    - [create_quiz_answer](#create_quiz_answer)
    - [get_quiz_with_flashcards](#get_quiz_with_flashcards)
    - [create_flashcard](#create_flashcard)
    - [get_flashcard](#get_flashcard)
    - [update_flashcard](#update_flashcard)
4. [Student Profile & Status](#student-profile--status)
    - [get_student_profile](#get_student_profile)
    - [set_student_profile](#set_student_profile)
    - [get_student_running_status](#get_student_running_status)
    - [set_student_running_status](#set_student_running_status)
    - [update_student_running_status](#update_student_running_status)
5. [System Integration](#system-integration)
    - [memory_upload_to_vector_store](#memory_upload_to_vector_store)
    - [manual_task_priority_engine](#manual_task_priority_engine)

---

## Task Management

### `get_tasks`
Fetches a list of tasks for a specific student, with optional filtering by course and status. Tasks are returned sorted by priority (Priority Level first, then Priority Score descending).

**Endpoint URL:** `https://get-tasks-klhq2j3aja-uc.a.run.app`

**Request Specification:**
| Field Name | Data Type | Required | Description |
|---|---|---|---|
| `studentUid` | String | Yes | Unique identifier for the student. |
| `courseId` | String | No | Filter tasks by a specific course ID. |
| `progressStatus` | Array[String] | No | List of statuses to filter by (e.g., `["notStarted", "inProgress"]`). |
| `limit` | Integer | No | Maximum number of tasks to return. |

**Response Schema:**
- **Success Case (200):**
  ```json
  {
    "schemaVersion": "priorityTasksFlatReadable_v1",
    "tasks": [
      {
        "scheduledTaskId": "string",
        "studentUid": "string",
        "taskTitle": "string",
        "taskStatus": "string",
        "taskPriority": "string",
        "priorityScore": number,
        "..." : "..."
      }
    ]
  }
  ```

---

### `get_task`
Retrieves a single task detail by its unique `scheduledTaskId`.

**Endpoint URL:** `https://get-task-klhq2j3aja-uc.a.run.app`

**Request Specification:**
| Field Name | Data Type | Required | Description |
|---|---|---|---|
| `scheduledTaskId` | String | Yes | The unique ID of the task (usually `studentUid_taskId`). |

**Response Schema:**
- **Success Case (200):** Returns the task object wrapped in a tasks array.
- **Error Case (404):** `{"error": "Task not found"}`

**Full Practical Example:**
```json
{
  "scheduledTaskId": "STU_12345_DNA_REPLICATION_01"
}
```

---

### `create_tasks`
Generates a set of tasks for a student based on a blueprint curriculum. It flattens the curriculum's units and lessons into individual student-specific task documents.

**Endpoint URL:** `https://create-tasks-klhq2j3aja-uc.a.run.app`

**Request Specification:**
| Field Name | Data Type | Required | Description |
|---|---|---|---|
| `studentUid` | String | Yes | Unique identifier for the student. |
| `courseId` | String | Yes | The curriculum blueprint ID to use for generation. |

**Response Schema:**
- **Success Case (201):**
  ```json
  {
    "success": true,
    "course": "Biology 101",
    "student": "STU_12345",
    "tasksCreated": 12,
    "taskIds": ["STU_12345_TASK_1", "..."]
  }
  ```

---

### `update_tasks`
Allows an AI agent to update specific dynamic fields of a task during or after interaction. Only a whitelist of fields is allowed to prevent corruption of system-managed data.

**Endpoint URL:** `https://update-tasks-klhq2j3aja-uc.a.run.app`

**Request Specification:**
| Field Name | Data Type | Required | Description |
|---|---|---|---|
| `scheduledTaskId` | String | Yes | The unique ID of the task. |
| `taskStatus` | String | No | One of: `notStarted`, `inProgress`, `completed`, `cancelled`. |
| `engagementResults` | String | No | Summary of the student's performance or engagement. |
| `recentPedagogicalContext` | String | No | AI's notes on the student's learning state. |
| `taskCurrentRunningGuidance` | String | No | Active guidance provided by the AI during the task. |

**Response Schema:**
- **Success Case (200):** `{"success": true, "updatedTaskId": "...", "fields": [...]}`

**Full Practical Example:**
```json
{
  "scheduledTaskId": "STU_12345_LAB_EXP_02",
  "taskStatus": "completed",
  "engagementResults": "Student correctly identified the chemical reaction stages.",
  "recentPedagogicalContext": "Shows strength in visual observation but needs support with formula calculations."
}
```

---

## Course & Curriculum Management

### `create_curriculum`
Uploads or updates a course curriculum blueprint.

**Endpoint URL:** `https://create-curriculum-klhq2j3aja-uc.a.run.app`

**Request Specification:**
| Field Name | Data Type | Required | Description |
|---|---|---|---|
| `curriculum` | Object | Yes | The full curriculum structure. |
| `curriculum.courseId` | String | Yes | Unique ID for the course. |

**Response Schema:**
- **Success Case (210):** `{"success": true, "courseId": "..."}`

---

### `get_curriculum`
Retrieves and simplifies a course curriculum blueprint.

**Endpoint URL:** `https://get-curriculum-klhq2j3aja-uc.a.run.app`

**Request Specification:**
| Field Name | Data Type | Required | Description |
|---|---|---|---|
| `courseId` | String | Yes | The ID of the curriculum. |

**Full Practical Example:**
```json
{
  "courseId": "MATH_GEOM_101"
}
```

---

### `get_courses`
Fetches all scheduled courses assigned to a student.

**Endpoint URL:** `https://get-courses-klhq2j3aja-uc.a.run.app`

**Request Specification:**
| Field Name | Data Type | Required | Description |
|---|---|---|---|
| `studentUid` | String | Yes | Unique identifier for the student. |

---

### `create_course`
Initializes a new course for a student based on a blueprint.

**Endpoint URL:** `https://create-course-klhq2j3aja-uc.a.run.app`

**Request Specification:**
| Field Name | Data Type | Required | Description |
|---|---|---|---|
| `studentUid` | String | Yes | Unique identifier for the student. |
| `courseId` | String | Yes | The ID of the curriculum. |

---

### `update_course`
Updates mutable status and progress fields for a student's course.

**Endpoint URL:** `https://update-course-klhq2j3aja-uc.a.run.app`

**Request Specification:**
| Field Name | Data Type | Required | Description |
|---|---|---|---|
| `studentUid` | String | Yes | Student identifier. |
| `courseId` | String | Yes | Course identifier. |
| `progressStatus` | String | No | Mutable status. |

---

## Quiz & Flashcard Management

### `create_quiz`
Creates a quiz document with metadata and questions.

**Endpoint URL:** `https://us-central1-ai-students-85242.cloudfunctions.net/create_quiz`

**Request Specification:**
| Field Name | Data Type | Required | Description |
|---|---|---|---|
| `quizMeta` | Object | Yes | Metadata about the quiz. |
| `quizMeta.quizInstanceId` | String | Yes | Unique ID for the quiz. |
| `questions` | Array | Yes | List of question objects. |

**Full Practical Example:**
```json
{
  "quizMeta": {
    "quizInstanceId": "QZ_BIO_01",
    "quizName": "Cells & Organelles",
    "quizSubject": "Biology",
    "studentEmail": "hassan@example.com",
    "totalNumberOfQuestions": 1
  },
  "questions": [
    {
      "questionId": "q1",
      "text": "What is the powerhouse of the cell?",
      "options": ["Nucleus", "Mitochondria", "Ribosome"],
      "correctAnswer": "Mitochondria"
    }
  ]
}
```

---

### `get_quizzes`
Retrieves a single quiz or a list of quizzes.

**Endpoint URL:** `https://us-central1-ai-students-85242.cloudfunctions.net/get_quizzes`

---

### `update_quiz`
Updates the metadata or questions of an existing quiz.

**Endpoint URL:** `https://us-central1-ai-students-85242.cloudfunctions.net/update_quiz`

---

### `create_quiz_answer`
Submits a student's answers for a specific quiz.

**Endpoint URL:** `https://us-central1-ai-students-85242.cloudfunctions.net/create_quiz_answer`

---

### `get_quiz_answer`
Fetches quiz answers filtered by student or quiz.

**Endpoint URL:** `https://us-central1-ai-students-85242.cloudfunctions.net/get_quiz_answer`

---

### `get_quiz_with_flashcards`
Returns both the quiz content and its associated flashcards.

**Endpoint URL:** `https://get-quiz-with-flashcards-klhq2j3aja-uc.a.run.app`

---

### `create_flashcard`
Creates a dedicated flashcard set.

**Endpoint URL:** `https://us-central1-ai-students-85242.cloudfunctions.net/create_flashcard`

**Full Practical Example:**
```json
{
  "quizInstanceId": "FC_BIO_01",
  "flashcards": {
    "title": "Bio Terms",
    "cards": [{"front": "Cell", "back": "Basic unit of life"}]
  }
}
```

---

### `get_flashcard`
Retrieves flashcard sets.

**Endpoint URL:** `https://us-central1-ai-students-85242.cloudfunctions.net/get_flashcard`

---

### `update_flashcard`
Updates an existing flashcard set.

**Endpoint URL:** `https://us-central1-ai-students-85242.cloudfunctions.net/update_flashcard`

---

## Student Profile & Status

### `get_student_profile`
Looks up a student document by email.

**Endpoint URL:** `https://get-student-profile-klhq2j3aja-uc.a.run.app`

**Request Specification:**
| Field Name | Data Type | Required | Description |
|---|---|---|---|
| `email` | String | Yes | Student email address. |

---

### `set_student_profile`
Saves or updates a student profile.

**Endpoint URL:** `https://set-student-profile-klhq2j3aja-uc.a.run.app`

**Request Specification:**
| Field Name | Data Type | Required | Description |
|---|---|---|---|
| `studentUid` | String | Yes | Student identifier. |
| `profile` | Object | No | Profile fields. |

---

### `get_student_running_status`
Retrieves the student's current active state.

**Endpoint URL:** `https://get-student-running-status-klhq2j3aja-uc.a.run.app`

**Request Specification:**
| Field Name | Data Type | Required | Description |
|---|---|---|---|
| `studentUid` | String | Yes | Student identifier. |

---

### `set_student_running_status`
Saves the student's current active state.

**Endpoint URL:** `https://set-student-running-status-klhq2j3aja-uc.a.run.app`

**Request Specification:**
| Field Name | Data Type | Required | Description |
|---|---|---|---|
| `studentUid` | String | Yes | Student identifier. |
| `runningStatus` | Object | No | Status details. |

---

### `update_student_running_status`
Updates specific whitelisted fields of the student's running status.

**Endpoint URL:** `https://update_student_running_status-klhq2j3aja-uc.a.run.app`

**Request Specification:**
| Field Name | Data Type | Required | Description |
|---|---|---|---|
| `studentUid` | String | Yes | Student identifier. |
| `currentMood` | String | No | Student's current mood. |
| `availableTimeMinutes` | Integer | No | Time available for study. |
| `goalByStudent` | String | No | Goal set by the student. |
| `goalByAI` | String | No | Goal set by the AI. |
| `activityNarrative` | String | No | Description of the current activity. |
| `recentPedagogicalContext` | String | No | Educational context notes. |

---

## System Integration

### `memory_upload_to_vector_store`
Uploads text data to an OpenAI Vector Store for persistent memory.

**Endpoint URL:** `https://memory_upload_to_vector_store-klhq2j3aja-uc.a.run.app`

**Request Specification:**
| Field Name | Data Type | Required | Description |
|---|---|---|---|
| `text` | String | Yes | Text content to upload. |

**Full Practical Example:**
```json
{
  "text": "The student has completed Unit 1 of Biology and understands the basics of cell structure."
}
```

---

### `manual_task_priority_engine`
Manually triggers the priority calculation for a task without updating the database. Useful for testing logic.

**Endpoint URL:** `https://manual-task-priority-engine-klhq2j3aja-uc.a.run.app`

**Request Specification:**
| Field Name | Data Type | Required | Description |
|---|---|---|---|
| `taskPriority` | String | No | e.g., `urgent`, `high`, `normal`, `low`. |
| `dueAt` | ISO Date | No | Deadline for the task. |
| `courseTaskOrder` | Integer | No | Sequence order in the course. |

**Response Schema:**
- **Success Case (200):** `{"priorityScore": 85, "reasons": ["dueSoon"]}`

**Full Practical Example:**
```json
{
  "taskPriority": "high",
  "dueAt": "2024-04-21T18:00:00Z",
  "courseTaskOrder": 2
}
```
