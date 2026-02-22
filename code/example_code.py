from ollama import Client
import json
import chromadb
from langchain_text_splitter import RecursiveCharacterTextSpitter
import os

client = chromadb.PersistentClient()
remote_client = Client(host=f"http://172.16.8.168:11434")
collection = client.get_or_create_collection(name="articles_demo")


counter = 0
if os.path.exists("counter.txt"):
    with open("counter.txt", "r") as f:
        counter = int(f.read())

splitter = RecursiveCharacterTextSplitter(
    chunk_size=100,
    chunk_overlap=0,
    separators=[".", "\n"]
   )

print("Reading articles.jsonl and generating embeddings...")

if collection.count() == 0:  # Only build the database if it's empty
    print("Database is empty. Building the database...")
    with open("articles.jsonl", "r", encoding="utf-8") as f:
        for i, article in enumerate(f):
                if i < counter:
                    print("skipping line", i ,counter)
                    continue
                article = json.loads(article)
                content = article["content"]
                sentences = [c.strip() for c in splitter.split_text(content) if c.strip()]

        for i, text_chunk in enumerate(sentences):
            response = remote_client.embed(model="nomic-embed-text", input=f"search_document: {text_chunk}")
            collection.add(
            ids=[f"sentence_{i}"],
            embeddings=[response["embeddings"][0]],
            documents=[text_chunk]
            )
print("Database built successfully!")

# query = "what are different problems provinces of nepal are facing?"
# query = "Where is Soaltee Hotel located?"
# query = "Are there any predicted hindrance for upcoming election ?"
# query = "Who is contending for first title at the under-age tournament?"
# query_embed = remote_client.embed(model="nomic-embed-text", input=f"query: {query}")["embeddings"][0]

usr_input = input("Enter your question: ")
query_embed = remote_client.embed(model="nomic-embed-text", input=f"query: {usr_input}")["embeddings"][0]

results = collection.query(query_embeddings=[query_embed], n_results=3)
print(f"\nQuestion: {usr_input}")

contxt = "\n".join([f"{doc}" for doc in results["documents"][0]])

result = chat_bot.generate(
    model="nomic-chat",
    input=[
        {"role": "system", "content": "You are a helpful assistant that provides information based on the retrieved context."},
        {"role": "user", "content": f"Context: {contxt}\n\nQuestion: {usr_input}\n\nAnswer:"}
    ])

print(result)




