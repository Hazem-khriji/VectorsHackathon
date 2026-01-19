# FinCommerce - Live Data Search Engine

FinCommerce is a real-time product search engine that combines **Live Web Scraping**, **Vector Search (Qdrant)**, and **Financial Context** to provide personalized product recommendations.

## 🚀 Features
- **Live Data Pipeline**: Scrapes real-time product data (Laptops, Tablets, Phones) from e-commerce sites.
- **Semantic Search**: Uses `sentence-transformers` and `Qdrant` to find products by meaning, not just keywords.
- **Context-Aware Ranking**: Filters and recommends products based on User Financial Profile (Balance, Budget).
- **Modular Monolith**: Built with **FastAPI**, **SQLModel**, and **Python**.

## 🛠️ Prerequisites
- Python 3.12+
- Docker (for Qdrant)

## 📦 Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Hazem-khriji/VectorsHackathon.git
   cd VectorsHackathon
   ```

2. **Create a Virtual Environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Setup**
   Create a `.env` file in the root directory:
   ```bash
   touch .env
   ```
   Add your Qdrant configuration (optional if running locally without API key):
   ```env
   QDRANT_URL=http://localhost:6333
   # QDRANT_API_KEY=your_key_here
   ```

## 🐳 Running Qdrant (Vector Database)

You need a running Qdrant instance to store vectors. The easiest way is via Docker:

```bash
docker run -d -p 6333:6333 qdrant/qdrant
```
*Access Qdrant Dashboard at: `http://localhost:6333/dashboard`*

## 🏃‍♂️ Running the Application

### 1. Scrape Live Data (Optional)
Fetch the latest products from the web.
```bash
python src/scraper.py
```
*Outputs to `data/raw/scraped_products.json`*

### 2. Index Data to Qdrant
Upload keywords and vectors to the database.
```bash
python src/upload_scraped.py
```

### 3. Start the Backend API
Run the FastAPI server.
```bash
uvicorn src.app.main:app --reload
```
*API will run at `http://localhost:8000`*

### 4. Test the System
Run the interactive test script to try searches with different users.
```bash
python src/test_api.py
```

## 🧪 API Endpoints

- **GET /**: Health check.
- **GET /search**: Search for products.
  - Query params: 
    - `q`: Search query (e.g., "iphone")
    - `user_id`: ID of the user (use `1` for demo user)

Example:
```bash
curl "http://localhost:8000/search?q=laptop&user_id=1"
```
