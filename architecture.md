# System Architecture

# LegalEase AI - System Architecture

---

# Purpose

This document defines the overall architecture of LegalEase AI.

It explains how the frontend, backend, AI Agent, knowledge base, database, and external services work together to provide an intelligent consumer rights assistance platform.

The architecture must be modular, scalable, secure, and maintainable.

---

# Architecture Style

LegalEase AI follows a Layered Architecture combined with an Agentic AI workflow.

The system consists of:

- Presentation Layer
- Application Layer
- AI Agent Layer
- Knowledge Layer
- Data Layer
- External Services Layer

Each layer has a single responsibility.

---

# High-Level Architecture

User

↓

Frontend (React)

↓

Backend API (FastAPI)

↓

AI Agent (LangGraph)

↓

Knowledge Retrieval (RAG)

↓

Knowledge Base (ChromaDB)

↓

Gemini API

↓

Response Generation

↓

Backend

↓

Frontend

↓

User

---

# System Components

## Presentation Layer

Responsibilities

- User Authentication
- Consumer Case Creation
- AI Chat Interface
- Resolution Roadmap Display
- Evidence Checklist Display
- Consumer Report Display
- User Dashboard

The presentation layer must never contain business logic.

---

## Backend Layer

Responsibilities

- Authentication
- Authorization
- API Management
- Business Logic
- Validation
- Database Communication
- AI Agent Communication
- Report Generation
- Error Handling

The backend acts as the central coordinator.

---

## AI Agent Layer

The AI Agent is the core intelligence of the system.

Responsibilities

- Understand user intent
- Classify consumer issues
- Ask follow-up questions
- Collect missing information
- Retrieve legal knowledge
- Analyze consumer rights
- Generate personalized guidance
- Produce consumer reports

The AI Agent must never skip information gathering.

---

# AI Agent Workflow

The AI Agent follows this sequence.

Start Conversation

↓

Understand User Problem

↓

Identify Consumer Issue

↓

Ask Follow-up Questions

↓

Collect Missing Information

↓

Validate Information

↓

Retrieve Legal Knowledge

↓

Analyze Consumer Rights

↓

Educate Consumer

↓

Generate Resolution Roadmap

↓

Generate Evidence Checklist

↓

Recommend Consumer Authority

↓

Generate Consumer Report

↓

End Conversation

---

# Knowledge Layer

The Knowledge Layer provides verified legal information.

Knowledge Sources

- Consumer Protection Act, 2019
- Consumer Protection Rules
- Consumer Protection (E-Commerce) Rules
- Department of Consumer Affairs
- National Consumer Helpline

Only verified legal information may be used.

---

# Retrieval-Augmented Generation (RAG)

The AI must never rely solely on the language model.

Workflow

User Question

↓

Convert Query

↓

Retrieve Relevant Knowledge

↓

Rank Retrieved Results

↓

Provide Context to Gemini

↓

Generate Response

↓

Return Verified Answer

---

# Vector Database

Responsibilities

- Store legal document embeddings
- Perform semantic search
- Retrieve relevant legal knowledge
- Support RAG pipeline

Vector Database

ChromaDB

---

# Relational Database

Responsibilities

Store

- User Accounts
- Consumer Cases
- Conversation History
- Resolution Roadmaps
- Evidence Checklists
- Generated Reports

Database

PostgreSQL

---

# External Services

Gemini API

Purpose

- Natural Language Understanding
- Response Generation
- Reasoning
- Consumer Guidance

The Gemini API must only receive relevant retrieved context.

---

# Authentication Flow

User Login

↓

Backend Validation

↓

JWT Generation

↓

Authenticated Session

↓

Protected APIs

---

# Consumer Case Flow

User Creates Case

↓

Backend Validation

↓

Database Storage

↓

AI Conversation Starts

↓

Case Updated

↓

Roadmap Generated

↓

Report Generated

---

# AI Conversation Flow

User Message

↓

Intent Detection

↓

Issue Classification

↓

Information Collection

↓

Knowledge Retrieval

↓

Reasoning

↓

Guidance Generation

↓

Response

---

# Roadmap Generation Flow

Consumer Information

↓

Issue Analysis

↓

Legal Rights

↓

Available Options

↓

Personalized Steps

↓

Resolution Roadmap

---

# Evidence Generation Flow

Consumer Issue

↓

Issue Category

↓

Required Evidence

↓

Supporting Evidence

↓

Evidence Checklist

---

# Consumer Report Flow

Consumer Information

↓

Conversation Summary

↓

Applicable Rights

↓

Resolution Roadmap

↓

Evidence Checklist

↓

Recommended Next Steps

↓

Final Consumer Report

---

# Security Architecture

The system must implement

- JWT Authentication
- Password Hashing
- Role-Based Authorization
- HTTPS
- Input Validation
- SQL Injection Prevention
- XSS Prevention
- Secure API Communication
- Environment Variable Management

Sensitive information must never be exposed.

---

# Error Handling Architecture

Every layer must

- Validate inputs
- Handle exceptions
- Log errors
- Return meaningful responses
- Prevent application crashes

Errors must not expose internal implementation details.

---

# Logging Architecture

The system should log

- User Authentication
- Consumer Case Creation
- AI Conversations
- API Requests
- Errors
- Warnings
- Security Events

Sensitive user information must never be logged.

---

# Scalability

The architecture should support

- Multiple concurrent users
- Modular services
- Independent AI improvements
- Future legal domains
- Horizontal scaling
- Cloud deployment

---

# Performance Requirements

The architecture should

- Minimize API response time
- Reduce unnecessary database queries
- Cache reusable legal knowledge
- Optimize vector searches
- Support asynchronous processing

---

# Maintainability

The architecture must

- Separate responsibilities
- Minimize coupling
- Maximize modularity
- Support independent module development
- Allow easy feature expansion

---

# Deployment Architecture

Frontend

↓

Backend API

↓

PostgreSQL

↓

ChromaDB

↓

Gemini API

↓

Cloud Infrastructure

Each service should be independently deployable.

---

# Architecture Principles

The architecture must follow

- Separation of Concerns
- Single Responsibility Principle
- Modularity
- Scalability
- Security by Design
- Reusability
- Maintainability
- Reliability
- Fault Tolerance

---

# Success Criteria

The architecture is considered complete when

- All system layers are clearly defined.
- Components have well-defined responsibilities.
- AI workflow is fully documented.
- RAG architecture is integrated.
- Security architecture is specified.
- Scalability is supported.
- Deployment strategy is defined.
- The system is ready for implementation.