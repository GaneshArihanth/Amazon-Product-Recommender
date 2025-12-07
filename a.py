from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate

# Initialize LLM
llm = OllamaLLM(model="mistral", device="cuda")  # GPU if available

# Define a prompt template
template_str = "You are a helpful assistant. Answer concisely:\n{user_input}"
prompt = ChatPromptTemplate.from_template(template_str)

# Create chain
chain = prompt | llm

# Example invocation
user_query = "Summarize blue led 300 words"
response = chain.invoke({"user_input": user_query})

print("Mistral Response:", response)
