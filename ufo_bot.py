from langchain.llms import OpenAI
from langchain.document_loaders import DirectoryLoader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.chains.qa_with_sources import load_qa_with_sources_chain
from langchain.docstore.document import Document
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores.faiss import FAISS
import time
import requests

start_time = time.time()
user_input = input("Please enter some text: ")

loader = DirectoryLoader('../ufo-report-scraper/data/raw_month_data_converted_txt', glob="**/*.txt")
docs = loader.load()
len(docs)
2

source_chunks = []
splitter = CharacterTextSplitter(separator=" ", chunk_size=1024, chunk_overlap=0)
for source in docs:
    for chunk in splitter.split_text(source.page_content):
        source_chunks.append(Document(page_content=chunk, metadata=source.metadata))

search_index = FAISS.from_documents(source_chunks, OpenAIEmbeddings())

chain = load_qa_with_sources_chain(OpenAI(temperature=0.5))

def print_answer(question):
    print(
        chain(
            {
                "input_documents": search_index.similarity_search(question, k=4),
                "question": question,
            },
            return_only_outputs=False,
        )["output_text"]
    )
print_answer(user_input)

end_time = time.time()
run_time = end_time - start_time
print(f"Script completed in {run_time:.2f} seconds.")