# 🎬 VideoMind AI Agent

An intelligent AI-powered video analysis and question-answering system. VideoMind processes video content, extracts meaningful information, and allows users to interact with video data through natural language queries using cutting-edge AI models.

---

## 🚀 Features

- 🎥 Automatic video downloading and processing
- 🧠 AI-powered video content understanding
- 🔍 Semantic search across video content
- 💬 Natural language Q&A on video data
- 💾 Persistent vector storage for fast retrieval
- ⚡ Efficient core pipeline with modular utilities

---

## 🛠️ Tech Stack

| Tool | Purpose |
|------|---------|
| LangChain | AI agent pipeline & chaining |
| OpenAI / Gemini | LLM & embeddings |
| Vector DB | Semantic search & storage |
| Python | Core language |

---

## 📁 Project Structure

```
VideoMind-AI/
│
├── app.py                  # Main application entry point
├── main.py                 # Core agent logic
├── test.py                 # Test scripts
├── requirements.txt        # Project dependencies
├── .env.example            # Environment variable template
├── README.md               # Project documentation
│
├── core/                   # Core pipeline components
├── utils/                  # Utility functions and helpers
├── vector_db/              # Vector store (auto-generated, not in repo)
└── downloads/              # Downloaded videos (auto-generated, not in repo)
```

---

## ⚙️ Setup & Installation

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/VideoMind-AI.git
cd VideoMind-AI
```

### 2. Create a Virtual Environment
```bash
python -m venv .venv
```

Activate it:
- **Windows:** `.venv\Scripts\activate`
- **Mac/Linux:** `source .venv/bin/activate`

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables
Create a `.env` file in the root directory:
```bash
cp .env.example .env
```
Then fill in your actual API keys:
```
OPENAI_API_KEY=your_openai_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
LANGCHAIN_API_KEY=your_langchain_api_key_here
```

### 5. Run the Application
```bash
python app.py
```

---

## 🔑 Environment Variables

| Variable | Description |
|----------|-------------|
| `OPENAI_API_KEY` | Your OpenAI API key |
| `GEMINI_API_KEY` | Your Google Gemini API key |
| `LANGCHAIN_API_KEY` | Your LangChain API key |

> ⚠️ Never commit your `.env` file to GitHub. It is already added to `.gitignore`.

---

## 📝 How It Works

```
Video Input (URL / File)
        ↓
  Video Downloader
        ↓
  Content Extraction
        ↓
  Text & Frame Processing
        ↓
  Embeddings Generation
        ↓
     Vector DB
        ↓
User Query → Semantic Search → Relevant Content → LLM → Answer
```

1. **Input** — User provides a video URL or file
2. **Download** — Video is fetched and stored locally
3. **Extract** — Audio, frames, and text are extracted
4. **Embed** — Content is converted to vector embeddings
5. **Store** — Embeddings saved in Vector DB for fast search
6. **Query** — User asks a question in natural language
7. **Retrieve** — Most relevant content chunks are fetched
8. **Generate** — LLM generates a precise answer

---

## 🧪 Running Tests

```bash
python test.py
```

---

## 📦 Requirements

See `requirements.txt` for the full list. Main dependencies:
```
langchain
openai
google-generativeai
python-dotenv
```

---

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feat/your-feature`)
3. Commit your changes (`git commit -m "feat: add your feature"`)
4. Push to the branch (`git push origin feat/your-feature`)
5. Open a Pull Request

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

## 👤 Author

**Your Name**
- GitHub: [@your-username](https://github.com/your-username)
- LinkedIn: [your-linkedin](https://linkedin.com/in/your-linkedin)
