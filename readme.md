# RAG Architect

A scalable **Retrieval-Augmented Generation (RAG)** system designed for enterprise-grade document ingestion, vector storage, and semantic retrieval. The project includes a complete ingestion pipeline, a querying pipeline, and a fully Dockerized FastAPI backend with Weaviate integration.

---

## 📌 Status
**Core RAG pipeline complete · Dockerized API ready · Weaviate integrated · HyDE & Evaluation pending**

---

## 🧩 Project Summary

RAG Architect provides:

- PDF → text → chunk → embed → vector store ingestion
- Querying powered by Weaviate + Google Gemini Embeddings
- FastAPI backend for `/ingest`, `/query`, `/health`
- Dockerized application + vector database
- Modular architecture prepared for HyDE and evaluation extensions

The first milestone is complete: a functioning ingestion & retrieval system with containerized deployment.

---

## ✨ Features

### Core
- PDF text extraction via `pypdf`
- Chunking, cleaning, and metadata tracking
- Embedding generation using **Google Generative AI**
- Vector database powered by **Weaviate**
- FastAPI endpoints for ingestion, querying, and health checking

### Engineering Enhancements
- Retry-safe Weaviate connection client with exponential backoff
- Auto schema creation
- Local + Docker deployment confirmed working

---

## 🏗️ Architecture Overview

**Pipeline Flow:**
1. Ingest PDF → extract text  
2. Chunk + clean  
3. Generate embeddings via Gemini  
4. Store vectors + metadata into Weaviate  
5. Query → embed question → retrieve top-K  
6. Generate LLM answer  

*A final architecture diagram is pending.*

---


---

## ⚙️ Installation

### 1. Requirements
- Docker + Docker Compose  
- Python 3.10+ (optional local run)  
- Google Generative AI API key  

### 2. Environment Setup

Create a `.env` file:


---

## 🚀 Running the System

### 1. Start the Services

```bash
sudo docker compose up --build -d

2. Health Checks
curl http://localhost:8000/health
curl -i http://localhost:8080/v1/.well-known/ready

3. Ingest a PDF
curl -X POST "http://localhost:8000/ingest" \
     -F "file=@/path/to/file.pdf"

4. Query the System
curl -X POST "http://localhost:8000/query" \
     -F "question=What is this document about?"

