# Retrieval-Augmented Generation

RAG is a pattern where an application retrieves relevant information from a knowledge source and supplies it to the model before generation.

Instead of asking the model to answer from general training alone, RAG grounds the response in selected documents, notes, or records.

## Why It Matters

RAG is one of the most practical skills in agent engineering because many useful systems need grounded answers based on private or changing data.

## What RAG Usually Includes

- document ingestion
- chunking
- embeddings
- vector or hybrid search
- retrieval
- prompt assembly
- grounded answer generation

## When I Would Use It

- when answers must be based on documents
- when data changes often
- when I need citations or evidence
- when building internal assistants or knowledge tools

## Common Mistakes

- retrieving too much irrelevant context
- assuming retrieval quality is already good
- skipping chunking strategy
- not evaluating whether answers are actually grounded

## Strong Use Cases

- runbook assistants
- internal policy assistants
- onboarding copilots
- customer support knowledge assistants
- postmortem and incident knowledge search

## Good Portfolio Projects

1. DevOps runbook assistant
2. Deployment troubleshooting assistant
3. Engineering onboarding knowledge bot
4. Incident postmortem search assistant

## Learning Checklist

1. Build a simple ingestion pipeline
2. Add retrieval over markdown or PDF files
3. Return answers with citations
4. Measure retrieval quality manually
5. Combine RAG with an agent workflow
