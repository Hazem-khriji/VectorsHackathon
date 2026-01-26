# AI-Powered Product Search 🔍

An intelligent product search application that combines the power of AI and vector search to help users find products using natural language queries and images.

## 🌟 Features

- **Text-Based Search**: Search for products using natural language descriptions
- **Image Search**: Upload product images to find similar items
- **Hybrid Search**: Combines text and image search for better results
- **RAG Pipeline**: Uses Retrieval-Augmented Generation for accurate product recommendations
- **Modern UI**: Beautiful, responsive React interface with smooth animations
- **Real-time Results**: Fast, AI-powered search results

## 🏗️ Architecture

### Frontend
- **React 19** with TypeScript
- **Vite** for fast development and building
- Modern, responsive UI with gradient backgrounds
- Real-time search with loading states

### Backend
- **FastAPI** for high-performance API
- **LangChain** for LLM orchestration
- **Qdrant** vector database for semantic search
- **Hybrid Search** combining multiple retrieval strategies
- Support for both text and image inputs

### AI/ML Components
- RAG (Retrieval-Augmented Generation) pipeline
- Vector embeddings for semantic search
- Image understanding for visual search
- Query refinement for better results

## 📁 Project Structure

```
VectorsHackthon/
├── Frontend/
│   └── app/                 # React application
│       ├── src/
│       │   ├── App.tsx      # Main component
│       │   ├── App.css      # Styling
│       │   └── main.tsx     # Entry point
│       └── package.json
├── Backend/
│   └── main.py              # FastAPI server
├── App/
│   ├── RAG_pipeline.py      # RAG implementation
│   ├── Hybrid_Search.py     # Hybrid search logic
│   ├── llms.py              # LLM configurations
│   └── prompts.py           # AI prompts
└── README.md
```

## 🚀 Getting Started

### Prerequisites

- **Node.js** (v18 or higher)
- **Python** 3.8+
- **Qdrant** vector database running on `http://localhost:6333`
- Virtual environment (recommended)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd VectorsHackthon
   ```

2. **Set up the Python backend**
   ```bash
   # Create and activate virtual environment
   python -m venv .venv
   .venv\Scripts\activate  # On Windows
   # source .venv/bin/activate  # On macOS/Linux

   # Install dependencies
   pip install -r requirements.txt
   ```

3. **Set up the React frontend**
   ```bash
   cd Frontend/app
   npm install
   ```

4. **Configure environment variables**
   Create a `.env` file in the root directory with necessary API keys and configurations.

### Running the Application

1. **Start Qdrant** (if not already running)
   ```bash
   # Follow Qdrant documentation for your setup
   docker run -p 6333:6333 qdrant/qdrant
   ```

2. **Start the backend server**
   ```bash
   # From the root directory
   cd Backend
   python main.py
   ```
   The API will be available at `http://localhost:8000`

3. **Start the frontend development server**
   ```bash
   cd Frontend/app
   npm run dev
   ```
   The app will be available at `http://localhost:5173`

## 🎯 Usage

1. **Text Search**: 
   - Enter a product description in the search box
   - Click "Search" to get AI-powered results

2. **Image Search**:
   - Click the upload area or drag and drop an image
   - Optionally add text description for better results
   - Click "Search"

3. **View Results**:
   - Results appear below the search form
   - AI generates relevant product recommendations

4. **Reset**:
   - Click "Reset" to clear the form and start a new search

## 🔧 API Endpoints

### POST `/api/search`
Search for products using text and/or image

**Request:**
- `query` (optional): Text search query
- `image` (optional): Image file (PNG, JPG, WEBP)

**Response:**
```json
{
  "success": true,
  "data": "AI-generated product recommendations"
}
```

## 🛠️ Technologies Used

### Frontend
- React 19
- TypeScript
- Vite
- Modern CSS with animations

### Backend
- FastAPI
- LangChain
- Qdrant Client
- Python 3.8+

### AI/ML
- Large Language Models (LLMs)
- Vector Embeddings
- RAG (Retrieval-Augmented Generation)
- Hybrid Search

## 🎨 Features in Detail

### Modern UI Design
- Dark gradient background with glowing effects
- Glass-morphism card design
- Smooth animations and transitions
- Responsive layout for all devices
- Custom file upload interface
- Loading states and error handling

### Intelligent Search
- Query refinement for better results
- Image understanding and description
- Semantic search using vector embeddings
- Hybrid search combining multiple strategies
- Context-aware product recommendations

## 📝 Development

### Frontend Development
```bash
cd Frontend/app
npm run dev      # Start development server
npm run build    # Build for production
npm run lint     # Lint code
```

### Backend Development
```bash
cd Backend
python main.py   # Start FastAPI server
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👥 Authors

Created for the Vectors Hackathon

## 🙏 Acknowledgments

- LangChain for LLM orchestration
- Qdrant for vector search
- FastAPI for the backend framework
- React team for the amazing frontend library

---

**Note**: Make sure all services (Qdrant, Backend, Frontend) are running for the application to work properly.
