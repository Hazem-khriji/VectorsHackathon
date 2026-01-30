# AI-Powered Product Search & Personalization Engine 🔍

An intelligent, full-stack product search application built for the **Vectors Hackathon**. This project leverages **AI**, **Vector Search (Qdrant)**, and **User Behavior Tracking** to deliver a highly personalized shopping experience. It features hybrid search (text + image), real-time recommendations, and an adaptive interface that learns from user interactions.

## 🌟 Key Features

### 🔍 Advanced Search & RAG
- **Hybrid Search**: seamlessly combines keyword matching with semantic vector search for superior accuracy.
- **Visual Search**: Upload images to find visually similar products using computer vision models.
- **RAG Pipeline**: Retrieves relevant context to generate AI-powered explanations for search results.
- **Query Refinement**: Automatically enhances user queries to capture search intent better.

### 👤 Personalization & Behavioral Tracking
- **Real-Time Tracking**: Monitors user actions including:
  - `search`: What users are looking for.
  - `view`: Products they open.
  - `click`: Items they show interest in.
- **Behavioral Vectors**: Converts user actions into vector embeddings stored in Qdrant's `user_behaviors` collection.
- **Adaptive Feed**: The main product feed personalizes itself based on the user's "cumulative context" (a weighted history of their interests).
- **Session-Based Monitoring**: Tracks anonymous user sessions to provide immediate personalization without requiring login.

### 🛠️ Architecture & Automation
- **Automatic Index Management**: The system automatically checks for and creates necessary Qdrant collections and indexes (`products` and `user_behaviors`) on startup.
- **Dockerized Deployment**: Easy-to-deploy backend services using Docker Compose.

---

## 🏗️ Technical Architecture

### Frontend (`Frontend/`)
There are two frontend versions available:
1. **Standard App (`Frontend/app`)**: The primary React application featuring the full search and personalization UI.
2. **Version 2 (`Frontend/app_version_2`)**: An experimental or alternative interface (if applicable).

**Tech Stack**:
- **React 19** & **TypeScript**
- **Vite** for ultra-fast tooling
- **Modern UI**: Gradient aesthetics, glassmorphism, and responsive design.

### Backend (`Backend/`)
The core logic engine exposed via REST API.
- **FastAPI**: High-performance asynchronous web framework.
- **LangChain**: Orchestrates interactions with Large Language Models (LLMs).
- **Qdrant**: The vector database powering all semantic search and personalization.
- **Sentence Transformers**: Generates embeddings for text and images.

### Data & AI Flow
1. **Ingestion**: Product data is vectorized and stored in Qdrant (`products` collection).
2. **Search**: User queries (text/image) are converted to vectors and compared against product vectors via Hybrid Search.
3. **Tracking**: User interactions are captured, vectorized, and stored (`user_behaviors` collection).
4. **Personalization**: When a user requests recommendations or the home feed, the system aggregates their recent behavior vectors to query for products that match their evolving interests.

---

## 📁 Project Structure

```bash
VectorsHackthon/
├── Frontend/
│   ├── app/                 # Main React Frontend
│   └── app_version_2/       # Secondary Frontend
├── Backend/
│   ├── main.py              # FastAPI Application Entry & Endpoints
│   └── Dockerfile           # Backend Container Config
├── App/                     # Core Logic Modules
│   ├── RAG_pipeline.py      # Retrieval-Augmented Generation Logic
│   ├── Hybrid_Search.py     # Qdrant Search Implementation
│   ├── user_behavior.py     # Behavior Tracking & Vectorization
│   └── llms.py              # LLM Integration Settings
├── create_indexes.py        # Product Index Creation Script
├── create_behavior_indexes.py # User Behavior Index Creation Script
└── docker-compose.yml       # Container Orchestration
```

---

## 🚀 Getting Started

### Prerequisites
- **Node.js** (v18+)
- **Python** (3.8+)
- **Docker Desktop** (for running Qdrant)


## 🚀 Quick Start

### Option 1: Using Docker Compose (Recommended - Easiest)

1. **Setup Environment Variables**
   Create a `.env` file in the root directory:
```env
   # Qdrant Configuration
   QDRANT_URL=http://qdrant:6333
   QDRANT_API_KEY=your_qdrant_api_key_if_cloud
   
   # LLM Configuration (e.g., OpenAI, Gemini, etc.)
   OPENAI_API_KEY=your_api_key
```

2. **Run Everything with Docker Compose**
```bash
   docker-compose up --build
```
   - **Qdrant**: `http://localhost:6333`
   - **Backend**: `http://localhost:8000`
   - **Frontend**: `http://localhost:80`

---

### Option 2: Manual Setup (Step by Step)

#### 1. Start Vector Database (Qdrant)
Run Qdrant using Docker:
```bash
docker run -p 6333:6333 -p 6334:6334 qdrant/qdrant
```

#### 2. Setup Environment Variables
Create a `.env` file in the root directory:
```env
# Qdrant Configuration
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=your_qdrant_api_key_if_cloud

# LLM Configuration (e.g., OpenAI, Gemini, etc.)
OPENAI_API_KEY=your_api_key
```

#### 3. Backend Setup
1. Create a virtual environment:
```bash
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
```
2. Install dependencies:
```bash
   pip install -r requirements.txt
```
3. **Run the Backend**:
```bash
   python Backend/main.py
```
   > **Note:** On the first run, the backend will automatically detect missing indexes and run `create_indexes.py` and `create_behavior_indexes.py` to initialize the database.

   API Documentation will be available at: `http://localhost:8000/docs`

#### 4. Frontend Setup
1. Navigate to the frontend directory:
```bash
   cd app_version_2
```
2. Install dependencies:
```bash
   npm install
```
3. Run the development server:
```bash
   npm run dev
```
   Frontend will be available at: `http://localhost:3000` (or the port shown in terminal)

---

## 🎯 How to Use

1. **Home Feed**: Initially displays generic trending items. As you interact, it adapts to show products matching your interests.
2. **Search**:
   - **Text**: Type "red running shoes" to find matches.
   - **Image**: Upload a photo of a shoe to find similar ones.
3. **Product Interaction**: Click on products. The system records this "view" event.
4. **Personalization**: Go back to the home feed or refresh. You should see recommendations change based on what you just viewed or searched for, thanks to the **User Behavior Tracker**.

---

## 🔧 API Endpoints Overview

- `POST /api/search`: Hybrid search with text/image.
- `GET /api/products`: Fetches the main feed. **Personalized** if `session_id` is provided.
- `POST /api/track`: Receives user events (clicks, searches) to update their behavioral profile.
- `GET /api/recommendations`: Returns specific product suggestions based on session history.

---

## 👥 Authors
Created for the **Vectors Hackathon** to demonstrate the power of Vector Search in e-commerce personalization.