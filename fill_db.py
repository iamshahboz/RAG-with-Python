from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

import chromadb 

# setting the environment

DATA_PATH = r"data"
CHROMA_PATH = r"chroma_db"

print("Starting: connecting to ChromaDB...")

chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)

collection = chroma_client.get_or_create_collection(name="growing_vegetables")

print(f"Connected to collection '{collection.name}' (currently {collection.count()} items)")

# loading the document 

print(f"Loading PDFs from '{DATA_PATH}'...")

loader = PyPDFDirectoryLoader(DATA_PATH)

raw_documents = loader.load()

print(f"Loaded {len(raw_documents)} pages")

# splitting the document 

print("Splitting documents into chunks...")

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size = 300,
    chunk_overlap=100,
    length_function = len,
    is_separator_regex=False
)

chunks = text_splitter.split_documents(raw_documents)

print(f"Split into {len(chunks)} chunks")

# preparing to be added to chromadb 

documents = []

metadata = []
ids = []

i = 0 

print("Adding chunks to ChromaDB...")

for chunk in chunks:
    documents.append(chunk.page_content)
    ids.append("ID" + str(i))
    metadata.append(chunk.metadata)

    i += 1 

    # adding to chromadb 

    collection.upsert(
        documents=documents,
        metadatas=metadata,
        ids=ids
    )

    if i % 50 == 0 or i == len(chunks):
        print(f"Progress: {i}/{len(chunks)} chunks ({i / len(chunks):.0%})")

print(f"Done! Collection now has {collection.count()} items.")