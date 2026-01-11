#!/usr/bin/env python3
"""
Interactive Review Script
Resume extraction conversations using saved thought signatures.
"""

import argparse
import json
import os
from pathlib import Path

from google.genai import types
from google import genai
from dotenv import load_dotenv

from extraction_state import ExtractionState, rebuild_conversation_for_gemini


def interactive_review(
    state_path: str,
    question: str,
    pdf_path: str = None,
    verbose: bool = False
) -> str:
    """Ask a follow-up question using saved extraction state.
    
    Args:
        state_path: Path to saved extraction state JSON
        question: Follow-up question to ask
        pdf_path: Optional path to PDF for additional context
        verbose: Print debug info
    
    Returns:
        Model's response text
    """
    load_dotenv()
    api_key = os.environ.get('GOOGLE_API_KEY') or os.environ.get('GEMINI_API_KEY')
    client = genai.Client(api_key=api_key)
    
    # Load saved state
    state = ExtractionState.load(state_path)
    
    if verbose:
        print(f"📂 Loaded state: {state.study_id}")
        print(f"   Model: {state.model_name}")
        print(f"   Turns: {len(state.conversation_history)}")
    
    # Rebuild conversation history
    contents = rebuild_conversation_for_gemini(state)
    
    # Optionally add PDF for additional context
    if pdf_path:
        with open(pdf_path, 'rb') as f:
            pdf_data = f.read()
        pdf_part = types.Part.from_bytes(data=pdf_data, mime_type='application/pdf')
        # Insert PDF at the beginning
        contents.insert(0, types.Content(
            role="user",
            parts=[pdf_part, types.Part(text="Here is the paper again for reference.")]
        ))
        if verbose:
            print(f"   📄 Added PDF: {pdf_path}")
    
    # Add the new question
    contents.append(types.Content(
        role="user",
        parts=[types.Part(text=question)]
    ))
    
    if verbose:
        print(f"\n❓ Question: {question}")
        print("⏳ Thinking...")
    
    # Generate response
    config = types.GenerateContentConfig(
        temperature=0,
        thinking_config=types.ThinkingConfig(thinking_level="medium"),
    )
    
    response = client.models.generate_content(
        model=state.model_name,
        contents=contents,
        config=config
    )
    
    return response.text


def main():
    parser = argparse.ArgumentParser(description="Interactive review of extraction")
    parser.add_argument("--state", "-s", required=True, help="Path to extraction state JSON")
    parser.add_argument("--question", "-q", required=True, help="Question to ask")
    parser.add_argument("--pdf", "-p", help="Optional PDF path for additional context")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    response = interactive_review(
        state_path=args.state,
        question=args.question,
        pdf_path=args.pdf,
        verbose=args.verbose
    )
    
    print("\n" + "="*60)
    print("💬 Response:")
    print("="*60)
    print(response)


if __name__ == "__main__":
    main()
