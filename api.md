# API Requirements

# LegalEase AI - API Specification

---

# Purpose

The API layer provides communication between the frontend, AI Agent, database, and external AI services.

All APIs must follow RESTful principles and return JSON responses.

---

# API Design Principles

All APIs must:

- Follow REST architecture.
- Use HTTPS.
- Return JSON responses.
- Validate every request.
- Handle all exceptions gracefully.
- Return meaningful HTTP status codes.
- Be versioned.
- Be stateless.
- Be secure.

Base URL

/api/v1/

---

# Authentication

Authentication Method

JWT Authentication

Protected APIs require:

Authorization: Bearer <JWT_TOKEN>

Public APIs:

- User Registration
- User Login
- Health Check

All other APIs require authentication.

---

# Standard Response Format

Successful Response

```json
{
    "success": true,
    "message": "Request completed successfully",
    "data": {}
}
```

Error Response

```json
{
    "success": false,
    "message": "Validation failed",
    "errors": []
}
```

---

# Authentication APIs

## Register User

POST

/auth/register

Purpose

Create a new user account.

Required Data

- Full Name
- Email
- Password

Validation

- Email must be unique.
- Password must meet security requirements.

---

## Login

POST

/auth/login

Purpose

Authenticate user.

Returns

- JWT Access Token
- User Information

---

## Logout

POST

/auth/logout

Purpose

Invalidate user session.

Authentication Required

Yes

---

# User APIs

## Get User Profile

GET

/users/profile

Purpose

Retrieve logged-in user's profile.

Authentication Required

Yes

---

## Update User Profile

PUT

/users/profile

Purpose

Update user information.

Authentication Required

Yes

---

# Consumer Case APIs

## Create Consumer Case

POST

/cases

Purpose

Create a new consumer case.

Required Data

- Issue Title
- Issue Description
- Category
- Product or Service
- Purchase Date (optional)
- Seller Name (optional)

Returns

- Case ID

---

## Get Consumer Cases

GET

/cases

Purpose

Retrieve all consumer cases created by the user.

---

## Get Consumer Case

GET

/cases/{case_id}

Purpose

Retrieve a specific case.

---

## Update Consumer Case

PUT

/cases/{case_id}

Purpose

Update consumer case details.

---

## Delete Consumer Case

DELETE

/cases/{case_id}

Purpose

Delete a consumer case.

---

# AI Conversation APIs

## Start AI Conversation

POST

/agent/start

Purpose

Start a new AI conversation.

Returns

- Conversation ID
- Initial AI Greeting

---

## Send Message to AI

POST

/agent/chat

Purpose

Send a user message to the AI Agent.

Request

- Conversation ID
- User Message

AI Responsibilities

- Understand issue
- Ask follow-up questions
- Retrieve legal knowledge
- Guide user

Returns

- AI Response
- Conversation Status

---

## End Conversation

POST

/agent/end

Purpose

Close conversation.

Returns

- Final Conversation Status

---

# Roadmap APIs

## Generate Resolution Roadmap

POST

/roadmap/generate

Purpose

Generate a personalized consumer resolution roadmap.

Returns

- Step-by-step roadmap
- Recommended actions

---

## Get Generated Roadmap

GET

/roadmap/{case_id}

Purpose

Retrieve an existing roadmap.

---

# Evidence APIs

## Generate Evidence Checklist

POST

/evidence/generate

Purpose

Generate a personalized evidence checklist.

Returns

- Required documents
- Optional supporting evidence

---

## Get Evidence Checklist

GET

/evidence/{case_id}

Purpose

Retrieve evidence checklist.

---

# Consumer Report APIs

## Generate Consumer Report

POST

/report/generate

Purpose

Generate the final consumer guidance report.

Returns

- Case Summary
- Consumer Rights
- Resolution Roadmap
- Evidence Checklist
- Suggested Next Actions

---

## Download Consumer Report

GET

/report/{case_id}

Purpose

Download the generated report.

Supported Formats

- PDF

---

# Knowledge Base APIs

## Search Legal Knowledge

GET

/knowledge/search

Purpose

Retrieve relevant legal information.

Parameters

- Query
- Category

Returns

- Relevant legal sections
- Consumer guidance

---

# Health Check API

GET

/health

Purpose

Verify server health.

Returns

- Server Status
- Database Status
- AI Service Status

---

# Validation Rules

Every API must validate:

- Required fields
- Input format
- Data types
- Authentication
- Authorization
- Request size

Reject invalid requests.

---

# HTTP Status Codes

200 OK

201 Created

400 Bad Request

401 Unauthorized

403 Forbidden

404 Not Found

409 Conflict

422 Validation Error

500 Internal Server Error

503 Service Unavailable

---

# Error Handling

Every API must:

- Return meaningful error messages.
- Never expose internal server details.
- Log unexpected errors.
- Handle invalid inputs safely.
- Return consistent error structures.

---

# Security Requirements

All APIs must:

- Require HTTPS.
- Validate JWT tokens.
- Hash passwords.
- Prevent SQL Injection.
- Prevent XSS attacks.
- Sanitize user inputs.
- Implement rate limiting.
- Never expose API keys.

---

# Performance Requirements

APIs should:

- Return responses quickly.
- Use asynchronous processing where appropriate.
- Minimize unnecessary database queries.
- Support pagination for large datasets.
- Cache frequently accessed knowledge if needed.

---

# API Documentation

Every API must include:

- Endpoint
- HTTP Method
- Purpose
- Authentication Requirement
- Request Parameters
- Response Format
- Error Responses
- Example Request
- Example Response

---

# API Success Criteria

The API layer is considered complete when:

- All endpoints are implemented.
- Authentication is secure.
- Validation is complete.
- Error handling is consistent.
- APIs pass unit and integration tests.
- API documentation is complete.
- All endpoints are production-ready.