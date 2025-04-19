from Modules.retrieval import FinancialRetriever
from Modules.generation import ResponseGenerator

retriever = FinancialRetriever()
response_gen = ResponseGenerator(retriever)

# Now this should find "APPL" when you search for "Apple"
response = response_gen.generate_response("Show Apple data", "Apple")
print(response)