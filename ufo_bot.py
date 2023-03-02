from langchain.llms import OpenAI
from langchain.document_loaders import DirectoryLoader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.chains.qa_with_sources import load_qa_with_sources_chain
from langchain.docstore.document import Document
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores.faiss import FAISS
from langchain.llms import OpenAIChat
from langchain import PromptTemplate, LLMChain
import time
import requests

start_time = time.time()
user_input = input("Please enter some text: ")

# loader = DirectoryLoader('../ufo-report-scraper/data/raw_month_data_converted_txt', glob="**/*.txt")
loader = DirectoryLoader('../ufo-report-scraper/data/raw_month_data_converted_txt_small', glob="**/*.txt")
# loader = DirectoryLoader('../../Programming/data', glob="**/*.txt")
docs = loader.load()
len(docs)
2

source_chunks = []
splitter = CharacterTextSplitter(separator=" ", chunk_size=1024, chunk_overlap=0)
# splitter = CharacterTextSplitter(separator=" ", chunk_size=240, chunk_overlap=0) # for curie
for source in docs:
    for chunk in splitter.split_text(source.page_content):
        # print(Document(page_content=chunk, metadata=source.metadata), "\n\n")
        source_chunks.append(Document(page_content=chunk, metadata=source.metadata))

search_index = FAISS.from_documents(source_chunks, OpenAIEmbeddings())

# LIST OF DIFFERENT MODELS
# chain = load_qa_with_sources_chain(OpenAI(model_name="gpt-3.5-turbo", temperature=0.5))
chain = load_qa_with_sources_chain(OpenAIChat(model_name="gpt-3.5-turbo", temperature=0.3))
# chain = load_qa_with_sources_chain(OpenAI(model_name="text-davinci-003", temperature=0.5))
# chain = load_qa_with_sources_chain(OpenAI(model_name="text-babbage-001", max_tokens="128", temperature=0.5))
# chain = load_qa_with_sources_chain(OpenAI(model_name="text-curie-001", max_tokens="1280", temperature=0.5))

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