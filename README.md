# Website FAQ Bot
This project is a Python-based FAQ bot that can answer questions about the content of any given website. It now includes a Streamlit web UI, making it easy to enter a URL, process the website, and interactively ask questions. The bot uses web scraping, text embedding, semantic search, and OpenAI's GPT model to provide accurate answers based entirely on the website's content.

## Features
- Streamlit UI for easy interactive use
- Web scraping to extract content from any given URL
- Text processing and chunking for efficient handling of large text
- Embedding generation using OpenAI's text-embedding model
- Semantic search to find relevant context for user questions
- Question answering using OpenAI GPT models
- Stores processed website data for fast repeated queries

## Requirements
- Python 3.6+
- requests
- beautifulsoup4
- openai
- numpy
- streamlit

## Installation
1. Clone this repository:
git clone https://github.com/mr-rao-0/Final-project.git
cd Final-project

2. Install the required packages:
pip install -r requirements.txt

3. Set up your OpenAI API key as an environment variable:
macOS/Linux:
export OPENAI_API_KEY="your_api_key"
Windows:
setx OPENAI_API_KEY "your_api_key"

## Usage (Streamlit UI)
1. Run the Streamlit app:
streamlit run ui.py
2. Enter the website URL in the sidebar.
3. Click "Process Website" to extract and embed the content.
4. Ask any question about the processed website.
5. The bot will respond using only extracted content.

## Usage (Command Line)
1. Run the script:
python bot.py
2. Enter the URL of the website when prompted.
3. Ask questions in the terminal.
4. Type "exit" to quit.

## How it works
1. The script fetches the website content and parses it using BeautifulSoup.
2. The text is split into smaller chunks for efficient embedding.
3. Each chunk is converted into an embedding using OpenAI’s embedding model.
4. User questions are also embedded.
5. The most relevant chunks are selected using similarity search.
6. These chunks are passed to the GPT model to generate an accurate answer.

## Note
This project requires an OpenAI API key. Ensure the environment variable is set correctly. Some websites may block scraping or return limited text.

