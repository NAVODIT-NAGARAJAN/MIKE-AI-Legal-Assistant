# AGENTS.md

# LegalEase AI - AI Coding Instructions

## Project Name

LegalEase AI – Agentic AI Consumer Rights Assistant

---

# Project Overview

LegalEase AI is an Agentic AI application designed specifically for Indian consumers.

The system helps consumers understand their rights under the Consumer Protection Act, 2019 by analyzing their situation, educating them about their legal rights, and generating a personalized step-by-step resolution roadmap.

The AI DOES NOT replace lawyers or provide legally binding legal advice.

---

# Primary Objective

Build a production-ready Agentic AI application that assists Indian consumers in resolving consumer-related issues through education and guided decision-making.

---

# Scope

The project ONLY supports Indian Consumer Rights.

Supported issues include:

- Defective Products
- Refund Issues
- Warranty Claims
- Billing Disputes
- Delivery Problems
- Service Deficiency
- Misleading Advertisements
- E-Commerce Complaints

Do NOT implement other legal domains.

---

# Out of Scope

Do NOT implement:

- Court case filing
- Legal representation
- Lawyer replacement
- Court judgment prediction
- Automatic complaint filing
- Court tracking
- Criminal law
- Property law
- Family law
- Tenant law

---

# AI Behaviour

The AI must always follow this workflow.

Consumer explains problem

↓

Understand Issue

↓

Ask Follow-up Questions

↓

Collect Missing Information

↓

Analyze Consumer Rights

↓

Educate Consumer

↓

Generate Personalized Resolution Roadmap

↓

Recommend Evidence

↓

Suggest Appropriate Consumer Authority

↓

Finish

Never skip any step.

---

# Development Workflow

Every module MUST follow this order.

Requirements

↓

Design

↓

Create

↓

Unit Test

↓

Debug

↓

Integration Test

↓

Verification

↓

Mark Completed

Never move to the next module before the current module is completely verified.

---

# Module Completion Rule

Every module must satisfy:

✅ Build Successful

✅ No Compilation Errors

✅ No Runtime Errors

✅ Unit Tests Passed

✅ Integration Tests Passed

✅ Code Reviewed

✅ Documentation Updated

Only after all conditions are satisfied

Mark module as

🟩 Completed

Then continue.

---

# AI Coding Rules

Always

- Write modular code.
- Follow SOLID principles.
- Write reusable components.
- Keep business logic separate.
- Keep frontend and backend separated.
- Explain complex functions.
- Write meaningful variable names.
- Write production-ready code.
- Validate every input.
- Handle all exceptions.
- Write readable code.

Never

- Duplicate code.
- Hardcode secrets.
- Skip testing.
- Ignore errors.
- Delete existing functionality.
- Break existing APIs.
- Generate placeholder logic without marking it clearly.

---

# Backend Stack

Language

Python

Framework

FastAPI

Authentication

JWT

Database

PostgreSQL

Vector Database

ChromaDB

ORM

SQLAlchemy

AI Framework

LangGraph

LLM

Gemini API

---

# Frontend Stack

React

Tailwind CSS

Axios

React Router

---

# Database Rules

Use normalized tables.

Create separate tables for

Users

ConsumerCases

ChatHistory

GeneratedRoadmaps

EvidenceChecklist

KnowledgeBase

Do not create unnecessary tables.

---

# AI Rules

The AI must never invent laws.

Every legal explanation must be retrieved from the knowledge base.

Use Retrieval-Augmented Generation (RAG).

Never generate unsupported legal claims.

If confidence is low,

ask more follow-up questions.

---

# Knowledge Base

Use only official Indian sources.

Consumer Protection Act, 2019

Consumer Protection Rules

Consumer Protection (E-Commerce) Rules

Department of Consumer Affairs

National Consumer Helpline

Never use unofficial legal blogs as primary sources.

---

# UI Guidelines

Theme

Modern

Minimal

Responsive

Desktop First

Professional

Primary Color

Blue

Secondary Color

White

Icons

Lucide React

---

# Folder Structure

backend/

frontend/

legal_data/

tests/

docs/

---

# API Rules

REST APIs only.

Always validate requests.

Return proper HTTP status codes.

Always return JSON.

Handle every possible exception.

---

# Testing Rules

Every feature must include

Unit Testing

Integration Testing

Error Handling

Validation Testing

Only after all tests pass

mark module completed.

---

# Security Rules

Hash passwords.

Store secrets in .env

Validate every request.

Prevent SQL Injection.

Sanitize user input.

Never expose API keys.

---

# Performance Rules

Keep API response fast.

Avoid duplicate database queries.

Use asynchronous APIs where appropriate.

Reuse database connections.

---

# Documentation Rules

Every completed module must include

Updated documentation

API documentation

Comments for complex logic

README updates if necessary

---

# Important Rule

LegalEase AI is NOT a legal chatbot.

It is an Agentic AI Consumer Rights Assistant.

Its purpose is to

Understand

Analyze

Educate

Guide

Generate Personalized Roadmaps

Help consumers make informed decisions.

Never behave like a generic question-answer chatbot.

Always work toward helping the consumer understand and navigate their consumer rights issue.

## Golden Rule

Whenever generating code, think like a senior software engineer.

Prioritize:

1. Correctness
2. Maintainability
3. Scalability
4. Security
5. Readability

Never sacrifice code quality for speed.

If requirements are unclear, stop and ask for clarification instead of making assumptions.