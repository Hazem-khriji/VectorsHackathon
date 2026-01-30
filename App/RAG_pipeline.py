from langchain_core.output_parsers import JsonOutputParser
from App.llms import model, ollama_model, vision_model
from App.prompts import query_refinement, image_query_extraction, products_choice
from langchain_core.prompts import ChatPromptTemplate
import base64
from langchain_core.messages import HumanMessage
from qdrant_client import QdrantClient,models
from App.Hybrid_Search import HybridSearcher
import os

client = QdrantClient(
    url=os.getenv("QDRANT_URL", "http://localhost:6333"),
    api_key=os.getenv("QDRANT_API_KEY")
)

class Pipeline :
    def __init__(self):
        self.hybrid_searcher = HybridSearcher(collection_name="products")
        self.prompt_refinement = ChatPromptTemplate.from_template(query_refinement)
        self.prompt_choice = ChatPromptTemplate.from_template(products_choice)
        self.chain_refinement = self.prompt_refinement | model | JsonOutputParser()
        self.chain_choice = self.prompt_choice | model

    def describe_image(self, image_path: str):
        with open(image_path, "rb") as image_file:
            image_data = base64.b64encode(image_file.read()).decode("utf-8")

        message = HumanMessage(
            content=[
                {"type": "text", "text": image_query_extraction},
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{image_data}"},
                },
            ]
        )

        try:
            # Use the vision model for image description
            print("DEBUG: Invoking vision model...")
            response = vision_model.invoke([message])
            print(f"DEBUG: Vision response: {response}")
            return response.content
        except Exception as e:
            print(f"DEBUG: Vision Model Error: {e}")
            import traceback
            traceback.print_exc()
            return ""

    def search (self, query,filters):
        return self.hybrid_searcher.search(query, filters)

    def refine_query(self,query):
        try:
            answer = self.chain_refinement.invoke({"query": query})
            return answer
        except Exception as e:
            return {"filters": {}, "error": f"Failed to parse: {str(e)}"}

    def make_choice(self,query,product_list):
        try:
            answer = self.chain_choice.invoke({"query": query, "product_list": product_list})
            return answer.content
        except Exception as e:
            return f"I encountered an error analyzing the products: {str(e)}. However, here are the search results potentially relevant to: {query}"

    def pipeline(self,query:str,image_path:str=None):
        if(image_path):
            try:
                query += self.describe_image(image_path)
            except Exception as e:
                query = query
        refined_query = self.refine_query(query)
        try:
            query_filter = models.Filter(
                should=[
                    models.FieldCondition(
                        key="discounted_price",
                        range=models.Range(lte=refined_query["filters"]["max_price"]),
                    )
                ],
            )
        except Exception as e:
            query_filter = None
        preliminary_results = self.search(query,query_filter)
        result = self.make_choice(query,preliminary_results)
        return result



