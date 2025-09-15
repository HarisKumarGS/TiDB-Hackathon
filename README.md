# CrashLens App — TiDB Hackathon Submission

#### [Live Demo](http://tidb-hackathon-static-site.s3-website-us-east-1.amazonaws.com)

## Overview

CrashLens is an AI-powered crash analysis platform for modern SaaS and e-commerce applications. It enables teams to, analyze root causes and guide to fix it using LLM agents, manage repositories, and automate bug fixes.

CrashLens leverages advanced code and document indexers to enable semantic search and retrieval across source code, logs, and documentation. The platform uses **multimodal Retrieval-Augmented Generation (RAG)** to store and query semantic embeddings for both code and natural language documents. This allows the RCA agent to cross-reference crash logs, code changes, and documentation for more accurate root cause analysis and automated bug fixes.

- **Semantic Storage:** Embeddings for code snippets, error logs, and documentation are indexed and stored for fast retrieval.
- **Multimodal RAG:** Combines text code semantics and technical document images / pdfs, enabling the LLM agent to reason across multiple data types and sources.
- **Contextual RCA:** RCA agent uses indexed semantics/ documents to provide context-aware suggestions and fixes.

---

## Key Features

- **Crash Simulation:** Generate realistic crash logs and RCA reports.
- **Root Cause Analysis:** Automated RCA and bug fixes using LLM agents.
- **Repository Management:** Multiple Projects in single dashborad
- **Real-time Dashboard:** Crash stats, severity charts, trends.
- **Crash Detail:** RCA report, log viewer, git diff viewer, PR creation.
- **WebSocket Notifications:** Real-time updates to frontend.

---

## Submission Notes

- See individual `README.md` files in [backend](./crash-lens-app/backend/) and [frontent](./crash-lens-app/frontend/) for more details.
- For demo, visit: [Live Demo](http://tidb-hackathon-static-site.s3-website-us-east-1.amazonaws.com)