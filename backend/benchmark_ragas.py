import os
import sys
import asyncio
import pandas as pd
from dotenv import load_dotenv
import nest_asyncio

# Apply nest_asyncio to allow running asyncio loops in environments that might already have one
nest_asyncio.apply()

# Setup paths and environment
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
sys.path.append(PROJECT_ROOT)
load_dotenv(os.path.join(PROJECT_ROOT, ".env"))
load_dotenv(os.path.join(PROJECT_ROOT, ".env.local"))

# Mock missing langchain_community modules before importing Ragas
import sys
from unittest.mock import MagicMock
sys.modules['langchain_community.chat_models.vertexai'] = MagicMock()
sys.modules['langchain_community.chat_models'] = MagicMock()
sys.modules['langchain_community.llms'] = MagicMock()
sys.modules['langchain_community.llms.vertexai'] = MagicMock()

# Import Ragas and Langchain components
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_precision, context_recall
from ragas.run_config import RunConfig
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_groq import ChatGroq

# Import JustorAI backend functions
from backend import (
    classify_query, 
    _embed, 
    retrieve_context, 
    format_retrieved_context, 
    call_llm_with_fallbacks, 
    get_system_prompt, 
    MODEL_CHAINS
)

def setup_ragas():
    """Configure Ragas to use Google Gemini instead of OpenAI."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("ERROR: GEMINI_API_KEY is not set.")
        sys.exit(1)
        
    openrouter_api_key = os.environ.get("OPENROUTER_API_KEY")
    if not openrouter_api_key:
        print("ERROR: OPENROUTER_API_KEY is not set.")
        sys.exit(1)

    # Use OpenRouter GPT-4o-mini to completely bypass API rate limits
    from langchain_openai import ChatOpenAI
    judge_llm = ChatOpenAI(
        model="openai/gpt-4o-mini",
        api_key=openrouter_api_key,
        base_url="https://openrouter.ai/api/v1"
    )
    
    # Use Gemini Embedding 2 for metric calculations
    judge_embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-2", google_api_key=api_key)
    
    return judge_llm, judge_embeddings

async def run_justor_query(query: str):
    """Run a query through the JustorAI pipeline and extract the answer and raw contexts."""
    print(f"Querying: '{query}'")
    
    # 1. Classify & Embed
    intent = classify_query(query)
    query_vec = _embed(query)
    
    # 2. Retrieve
    acts, dlrs = await retrieve_context(query_vec, intent)
    
    # 3. Format Context (We need the raw content for Ragas)
    formatted_context, sources = format_retrieved_context(acts, dlrs)
    
    # Extract raw text chunks for the 'contexts' field in Ragas
    raw_contexts = []
    for act in acts:
        raw_contexts.append(act.get("content", ""))
    for dlr in dlrs:
        raw_contexts.append(dlr.get("judgment_content", ""))
        
    # 4. Generate Answer (using General Public persona)
    messages = [{"role": "system", "content": get_system_prompt("General Public", formatted_context)}]
    messages.append({"role": "user", "content": query})
    
    models = MODEL_CHAINS["General Public"]
    answer, model_used = call_llm_with_fallbacks(models, messages)
    
    return answer, raw_contexts

async def main():
    print("Initializing Ragas Evaluation Benchmark...")
    judge_llm, judge_embeddings = setup_ragas()
    
    # Golden Dataset: 5 manually curated questions and ground truth answers based on the ingested laws
    golden_dataset = [
        {
            "question": "What is the penalty for breaching a contract under the Transfer of Property Act?",
            "ground_truth": "The Transfer of Property Act, 1882 primarily deals with the transfer of property by act of parties, such as sales, mortgages, leases, exchanges, and gifts. It does not prescribe criminal penalties or general damages for breaching a contract; contractual breaches are governed by the Contract Act."
        },
        {
            "question": "Can an oral transfer of property be valid under the Transfer of Property Act, 1882?",
            "ground_truth": "Under Section 9 of the Transfer of Property Act, 1882, a transfer of property may be made without writing in every case in which a writing is not expressly required by law."
        },
        {
            "question": "What happens if I try to transfer property to someone, but I attach a condition that absolutely stops them from selling it?",
            "ground_truth": "Under Section 10 of the Transfer of Property Act, 1882, a condition absolutely restraining the transferee from parting with or disposing of their interest in the property is void, except in cases of leases where it is for the benefit of the lessor."
        },
        {
            "question": "How is 'immovable property' defined in the Registration Act, 1908?",
            "ground_truth": "According to Section 2(6) of the Registration Act, 1908, 'immovable property' includes land, buildings, hereditary allowances, rights to ways, lights, ferries, fisheries or any other benefit to arise out of land, and things attached to the earth or permanently fastened to anything which is attached to the earth, but not standing timber, growing crops nor grass."
        },
        {
            "question": "Under the State Acquisition and Tenancy Act, 1950, what are the rights of a raiyat?",
            "ground_truth": "Under Section 83 of the State Acquisition and Tenancy Act, 1950, a raiyat has the right to occupy and use the land for any purpose connected with agriculture, horticulture, or pasturage, and the interest of a raiyat is heritable and transferable."
        }
    ]

    # Collect answers and contexts from the RAG pipeline
    dataset_dict = {
        "question": [],
        "answer": [],
        "contexts": [],
        "ground_truth": []
    }

    print("\n--- Phase 1: Generating Responses from JustorAI ---")
    for item in golden_dataset:
        question = item["question"]
        try:
            answer, contexts = await run_justor_query(question)
            
            # Ragas expects contexts to be a list of strings. If empty, add a placeholder to prevent crashes
            if not contexts:
                contexts = ["No context retrieved."]
                
            dataset_dict["question"].append(question)
            dataset_dict["answer"].append(answer)
            dataset_dict["contexts"].append(contexts)
            dataset_dict["ground_truth"].append(item["ground_truth"])
            
            print(f" -> Generated Answer. Retrieved {len(contexts)} context chunks.\n")
        except Exception as e:
            print(f"Error querying '{question}': {e}")

    # Convert to HuggingFace Dataset
    ragas_dataset = Dataset.from_dict(dataset_dict)
    
    print("\n--- Phase 2: Evaluating with Ragas (Gemini LLM Judge) ---")
    # Define the metrics to evaluate
    metrics = [
        faithfulness,       # Is the answer derived ONLY from the context?
        answer_relevancy,   # Does the answer actually address the question?
        context_precision,  # Did we retrieve the RIGHT context?
        context_recall      # Did we retrieve ALL the necessary context?
    ]
    
    # Setup run config to limit concurrency to avoid 429 Rate Limits
    run_config = RunConfig(max_workers=1)

    # Run evaluation
    result = evaluate(
        dataset=ragas_dataset,
        metrics=metrics,
        llm=judge_llm,
        embeddings=judge_embeddings,
        run_config=run_config
    )
    
    print("\n=== FINAL BENCHMARK SCORE ===")
    print(result)
    
    # Save detailed results
    df = result.to_pandas()
    output_file = os.path.join(PROJECT_ROOT, "ragas_results.csv")
    df.to_csv(output_file, index=False)
    print(f"\nDetailed scorecard saved to: {output_file}")

if __name__ == "__main__":
    asyncio.run(main())
