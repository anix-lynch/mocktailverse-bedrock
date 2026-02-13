# Workflows

This folder contains orchestration definitions for multi-step processes.

## Current State
- EventBridge scheduled rules (configured in AWS Console)
- Manual Lambda triggers

## Planned
- Step Functions definitions for:
  - Ingestion pipeline (fetch → enrich → embed)
  - Embedding pipeline (process → vectorize → store)
