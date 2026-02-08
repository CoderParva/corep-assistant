import os
import json
from typing import Dict, List
from groq import Groq
from dotenv import load_dotenv
from src.schemas import CR1Row, CR1Template, ExposureClass, RegulatoryReference
from src.retrieval.retriever import RegulatoryRetriever

# Load environment variables
load_dotenv()

class COREPGenerator:
    """Generates structured COREP data using LLM + RAG"""
    
    def __init__(self):
        # Get API key - check Streamlit secrets first, then environment
        api_key = None
        
        try:
            import streamlit as st
            if "GROQ_API_KEY" in st.secrets:
                api_key = st.secrets["GROQ_API_KEY"]
        except:
            pass
        
        if not api_key:
            api_key = os.getenv("GROQ_API_KEY")
        
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables or Streamlit secrets")
        
        self.client = Groq(api_key=api_key)
        self.retriever = RegulatoryRetriever()
        self.model = "llama-3.3-70b-versatile"
    
    def generate_cr1_row(self, query: str) -> Dict:
        """
        Generate CR1 row from natural language query
        
        Args:
            query: User question like "£50M corporate exposures, unrated"
            
        Returns:
            Dict with CR1 row data and audit trail
        """
        
        # Step 1: Retrieve relevant regulatory context
        print("🔍 Retrieving relevant regulations...")
        retrieved_docs = self.retriever.search(query, top_k=3)
        context = self.retriever.format_context(retrieved_docs)
        
        # Step 2: Build prompt for LLM
        prompt = self._build_prompt(query, context)
        
        # Step 3: Call LLM
        print("🤖 Generating structured output...")
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a regulatory reporting expert specializing in COREP CR1 templates. Extract structured data from user queries based on PRA Rulebook guidance."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.1,
            max_tokens=1000
        )
        
        llm_output = response.choices[0].message.content
        
        # Step 4: Parse LLM output into structured format
        result = self._parse_llm_output(llm_output, retrieved_docs)
        
        return result
    
    def _build_prompt(self, query: str, context: str) -> str:
        """Build prompt for LLM"""
        prompt = f"""Based on the following PRA Rulebook excerpts, extract COREP CR1 information from the user query.

REGULATORY CONTEXT:
{context}

USER QUERY:
{query}

Extract and return ONLY a JSON object with this structure:
{{
  "exposure_class": "one of: Central governments or central banks, Institutions, Corporates, Retail, Exposures secured by mortgages on residential property, Exposures secured by mortgages on commercial immovable property",
  "original_exposure_value": <number in millions>,
  "risk_weight_percent": <integer between 0-1250>,
  "article_used": <article number>,
  "reasoning": "brief explanation of why this classification and risk weight apply"
}}

Return ONLY the JSON, no other text."""
        
        return prompt
    
    def _parse_llm_output(self, llm_output: str, retrieved_docs: List[Dict]) -> Dict:
        """Parse LLM JSON output into structured format"""
        
        try:
            # Extract JSON from response
            llm_output = llm_output.strip()
            if "```json" in llm_output:
                llm_output = llm_output.split("```json")[1].split("```")[0]
            elif "```" in llm_output:
                llm_output = llm_output.split("```")[1].split("```")[0]
            
            data = json.loads(llm_output)
            
            # Calculate RWA
            exposure = data['original_exposure_value'] * 1_000_000  # Convert to actual value
            risk_weight = data['risk_weight_percent']
            rwa = exposure * (risk_weight / 100)
            
            # Build regulatory references - use top 2 most relevant documents
            references = []
            for doc in retrieved_docs[:2]:  # Take top 2 most relevant
                references.append(RegulatoryReference(
                    article_number=doc['article_number'],
                    source=doc['source'],
                    excerpt=doc['text'][:200] + "..."
                ))
            
            # Create CR1Row
            row = CR1Row(
                exposure_class=ExposureClass(data['exposure_class']),
                original_exposure_value=exposure,
                risk_weight_percent=risk_weight,
                risk_weighted_assets=rwa,
                regulatory_references=references
            )
            
            return {
                'cr1_row': row,
                'reasoning': data.get('reasoning', ''),
                'raw_llm_output': llm_output
            }
            
        except Exception as e:
            print(f"❌ Error parsing LLM output: {e}")
            print(f"Raw output: {llm_output}")
            raise


def test_generator():
    """Test the generator with sample queries"""
    generator = COREPGenerator()
    
    test_queries = [
        "We have £50 million in unrated corporate exposures",
        "£100M in residential mortgages",
        "£200M exposure to UK central government"
    ]
    
    for query in test_queries:
        print(f"\n{'='*70}")
        print(f"Query: {query}")
        print('='*70)
        
        result = generator.generate_cr1_row(query)
        row = result['cr1_row']
        
        print(f"\n✓ Exposure Class: {row.exposure_class.value}")
        print(f"✓ Original Exposure: £{row.original_exposure_value:,.0f}")
        print(f"✓ Risk Weight: {row.risk_weight_percent}%")
        print(f"✓ RWA: £{row.risk_weighted_assets:,.0f}")
        print(f"\n📋 Reasoning: {result['reasoning']}")
        
        if row.regulatory_references:
            print(f"\n📚 Regulatory Basis:")
            for ref in row.regulatory_references:
                print(f"   • {ref.source}")

if __name__ == "__main__":
    test_generator()