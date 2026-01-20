from langchain_core.output_parsers import JsonOutputParser
from llms import model, ollama_model
from prompts import query_refinement, image_query_extraction
from langchain_core.prompts import ChatPromptTemplate
import base64
from langchain_core.messages import HumanMessage
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient

embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
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


def refine(query):
    prompt = ChatPromptTemplate.from_template(query_refinement)
    chain = prompt | model
    try:
        answer = chain.invoke({"query": query})
        return answer.content
    except Exception as e:
        return {"error": f"Failed to parse: {str(e)}", "raw_query": query}


def get_result(query_text,limit=5):
    query_text = refine(query_text)
    query_vector = embedding_model.encode(query_text).tolist()
    results = client.query_points(
        collection_name="products",
        query=query_vector,
        using="dense",
        limit=limit
    ).points
    for i, point in enumerate(results, 1):
        print(f"\n--- Result {i} ---")
        print(f"Score: {point.score}")
        print(f"ID: {point.id}")
        print(f"Payload: {point.payload}")

