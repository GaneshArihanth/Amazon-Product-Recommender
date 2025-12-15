# Amazon Product Recommender

This is an end-to-end AI-powered recommendation and price-tracking system for Amazon products.  
This project combines web scraping, retrieval‑augmented generation (RAG), and a lightweight web UI to help users:

- Discover relevant products conversationally
- Compare options based on rich product metadata
- Track price changes over time and get alerts

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Core Features](#core-features)
3. [Architecture](#architecture)
   - [High‑Level Flow](#high-level-flow)
   - [Logical Components](#logical-components)
4. [Project Structure](#project-structure)
5. [Installation & Setup](#installation--setup)
   - [Prerequisites](#prerequisites)
   - [Clone and Environment](#clone-and-environment)
   - [Python Dependencies](#python-dependencies)
   - [Environment Variables](#environment-variables)
   - [ChromaDB Setup](#chromadb-setup)
   - [Ollama & Llama 3 Setup](#ollama--llama-3-setup)
6. [Running the Application](#running-the-application)
   - [Starting the Backend](#starting-the-backend)
   - [Using the Web UI](#using-the-web-ui)
   - [Running the Price Tracker](#running-the-price-tracker)
7. [Detailed Module Documentation](#detailed-module-documentation)
   - [`app.py` – Flask Application](#apppy--flask-application)
   - [`agent.py` – Recommendation Agent / RAG Orchestrator](#agentpy--recommendation-agent--rag-orchestrator)
   - [`tools.py` – Utility and Tooling Layer](#toolspy--utility-and-tooling-layer)
   - [`scrapers/` – Product Scrapers](#scrapers--product-scrapers)
   - [`price_tracker.py` & `price_history_provider.py`](#price_trackerpy--price_history_providerpy)
   - [`config.py` – Configuration Management](#configpy--configuration-management)
   - [`data/` – Product and Vector Data](#data--product-and-vector-data)
   - [`static/` & `templates/` – Frontend](#static--templates--frontend)
8. [Testing](#testing)
9. [Deployment](#deployment)
10. [Scope and Future Enhancements](#scope-and-future-enhancements)
11. [Limitations](#limitations)
12. [License](#license)

---

## Project Overview

Modern marketplaces like **Amazon** contain millions of products. Users often:

- Struggle to phrase what they want in keyword‑style queries
- Spend time jumping between tabs comparing products
- Miss out on deals because they are not continuously checking prices

This project aims to solve those problems by:

- Letting users **talk** to the system in natural language about what they want (e.g., _“I need a 27‑inch 4K monitor under $300 with good color accuracy”_)
- Using **RAG with Llama 3** and **ChromaDB** over scraped product data
- Maintaining a **price history** for products and enabling a **price tracker** workflow

---

## Core Features

### 1. Conversational Product Recommendations

- Accepts free‑form user queries via a simple web UI.
- Uses **LangChain** + **Llama 3 (Ollama)** + **ChromaDB** to:
  - Retrieve the most relevant product chunks from stored PDFs / dataset.
  - Generate concise, product‑aware responses.
- Supports product comparison, trade‑offs, and explanation‑style answers.

### 2. Product Data Ingestion and Storage

- Scraped Amazon product data is stored in the `data/` directory.
- Data is vectorized and stored in **ChromaDB** for semantic search.
- Embeddings are generated using a **sentence transformer** (configurable).

### 3. Retrieval‑Augmented Generation (RAG)

- Queries are embedded and matched against product vectors in ChromaDB.
- Retrieved context (titles, descriptions, specs, price history, etc.) is passed to Llama 3.
- LLM generates grounded recommendations, ideally citing or being based on the retrieved context.

### 4. Price Tracking and History

- **`price_tracker.py`** and **`price_history_provider.py`**:
  - Periodically scrape price information for relevant ASINs / URLs.
  - Store historical prices in a structured format (e.g., JSON / CSV / DB).
  - Provide APIs for checking price trends (e.g., “is this product trending down?”).

### 5. Web Frontend

- Built with **Flask** templates and **static** assets:
  - An input box for user queries
  - Results section showing:
    - Recommended products
    - Key specs
    - Price information and trends (where available)
- Lightweight, vanilla **HTML/CSS/JS**.

---

## Architecture

### High‑Level Flow

1. **Data Collection**
   - `scrapers/` gather product data from Amazon.
   - Raw product data is stored in `data/` and/or PDF form.

2. **Vectorization and Storage**
   - Product descriptions and metadata are processed into text chunks.
   - A sentence transformer embeds these chunks into vectors.
   - Vectors plus metadata are stored in **ChromaDB** (`chroma_db/`).

3. **User Query Handling**
   - User sends a query through the web UI (`app.py`).
   - Query → embedding → ChromaDB similarity search.

4. **RAG Pipeline**
   - Top‑k relevant documents/chunks retrieved from ChromaDB.
   - Retrieved context passed into **Llama 3** via **LangChain** (`agent.py`).
   - LLM generates a recommendation‑oriented response.

5. **Response to User**
   - Flask renders response (JSON or server‑side templates).
   - User sees recommended products and reasoning.

6. **Price Tracking (Background / Scheduled)**
   - `run_tracker.py` / `price_tracker.py` periodically call scrapers.
   - Price history is stored and can be used in responses.

### Logical Components

- **Data Layer**
  - `data/` – product data, cached responses, etc.
  - `chroma_db/` – local vector database directory.
- **Backend**
  - `app.py` – Flask web server and HTTP endpoints.
  - `agent.py` – binding LangChain, ChromaDB, and Ollama LLM.
  - `tools.py` – helper functions, tools, possibly LangChain tools.
  - `config.py` – config constants and environment handling.
- **Scraping & Tracking**
  - `scrapers/` – page/parsing logic for Amazon product data.
  - `price_tracker.py` – periodic price fetcher.
  - `price_history_provider.py` – abstraction around stored price history.
- **Frontend**
  - `templates/` – Flask HTML templates.
  - `static/` – CSS, JS, images.

---

## Project Structure

Below is the core structure of the repository with a description of each major element:

```text
Amazon-Product-Recommender/
├─ .env                      # Local environment variables (ignored by git)
├─ .env.example              # Example env file with required keys
├─ README.md                 # Project documentation (this file)
├─ requirements.txt          # Python dependencies
├─ render.yaml               # Render.com deployment configuration (if used)
├─ app.py                    # Flask application entry point
├─ agent.py                  # RAG agent / LangChain + Llama 3 integration
├─ config.py                 # Central config and environment management
├─ tools.py                  # Utility functions and tools for the agent
├─ price_tracker.py          # Price tracking main logic
├─ price_history_provider.py # Abstraction to read/write price history
├─ run_tracker.py            # Script/entry-point to run the price tracker
├─ a.py                      # Experimental / helper script (internal use)
├─ b.py                      # Experimental / helper script (internal use)
├─ test_async.py             # Tests for async behaviors / scrapers / calls
├─ test_caching.py           # Tests for caching logic (if any)
├─ test_import.py            # Tests for module import integrity
├─ test_scrapers.py          # Tests for scraping logic and parsers
├─ data/                     # Raw and processed product data
│  └─ ...                    # CSV/JSON/PDF or other artifacts
├─ scrapers/                 # Amazon scraping utilities
│  └─ ...                    # Specific scraper modules per page or pattern
├─ chroma_db/                # ChromaDB persistent storage directory
│  └─ ...                    # Collection data / index files
├─ static/                   # Frontend static assets
│  ├─ css/
│  ├─ js/
│  └─ img/
└─ templates/                # Flask HTML templates
   └─ index.html             # Main UI page (name may vary)
```

> Note: `__pycache__/` directories contain Python bytecode caches and are not part of the core logic.

---

## Installation & Setup

### Prerequisites

- **Python**: 3.8 or higher
- **pip**: Latest version
- **Ollama** installed and running locally  
  - With **Llama 3 (7B)** model installed.
- **ChromaDB** (Python package, installed via `requirements.txt`)
- Basic command‑line environment (Linux, macOS, or WSL on Windows)

### Clone and Environment

```bash
git clone https://github.com/GaneshArihanth/Amazon-Product-Recommender.git
cd Amazon-Product-Recommender
```

Create a virtual environment (recommended):

```bash
python -m venv .venv
source .venv/bin/activate   # On Windows: .venv\Scripts\activate
```

### Python Dependencies

```bash
pip install -r requirements.txt
```

If installation fails for a specific library (e.g., GPU‑related packages) you can either install CPU‑only versions or adjust `requirements.txt` accordingly.

### Environment Variables

Copy the example environment file:

```bash
cp .env.example .env
```

Open `.env` and set the following (names may vary depending on `config.py`):

- `OLLAMA_BASE_URL` – URL where the Ollama server is exposed (default: `http://localhost:11434`)
- `LLM_MODEL_NAME` – e.g., `llama3` or `llama3:7b`
- `CHROMA_PERSIST_DIR` – local path for ChromaDB persistence (often `./chroma_db`)
- Any keys or secrets required for scraping (if you use proxies or external APIs)

The exact keys used are defined and read in `config.py`.

### ChromaDB Setup

ChromaDB is embedded in the Python process and persists data to a directory. Typical flow:

- On first run of the ingestion pipeline (within `agent.py` or a dedicated script), ChromaDB collections are created and populated from data in `data/`.
- Subsequent runs re‑use the **persistent** data in `chroma_db/`.

If a setup script exists (for example):

```bash
python agent.py --init-db
```

Use it to build the initial index. If not, follow the logic in `agent.py` to see how and when embeddings are created.

### Ollama & Llama 3 Setup

1. Install Ollama following the official docs:  
   [Ollama documentation](https://ollama.com/docs)

2. Download the Llama 3 model (7B):

   ```bash
   ollama pull llama3
   ```

   or the specific tag your project expects (e.g., `llama3:7b`).

3. Start the Ollama server (if it’s not started automatically on your system):

   ```bash
   ollama serve
   ```

4. Make sure `OLLAMA_BASE_URL` in `.env` matches the actual host/port.

---

## Running the Application

### Starting the Backend

From the project root (and with your virtual environment activated):

```bash
export FLASK_APP=app.py        # On Windows: set FLASK_APP=app.py
export FLASK_ENV=development   # Optional
flask run                      # Defaults to http://127.0.0.1:5000
```

Or, if `app.py` has a typical `if __name__ == "__main__": app.run(...)`:

```bash
python app.py
```

Once running, open:

- `http://localhost:5000/` in your browser (port may differ).

### Using the Web UI

1. Navigate to the home page served by Flask.
2. Enter a query such as:
   - “I want wireless earbuds under ₹3000 with good battery life”
   - “Best 27‑inch monitors for programming and gaming”
3. Submit the query.
4. The backend:
   - Embeds your query.
   - Runs a ChromaDB search.
   - Sends context + query to Llama 3.
   - Renders the AI response and recommended products.

### Running the Price Tracker

Use `run_tracker.py` or call `price_tracker.py` directly, depending on how it is structured.

Example:

```bash
python run_tracker.py
# or
python price_tracker.py
```

This will:

- Fetch the latest prices for configured products.
- Update the stored price history through `price_history_provider.py`.

You can then integrate this information into the recommendation answers or query it via dedicated endpoints (see `app.py` for available routes).

---

## Detailed Module Documentation

### `app.py` – Flask Application

**Role**

- Main HTTP entry point.
- Defines routes/endpoints for:
  - Home page (UI).
  - Chat / recommendation API (e.g., `/recommend`, `/chat`, etc.).
  - Possibly API endpoints for price history or product search.

**Typical responsibilities**

- Validate and parse incoming user queries (JSON or form data).
- Invoke functions from `agent.py` to get AI‑generated recommendations.
- Format the result as:
  - JSON response for frontend JS, or
  - Directly rendered template with embedded results.
- Handle basic error cases and return appropriate HTTP status codes.

---

### `agent.py` – Recommendation Agent / RAG Orchestrator

**Role**

- Core intelligence of the project: orchestrates **retrieval** and **generation**.

**Responsibilities**

- Initialize connections to:
  - **ChromaDB** (vector store)
  - **Ollama** LLM (Llama 3 model)
- Define:
  - Embedding function or sentence transformer to vectorize queries and documents.
  - Retrieval pipeline (e.g., top‑k semantic search using ChromaDB).
  - LangChain chains or custom pipelines combining:
    - Prompt templates
    - Retrieval
    - LLM calls

**Typical flow**

1. Accept a user query as text.
2. Embed query → search ChromaDB for relevant product chunks.
3. Construct a prompt including:
   - User query
   - Retrieved product data (titles, descriptions, rating, price history, etc.)
   - System instructions (e.g., “Return at most 5 specific product suggestions…”).
4. Call Llama 3 through Ollama.
5. Parse the LLM output into:
   - Raw answer text
   - Optional structured product list (if you parse the text or use tool calls).
6. Return results to `app.py`.

---

### `tools.py` – Utility and Tooling Layer

**Role**

- Home for reusable logic and helper functions.
- May also define **LangChain tools** to be used by the agent.

**Common responsibilities**

- Text processing utilities (cleaning, chunking).
- Helpers for interacting with:
  - ChromaDB collections
  - File system (loading PDFs, JSON, CSV)
  - Price history retrieval
- Any generic code used by tests or multiple modules.

---

### `scrapers/` – Product Scrapers

**Role**

- Gather raw Amazon product information.

**Typical contents**

- Scrapers for:
  - Product listing pages
  - Product details pages
  - Possibly specific categories
- Parsing helpers that:
  - Extract title, brand, rating, reviews count, price, features, etc.
  - Normalize currencies and units.

**Notes**

- Respect Amazon’s Terms of Service and robots.txt.
- Consider rate‑limiting and anti‑bot measures.
- In a production‑grade system, scraping would typically be replaced with:
  - Official APIs (where allowed)
  - Ingested datasets.

---

### `price_tracker.py` & `price_history_provider.py`

**`price_tracker.py`**

- Schedules or runs price checks for configured products.
- Calls the scrapers to get the current price.
- Uses `price_history_provider.py` to record each observation.
- May contain logic like:
  - Notification triggers when price drops below a threshold.
  - Logging of anomalies or scraping failures.

**`price_history_provider.py`**

- Focused on reading and writing price history data.
- Abstracts storage details:
  - Could be JSON files, CSV, SQLite, etc.
- Provides methods such as:
  - `get_history(product_id)`
  - `append_price(product_id, price, timestamp)`
  - `calculate_trend(product_id)` (if implemented)

---

### `config.py` – Configuration Management

**Role**

- Central place for configuration constants and environment variables.

**Typical content**

- Paths:
  - `DATA_DIR`, `CHROMA_PERSIST_DIR`, etc.
- LLM settings:
  - `LLM_MODEL_NAME`, `OLLAMA_BASE_URL`.
- Application settings:
  - Flask debug flag, host, port.
- Helper functions:
  - `load_env()` or functions that read from `.env`.

---

### `data/` – Product and Vector Data

**Role**

- Storage of:
  - Raw scraped product data (e.g., CSV, JSON, PDF).
  - Pre‑processed forms of product information for ingestion.
- Could also contain:
  - Example datasets for testing.
  - Caches generated during ingestion.

This directory is consumed by `agent.py`, `scrapers/`, and potentially tests.

---

### `static/` & `templates/` – Frontend

**`templates/`**

- Contains **Flask HTML templates**.
- Typical files:
  - `index.html` – main page with:
    - A query input box
    - A section for showing AI recommendations
  - Optional additional pages (about, debug, etc.)

**`static/`**

- Contains static assets referenced by templates:
  - `static/css/style.css` – styling for the UI.
  - `static/js/app.js` – client‑side logic to call backend APIs.
  - `static/img/` – logo or icons (if any).

---

## Testing

The repository includes multiple test files:

- `test_async.py`  
  Ensures async behaviors (e.g., async scrapers, async I/O) work correctly and do not break the app.

- `test_caching.py`  
  Verifies that caching (if present) behaves as intended (e.g., reusing embeddings, not re‑scraping unnecessarily).

- `test_import.py`  
  Sanity check that modules import correctly, dependencies are in place, and circular imports are avoided.

- `test_scrapers.py`  
  Validates scraping logic using:
  - Sample HTML fixtures
  - Mocked HTTP responses

To run all tests:

```bash
pytest
```

(Install `pytest` if it’s not already in `requirements.txt`.)

---

## Deployment

The repository contains a `render.yaml` file, which suggests deployment on **Render.com**.

Typical steps (high‑level):

1. Push your code to GitHub (already done for this repo).
2. Create a new **Web Service** on Render.
3. Point it at this repository.
4. Set environment variables in Render’s dashboard to match `.env`.
5. Ensure the **start command** runs your Flask app, for example:

   ```bash
   gunicorn app:app --bind 0.0.0.0:$PORT
   ```

6. Make sure that:
   - ChromaDB storage directory is writable.
   - Ollama (or an equivalent LLM endpoint) is reachable from the deployed environment.
     - For cloud deployment, you may need a remote LLM endpoint instead of local Ollama.

Deployment specifics will depend on your actual hosting stack; `render.yaml` should be consulted and adapted when needed.

---

## Scope and Future Enhancements

This project is intentionally modular, allowing multiple extensions:

- **Better Product Coverage**
  - Expand scraping to more categories and regions.
  - Add multi‑language support.

- **Smarter Ranking**
  - Incorporate ratings, review sentiment, and seller trust.
  - Multi‑objective ranking (price vs. quality vs. brand).

- **Richer Interaction**
  - Multi‑turn chat where the agent remembers previous preferences.
  - Explicit comparison mode (e.g., “Compare product A vs B”).

- **Notification System**
  - Email/Telegram/Discord alerts when a tracked product hits a target price.
  - Daily/weekly price change summaries.

- **Model Improvements**
  - Optionally plug in other LLMs (cloud or local).
  - Experiment with better embedding models for product‑style text.

---

## Limitations

- **Unofficial Scraping**  
  Direct HTML scraping of Amazon may violate their Terms of Service; this project is for educational/research use. In a production environment, use allowed APIs or datasets.

- **Local Resources**  
  Running Llama 3 and building vector indices can be resource‑intensive on low‑end machines.

- **Data Freshness**  
  Recommendations are only as good as the underlying data and scraping/price‑tracking frequency.

- **Model Hallucinations**  
  Although RAG reduces hallucination risks, LLMs can still produce incorrect or outdated product details. Always verify critical information directly on Amazon.

---

## License

Unless otherwise specified in the repository, this project is provided under an open‑source license.  
Please check the `LICENSE` file (or repository settings) for the precise terms of use.


---
