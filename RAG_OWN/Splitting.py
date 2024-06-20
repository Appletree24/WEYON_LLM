from langchain_text_splitters import CharacterTextSplitter

text = "This is the text I would like to chunk up. It is the example text for this exercise"

text_splitter = CharacterTextSplitter(
    chunk_size=35, chunk_overlap=0, separator='e')

print(text_splitter.create_documents([text]))
