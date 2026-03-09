import os
from dotenv import load_dotenv
from groq import Groq
import sys

# Pre-pend the phase3 path so we can import the retriever
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'phase3_retrieval')))
from retriever import FundRetriever

class RAGGenerator:
    def __init__(self):
        # Load environment variables from the root .env file
        env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '.env'))
        print(f"LOADING ENV FROM: {env_path}")
        load_dotenv(dotenv_path=env_path)
        
        self.api_key = os.getenv("GROQ_API_KEY")
        print(f"LOADED API KEY: {('*' * 5) + str(self.api_key)[-4:] if self.api_key else 'None'}")
        
        if self.api_key:
            self.api_key = self.api_key.strip().strip("'").strip('"')
            
        if not self.api_key or self.api_key == "your_groq_api_key_here":
            print("WARNING: GROQ_API_KEY not found or is default in .env file. Please update it.")
            
        # Initialize Groq client
        self.client = Groq(api_key=self.api_key)
        
        # We will use llama-3.1-8b-instant for fast generation
        self.model = "llama-3.1-8b-instant" 
        
        # Initialize our local FAISS retriever
        self.retriever = FundRetriever(index_dir=os.path.join(os.path.dirname(__file__), '..', 'phase2_knowledge_base'))
        
        # Define the strict guardrail persona
        self.system_prompt = (
            "You are an expert Mutual Fund advisor for Indmoney. "
            "You are politely assisting a user by answering questions about mutual funds.\n\n"
            "CRITICAL INSTRUCTIONS:\n"
            "1. STRICT GROUNDING: You must NEVER answer questions using your own internal knowledge. "
            "You must ONLY use the information provided in the Context below. If the answer is not in the context, say 'I do not have enough information to answer that.'\n"
            "2. NO PII / OUT OF SCOPE: If the user asks for personal information, personal financial advice, or anything unrelated to mutual funds, "
            "you must politely and courteously refuse. You must NOT use the word 'chatbot' or 'bot'. Just explain gracefully that as a mutual fund advisor, you cannot provide that information.\n"
            "3. CITATIONS: You must heavily cite your sources. If you use information from multiple retrieved results, list all relevant 'Source URLs' at the very end of your answer."
        )

    def generate_answer(self, user_query: str) -> str:
        # 1. Retrieve Context
        retrieved_data = self.retriever.retrieve(user_query, top_k=4)
        
        # 2. Format Context
        context_block = "CONTEXT:\n"
        for i, item in enumerate(retrieved_data):
            context_block += f"--- Result {i+1} ---\n"
            context_block += f"Source URL: {item['source_url']}\n"
            context_block += f"Content: {item['content']}\n\n"
            
        print(f"--- Retrieved {len(retrieved_data)} context chunks ---")
            
        # 3. Build Messages
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": f"{context_block}\n\nUSER QUESTION: {user_query}"}
        ]
        
        # 4. Call Groq LLM
        try:
            chat_completion = self.client.chat.completions.create(
                messages=messages,
                model=self.model,
                temperature=0.0, # Zero temperature to prevent hallucination
                max_tokens=1024,
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            return f"Error connecting to Groq API: {e}"

if __name__ == "__main__":
    import sys
    # Handle UTF-8 encoding on Windows console
    if sys.stdout.encoding != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')
        
    generator = RAGGenerator()
    print("WARNING: Test will fail if GROQ_API_KEY is not set in ../.env")
    
    test_queries = [
        "What is the phone number of the CEO?", # Should be caught by PII/Out of Scope guardrail
        "Which fund has exactly a 3 year lock in?", # Standard retrieval
        "Who won the world cup in 2022?" # Out of scope / no context
    ]
    
    with open("result_log.txt", "w", encoding="utf-8") as f:
        for q in test_queries:
            f.write(f"\n======================\nQUERY: {q}\n")
            answer = generator.generate_answer(q)
            f.write(f"ANSWER:\n{answer}\n")
    print("Test finished. See result_log.txt")
