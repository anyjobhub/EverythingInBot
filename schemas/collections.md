# MongoDB Collections Schema

This document describes the MongoDB collections used in EverythingInBot.

## Collections Overview

### 1. users
**Purpose**: Store user profiles and subscription information

**Schema**:
```javascript
{
  _id: ObjectId,
  telegram_id: Number (unique, indexed),
  username: String,
  first_name: String,
  last_name: String,
  tier: String, // "guest", "free", "pro"
  total_requests: Number,
  daily_requests: Number,
  last_request_date: Date,
  created_at: Date (indexed),
  last_active: Date,
  language: String,
  notifications_enabled: Boolean
}
```

**Indexes**:
- `telegram_id` (unique)
- `tier`
- `created_at`

---

### 2. subscriptions
**Purpose**: Track payment history and active subscriptions

**Schema**:
```javascript
{
  _id: ObjectId,
  user_id: Number, // telegram_id
  tier: String, // "pro"
  status: String, // "active", "expired", "cancelled"
  payment_method: String, // "telegram_stars", "razorpay", "stripe"
  amount: Number,
  currency: String,
  transaction_id: String,
  started_at: Date,
  expires_at: Date (indexed),
  created_at: Date
}
```

**Indexes**:
- `user_id` + `status`
- `expires_at`

---

### 3. courses
**Purpose**: Store course content

**Schema**:
```javascript
{
  _id: ObjectId,
  title: String,
  description: String,
  category: String (indexed), // "hacking", "security", "programming", etc.
  thumbnail_url: String,
  published: Boolean (indexed),
  lessons: Array, // Array of lesson IDs
  total_lessons: Number,
  duration_hours: Number,
  difficulty: String, // "beginner", "intermediate", "advanced"
  created_at: Date,
  updated_at: Date
}
```

**Indexes**:
- `category`
- `published`
- `category` + `published`

---

### 4. lessons
**Purpose**: Individual lesson content

**Schema**:
```javascript
{
  _id: ObjectId,
  course_id: ObjectId,
  title: String,
  content: String, // Markdown or HTML
  video_url: String,
  pdf_url: String,
  order: Number,
  duration_minutes: Number,
  created_at: Date
}
```

---

### 5. user_progress
**Purpose**: Track user course progress

**Schema**:
```javascript
{
  _id: ObjectId,
  user_id: Number,
  course_id: ObjectId,
  completed_lessons: Array, // Array of lesson IDs
  progress_percentage: Number,
  last_accessed: Date,
  started_at: Date,
  completed_at: Date
}
```

**Indexes**:
- `user_id` + `course_id` (unique)

---

### 6. jobs
**Purpose**: Job listings

**Schema**:
```javascript
{
  _id: ObjectId,
  title: String,
  company: String,
  category: String (indexed), // "it", "non_it", "government", "internship", "remote"
  location: String (indexed),
  description: String,
  requirements: Array,
  salary_range: String,
  job_type: String, // "full_time", "part_time", "contract"
  apply_url: String,
  active: Boolean (indexed),
  posted_at: Date (indexed),
  expires_at: Date,
  created_at: Date
}
```

**Indexes**:
- `category` + `location`
- `posted_at` (descending)
- `active`

---

### 7. applications
**Purpose**: User job applications

**Schema**:
```javascript
{
  _id: ObjectId,
  user_id: Number,
  job_id: ObjectId,
  resume_id: ObjectId,
  cover_letter: String,
  status: String, // "applied", "viewed", "shortlisted", "rejected"
  applied_at: Date,
  updated_at: Date
}
```

---

### 8. resumes
**Purpose**: AI-generated resumes

**Schema**:
```javascript
{
  _id: ObjectId,
  user_id: Number,
  title: String,
  pdf_url: String,
  data: Object, // Resume data (name, experience, skills, etc.)
  created_at: Date
}
```

---

### 9. todos
**Purpose**: User to-do items

**Schema**:
```javascript
{
  _id: ObjectId,
  user_id: Number,
  title: String,
  description: String,
  completed: Boolean,
  priority: String, // "low", "medium", "high"
  due_date: Date,
  created_at: Date,
  completed_at: Date
}
```

---

### 10. notes
**Purpose**: User notes

**Schema**:
```javascript
{
  _id: ObjectId,
  user_id: Number,
  title: String,
  content: String,
  tags: Array,
  created_at: Date,
  updated_at: Date
}
```

---

### 11. habits
**Purpose**: Habit tracking

**Schema**:
```javascript
{
  _id: ObjectId,
  user_id: Number,
  name: String,
  frequency: String, // "daily", "weekly"
  streak: Number,
  last_completed: Date,
  created_at: Date
}
```

---

### 12. reminders
**Purpose**: Scheduled reminders

**Schema**:
```javascript
{
  _id: ObjectId,
  user_id: Number,
  message: String,
  scheduled_at: Date,
  sent: Boolean,
  created_at: Date
}
```

---

### 13. tool_usage
**Purpose**: Track tool usage for analytics

**Schema**:
```javascript
{
  _id: ObjectId,
  user_id: Number (indexed),
  tool_name: String (indexed),
  module: String, // "m1_ai", "m5_tools", etc.
  timestamp: Date (indexed),
  metadata: Object // Tool-specific data
}
```

**Indexes**:
- `user_id` + `tool_name`
- `timestamp` (descending)

---

### 14. osint_history
**Purpose**: OSINT query history (with consent)

**Schema**:
```javascript
{
  _id: ObjectId,
  user_id: Number,
  query_type: String, // "whois", "dns", "ip", etc.
  query: String,
  result: Object,
  timestamp: Date,
  consent_given: Boolean
}
```

---

### 15. breach_checks
**Purpose**: Breach check history

**Schema**:
```javascript
{
  _id: ObjectId,
  user_id: Number,
  check_type: String, // "email", "password"
  email: String, // Only for email checks
  result: Object,
  timestamp: Date
}
```

---

### 16. analytics
**Purpose**: General analytics and events

**Schema**:
```javascript
{
  _id: ObjectId,
  event_type: String (indexed), // "command", "callback", "error", etc.
  user_id: Number,
  data: Object,
  timestamp: Date (indexed)
}
```

**Indexes**:
- `event_type`
- `timestamp` (descending)

---

## Index Creation Commands

Run these in MongoDB shell or MongoDB Compass:

```javascript
// Users
db.users.createIndex({ "telegram_id": 1 }, { unique: true })
db.users.createIndex({ "tier": 1 })
db.users.createIndex({ "created_at": -1 })

// Subscriptions
db.subscriptions.createIndex({ "user_id": 1, "status": 1 })
db.subscriptions.createIndex({ "expires_at": -1 })

// Courses
db.courses.createIndex({ "category": 1 })
db.courses.createIndex({ "published": 1 })
db.courses.createIndex({ "category": 1, "published": 1 })

// Jobs
db.jobs.createIndex({ "category": 1, "location": 1 })
db.jobs.createIndex({ "posted_at": -1 })
db.jobs.createIndex({ "active": 1 })

// User Progress
db.user_progress.createIndex({ "user_id": 1, "course_id": 1 }, { unique: true })

// Tool Usage
db.tool_usage.createIndex({ "user_id": 1, "tool_name": 1 })
db.tool_usage.createIndex({ "timestamp": -1 })

// Analytics
db.analytics.createIndex({ "event_type": 1 })
db.analytics.createIndex({ "timestamp": -1 })
```
