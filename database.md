# Database Requirements

# LegalEase AI - Database Specification

---

# Purpose

The database is responsible for storing application data and managing the legal knowledge used by the AI Agent.

LegalEase AI uses two databases:

1. PostgreSQL
2. ChromaDB

PostgreSQL stores application data.

ChromaDB stores legal knowledge embeddings for Retrieval-Augmented Generation (RAG).

---

# Database Architecture

The system uses a hybrid database architecture.

Application Data

↓

PostgreSQL

Legal Knowledge

↓

ChromaDB

The two databases must remain independent.

---

# PostgreSQL Responsibilities

Store

- User Accounts
- User Profiles
- Consumer Cases
- AI Conversations
- Conversation History
- Resolution Roadmaps
- Evidence Checklists
- Generated Consumer Reports
- User Activity Logs

PostgreSQL must never store document embeddings.

---

# ChromaDB Responsibilities

Store

- Consumer Protection Act embeddings
- Legal rules embeddings
- Government guideline embeddings
- FAQ embeddings
- Consumer education document embeddings

ChromaDB is only used for semantic retrieval.

---

# Official Legal Knowledge Sources

The AI must only use verified Government of India sources.

Primary Sources

1. Consumer Protection Act, 2019

Source

India Code

Department of Consumer Affairs

---

2. Consumer Protection Rules

Include

- Consumer Protection (General) Rules, 2020
- Consumer Protection (Consumer Disputes Redressal Commissions) Rules, 2020
- Consumer Protection (Mediation) Rules, 2020
- Consumer Protection (Central Consumer Protection Council) Rules, 2020
- Consumer Protection (Qualification and Appointment) Rules, 2020
- Consumer Protection (Jurisdiction) Rules, 2021

---

3. Consumer Protection (E-Commerce) Rules

Include

- Consumer Protection (E-Commerce) Rules, 2020
- Consumer Protection (E-Commerce) Amendment Rules, 2021

---

4. Consumer Protection (Direct Selling) Rules

Include

- Consumer Protection (Direct Selling) Rules, 2021

---

5. Department of Consumer Affairs Publications

Include

- Consumer Awareness Guides
- Consumer Advisories
- Government Notifications
- Official Circulars

---

6. National Consumer Helpline

Include

- Frequently Asked Questions
- Consumer Rights Guides
- Complaint Procedures
- Consumer Education Material

---

# Legal Knowledge Categories

The legal database should organize information into the following categories.

Consumer Rights

Consumer Definitions

Consumer Responsibilities

Defective Products

Refunds

Replacement

Warranty

Guarantee

Billing Issues

Delivery Issues

Service Deficiency

Misleading Advertisements

Unfair Trade Practices

Unfair Contracts

Product Liability

E-Commerce Consumer Rights

Direct Selling

Consumer Commissions

Complaint Procedures

Mediation

Evidence Requirements

Appeal Procedures

Consumer Authorities

Important Government Notifications

---

# Legal Knowledge Structure

Every legal record should contain

Document ID

Document Title

Chapter

Section

Subsection

Legal Category

Topic

Keywords

Summary

Original Legal Text

Plain Language Explanation

Related Consumer Rights

Related Consumer Issues

Required Evidence

Suggested Resolution Steps

Source

Publication Date

Version

Embedding ID

---

# Knowledge Processing Pipeline

Official Government Documents

↓

Download

↓

Convert PDF to Text

↓

Clean Text

↓

Split into Chunks

↓

Generate Embeddings

↓

Store in ChromaDB

↓

Index Metadata

No manual editing of legal text.

---

# Retrieval Rules

The AI Agent must

Retrieve only relevant legal chunks.

Rank retrieved documents.

Use metadata filtering.

Pass retrieved context to Gemini.

Never generate responses without retrieval.

---

# Metadata Requirements

Every legal chunk must contain

Document Name

Section Number

Chapter

Topic

Category

Keywords

Government Source

Publication Date

Language

Version

Embedding Reference

---

# Application Database Tables

Users

Stores

- User Information
- Login Credentials
- Profile

---

ConsumerCases

Stores

- Case Information
- Consumer Category
- Case Status
- User Reference

---

Conversations

Stores

- Conversation ID
- User Messages
- AI Responses
- Timestamp

---

Roadmaps

Stores

- Personalized Resolution Steps
- Generated Date
- Consumer Case Reference

---

EvidenceChecklists

Stores

- Required Documents
- Optional Documents
- Consumer Case Reference

---

Reports

Stores

- Consumer Summary
- Rights
- Roadmap
- Evidence Checklist
- Final Report

---

ActivityLogs

Stores

- Login Events
- API Usage
- AI Requests
- Errors

---

# Data Validation

Every database record must

Validate required fields.

Reject duplicate IDs.

Maintain foreign key relationships.

Ensure data integrity.

---

# Security Requirements

Encrypt sensitive data.

Hash passwords.

Protect user privacy.

Restrict database access.

Never expose internal identifiers.

---

# Backup Requirements

Perform regular database backups.

Maintain version history of legal documents.

Support recovery after failure.

---

# Database Update Policy

Legal documents must only be updated when official Government publications change.

Every update must

Create a new version.

Preserve previous versions.

Update embeddings.

Re-index the knowledge base.

---

# Data Sources (Official Only)

Consumer Protection Act, 2019

Consumer Protection Rules

Consumer Protection (E-Commerce) Rules

Consumer Protection (Direct Selling) Rules

Department of Consumer Affairs

India Code

National Consumer Helpline

Do not use unofficial legal blogs or third-party legal websites as primary sources.

---

# Success Criteria

The database is considered complete when

- PostgreSQL schema is implemented.
- ChromaDB knowledge base is created.
- Official legal documents are indexed.
- Embeddings are generated successfully.
- Metadata is searchable.
- Retrieval is accurate.
- Database security is implemented.
- Backup strategy is in place.