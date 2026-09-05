# LLM Reliability Platform

A RAG-based platform designed to generate evidence-grounded answers and evaluate LLM reliability through claim-level verification.

## Overview

Large Language Models can generate fluent answers that may be unsupported or partially incorrect.

This project adds a reliability layer to a Retrieval-Augmented Generation (RAG) pipeline by:

- Retrieving relevant evidence from a knowledge base
- Using a Knowledge Graph for additional structured context
- Generating an answer using an LLM
- Extracting claims from the generated answer
- Verifying claims against the available evidence
- Calculating a reliability score
- Assigning a confidence level
- Safely refusing to answer when sufficient evidence is unavailable

## Core Pipeline

```text
Document
   ↓
Chunking
   ↓
Embedding Generation
   ↓
Vector Storage
   ↓
Semantic Retrieval
   ↓
Knowledge Graph Context
   ↓
LLM Answer Generation
   ↓
Claim Extraction
   ↓
Claim Verification
   ↓
Reliability Scoring
   ↓
Final Response

## Problem Statement

Large Language Models are highly capable of generating natural-language responses, but fluent responses are not necessarily reliable.

A response can contain:

- Unsupported claims
- Partially correct information
- Hallucinated facts
- Claims that cannot be traced back to the available evidence

Traditional RAG systems primarily focus on retrieving relevant documents and generating an answer from them. They do not necessarily evaluate whether the individual claims in the final response are actually supported by the retrieved evidence.

This project addresses that gap by introducing a **claim-level reliability evaluation layer** on top of the RAG pipeline.
## Solution

The platform extends a standard RAG architecture with a dedicated reliability evaluation pipeline.

Instead of treating the generated answer as the final output, the system evaluates the answer after generation:

```text
Retrieve Evidence
       ↓
Generate Answer
       ↓
Extract Claims
       ↓
Verify Claims
       ↓
Calculate Reliability
       ↓
Return Answer + Evidence + Evaluation

## Key Features

- **Semantic Retrieval** — Qdrant-based vector search with configurable similarity thresholds, candidate-pool retrieval, and duplicate removal.
- **RAG Pipeline** — Generates context from retrieved evidence and Knowledge Graph relationships before LLM generation.
- **Knowledge Graph** — NetworkX-based relationship extraction and persistent graph storage.
- **Claim-Level Verification** — Extracts claims from generated answers and verifies them against retrieved evidence.
- **Reliability Scoring** — Combines claim support and retrieval quality into an overall reliability score with confidence classification.
- **Safe Refusal** — Refuses to provide unsupported answers when sufficient evidence is unavailable.
- **Production-Style API** — FastAPI endpoints with Pydantic validation, typed response contracts, OpenAPI documentation, and structured error handling.
- **Automated Testing** — 53 Pytest tests covering retrieval, RAG, reliability evaluation, validation, refusal behavior, Knowledge Graph functionality, and API behavior.

## System Architecture

The platform is organized into independent API, service, repository, and data layers.

```text
                         User Query
                             │
                             ▼
                    ┌─────────────────┐
                    │    FastAPI      │
                    │      API        │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │   RAG Service   │
                    └────────┬────────┘
                             │
                ┌────────────┴────────────┐
                │                         │
                ▼                         ▼
       ┌─────────────────┐      ┌──────────────────┐
       │ Retrieval       │      │ Knowledge Graph  │
       │ Service         │      │ Service          │
       └────────┬────────┘      └────────┬─────────┘
                │                        │
                ▼                        ▼
       ┌─────────────────┐      ┌──────────────────┐
       │ Qdrant Vector   │      │ NetworkX Graph   │
       │ Database        │      │                  │
       └────────┬────────┘      └────────┬─────────┘
                │                        │
                └────────────┬───────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │  LLM Generation │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Claim Extraction│
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Claim           │
                    │ Verification    │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Reliability     │
                    │ Service         │
                    └────────┬────────┘
                             │
                             ▼
                  Answer + Evidence +
                  Reliability Metrics

                  ## End-to-End Workflow

### Document Ingestion

When a document is added to a knowledge base:

```text
Document
   ↓
Text Chunking
   ↓
Embedding Generation
   ↓
Qdrant Storage
   ↓
Knowledge Graph Extraction
   ↓
Persistent Knowledge Base

The document is divided into retrievable chunks. Each chunk is converted into an embedding and stored in Qdrant along with its document metadata.

The ingestion pipeline also extracts relationships from the document and stores them in the persistent Knowledge Graph.

Question Answering

When a user submits a query:

User Query
   ↓
Query Embedding
   ↓
Semantic Search
   ↓
Candidate Retrieval
   ↓
Duplicate Removal
   ↓
Evidence + Graph Context
   ↓
LLM Generation
   ↓
Claim Extraction
   ↓
Claim Verification
   ↓
Reliability Calculation
   ↓
Final API Response

## Reliability Evaluation

The platform evaluates the generated answer at the claim level rather than treating the entire response as a single unit.

### Claim Extraction

The generated answer is first decomposed into individual factual claims.

```text
Generated Answer
       ↓
Claim Extraction
       ↓
Claim 1
Claim 2
Claim 3
...

Claim Verification

Each claim is then compared against the retrieved evidence.

Claim
  ↓
Evidence Comparison
  ↓
Supported / Unsupported
  ↓
Supporting Evidence

This allows the system to identify which parts of an answer are actually grounded in the knowledge base.

Reliability Score

The final reliability score combines claim-level support with retrieval quality:

Reliability Score =
    0.7 × Claim Support Score
    +
    0.3 × Retrieval Score

Where:

Claim Support Score =
    Supported Claims / Total Claims

For example, if 4 out of 5 generated claims are supported:

Claim Support Score = 4 / 5 = 0.80

The platform also classifies the result using:

Reliability Status

highly_supported
partially_supported
unsupported
safe_refusal

Confidence Level

high
medium
low

This provides a structured evaluation of the generated response instead of returning an answer without any reliability signal.

## Safe Refusal

The system is designed to avoid generating unsupported answers when relevant evidence is unavailable.

If the retrieval layer cannot find sufficient supporting information, the RAG pipeline returns a structured safe refusal instead of relying on unsupported external knowledge.

```text
User Query
    ↓
Semantic Retrieval
    ↓
No Sufficient Evidence
    ↓
Safe Refusal

Safe Refusal

A safe refusal is returned with:

reliability_score = 0.0
claim_support_score = 0.0
reliability_status = safe_refusal
confidence_level = low

This makes the system's uncertainty explicit rather than presenting an unsupported response with false confidence.