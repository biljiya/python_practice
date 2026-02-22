from ollama import Client
import chromadb

# 1. Initialize the local Vector Database (ChromaDB)
client = chromadb.PersistentClient()
remote_client = Client(host='http://172.16.8.168:11434')


collection = client.get_or_create_collection(name="simple_knowledge")

# collection = client.get_or_create_collection(
#     name="simple_knowledge",
#     metadata={"hnsw:space": "cosine"}
# )

# 2. Load the simple text file and embed each line
print("Reading articles.jsonl and generating embeddings...")

with open('articles.jsonl', 'r') as f:
    for i, line in enumerate(f):
        content = line.strip()
        if not content:
            continue
        
        response = remote_client.embed(model='nomic-embed-text', input=content)
        # response = remote_client.embed(model='nomic-embed-text', input=f"search_document: {content}")
        
        embedding = response['embeddings'][0]
        collection.add(
            ids=[f"id_{i}"],
            embeddings=[embedding],
            documents=[content],
            metadatas=[{"line": i}]
        )

print("Database built successfully!")


# 3. Test Retrieval
query = "Who finishes off in style in the 2011 World Cup final?"
query_embed = remote_client.embed(model='nomic-embed-text', input=query)['embeddings'][0]
# query_embed = remote_client.embed(
#     model='nomic-embed-text', 
#     input=f"search_query: {query}"
# )['embeddings'][0]
while True:
    user_input = input("How may I assist you? \n")
    query_embd=ollama.embed(model="nomic-embed-text", input=f"query: {user_input}")["embeddings"][0]
    results = collection.query(query_embeddings=[query_embd], n_results=2)
    
    retrieved_docs = results['documents'][0]
    context = "\n\n".join(retrieved_docs)

    prompt = f"""You are a helpful assistant. Answer the question based on the context provided. Use the information in the context to form your answer. If context does not have enough information just say "I don't know"

    Context: {context}

    Question: {user_input}

    Answer:"""

    response = chat_bot.generate(
            model="qwen3:4b-instruct-2507-q4_K_M",
            prompt=prompt,
            options={
                "temperature": 0.1
            }
        )

    answer = response['response']

   



