from langchain_core.output_parsers import JsonOutputParser
from App.llms import model, ollama_model
from App.prompts import query_refinement, image_query_extraction, products_choice
from langchain_core.prompts import ChatPromptTemplate
import base64
from langchain_core.messages import HumanMessage
from qdrant_client import QdrantClient,models
from App.Hybrid_Search import HybridSearcher

client = QdrantClient(url="http://localhost:6333")


def describe_image(image_path: str):
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
        response = model.invoke([message])
        return response.content
    except Exception as e:
        return f"Error describing image: {str(e)}"




class Pipeline :
    def __init__(self):
        self.hybrid_searcher = HybridSearcher(collection_name="products")
        self.prompt_refinement = ChatPromptTemplate.from_template(query_refinement)
        self.prompt_choice = ChatPromptTemplate.from_template(products_choice)
        self.chain_refinement = self.prompt_refinement | model | JsonOutputParser()
        self.chain_choice = self.prompt_choice | model


    def search (self, query,filters):
        return self.hybrid_searcher.search(query, filters)

    def refine_query(self,query):
        try:
            answer = self.chain_refinement.invoke({"query": query})
            return answer
        except Exception as e:
            return {"error": f"Failed to parse: {str(e)}", "raw_query": query}


    def make_choice(self,query,product_list):
        try:
            answer = self.chain_choice.invoke({"query": query, "product_list": product_list})
            return answer.content
        except Exception as e:
            return {"error": f"Failed to rerank products : {str(e)}", "raw_query": query}

    def pipeline(self,query):
        refined_query = self.refine_query(query)
        query_filter = models.Filter(
            should=[
                models.FieldCondition(
                    key="discounted_price",
                    range=models.Range(lte=refined_query["filters"]["max_price"]),
                )
            ],
        )
        preliminary_results = self.search(query,query_filter)
        result = self.make_choice(query,preliminary_results)
        return result



