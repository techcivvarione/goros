# GOROS Runtime

## Overview

GOROS Runtime is the execution engine of the platform.

Every AI request passes through the Runtime before reaching an LLM.

The Runtime is responsible for orchestrating every intelligent operation performed inside GOROS.

Large Language Models are considered providers, not business logic.

GOROS Runtime owns the complete execution lifecycle.

---

## Responsibilities

The Runtime is responsible for:

- Authentication validation
- Organization validation
- Agent loading
- Prompt assembly
- Memory retrieval
- Knowledge retrieval
- Tool execution
- MCP communication
- LLM provider selection
- Response streaming
- Usage tracking
- Audit logging
- Error handling

The Runtime acts as the intelligence layer of the platform.

LLMs are only one dependency used by the Runtime.