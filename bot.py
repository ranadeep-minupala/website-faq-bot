import requests
from bs4 import BeautifulSoup
from openai import OpenAI
import numpy as np
import os

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def fetch_and_parse(url):
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, 'html.parser')

    for script_or_style in soup(['script', 'style']):
        script_or_style.decompose()

    text = soup.get_text(separator=' ')
    return text

def split_text(text, max_chunk_size=500):
    words = text.split()
    chunks = []
    current_chunk = []
    current_length = 0
    for word in words:
        current_chunk.append(word)
        current_length += len(word) + 1  # +1 for space
        if current_length >= max_chunk_size:
            chunks.append(' '.join(current_chunk))
            current_chunk = []
            current_length = 0
    if current_chunk:
        chunks.append(' '.join(current_chunk))
    return chunks

def get_embedding(text):
    response = client.embeddings.create(
        input=text,
        model='text-embedding-3-small'
    )
    embedding = response.data[0].embedding
    return np.array(embedding)

def compute_embeddings(chunks):
    embeddings = []
    for chunk in chunks:
        embedding = get_embedding(chunk)
        embeddings.append(embedding)
    return embeddings

def answer_question(question, chunks, embeddings, top_k=3):
    question_embedding = get_embedding(question)
    similarities = [
        np.dot(question_embedding, emb) / (np.linalg.norm(question_embedding) * np.linalg.norm(emb))
        for emb in embeddings
    ]

    top_indices = np.argsort(similarities)[-top_k:][::-1]
    context = '\n\n'.join([chunks[i] for i in top_indices])

    prompt = (
        "Answer the following question based only on the context below.\n\n"
        f"Context:\n{context}\n\n"
        f"Question: {question}\nAnswer:"
    )

    response = client.chat.completions.create(
        model='gpt-4o-mini',
        messages=[
            {"role": "system", "content": "You are a helpful FAQ bot that answers questions about website content."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=300,
        temperature=0.7,
    )
    answer = response.choices[0].message.content.strip()
    return answer

def build_knowledge_base(url):
    """Fetch website, split into chunks, compute embeddings."""
    text = fetch_and_parse(url)
    chunks = split_text(text)
    embeddings = compute_embeddings(chunks)
    return chunks, embeddings

# 👇 This block prevents code from running on import (VERY important for Streamlit)
if __name__ == "__main__":
    url = input("Enter the website URL: ")

    try:
        print("Fetching and processing the website content...")
        chunks, embeddings = build_knowledge_base(url)
        print("Processing complete. You can now ask questions.")

        while True:
            question = input("\nAsk a question (or type 'exit' to quit): ")
            if question.lower() == 'exit':
                break
            answer = answer_question(question, chunks, embeddings)
            print(f"Answer: {answer}")

    except Exception as e:
        print(f"An error occurred: {e}")
