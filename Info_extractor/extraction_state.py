"""
Extraction State Management
Stores conversation history with thought signatures for later interactive review.
"""

import json
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
import base64


@dataclass
class ExtractionState:
    """Stores the complete extraction state including conversation history.
    
    Enables:
    1. Resuming conversations with preserved thought context
    2. Interactive review of extraction results
    3. Reproducibility for paper supplementary materials
    """
    
    study_id: str
    model_name: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    # Conversation components (serializable format)
    conversation_history: List[Dict[str, Any]] = field(default_factory=list)
    
    # Extraction results
    final_result: Dict[str, Any] = field(default_factory=dict)
    study_type: Optional[str] = None
    
    # Metadata
    pdf_paths: List[str] = field(default_factory=list)
    extraction_mode: str = "tool_calling"
    
    # Token usage for cost tracking
    token_usage: Dict[str, int] = field(default_factory=lambda: {
        "prompt_tokens": 0,
        "output_tokens": 0,
        "thoughts_tokens": 0,
        "total_tokens": 0
    })
    
    def add_turn(self, role: str, parts: List[Dict[str, Any]]):
        """Add a conversation turn to history.
        
        Args:
            role: 'user' or 'model'
            parts: List of part dictionaries (text, function_call, function_response, thought_signature)
        """
        self.conversation_history.append({
            "role": role,
            "parts": parts,
            "timestamp": datetime.now().isoformat()
        })
    
    def add_model_response(self, response_content):
        """Add model response content, preserving thought signatures.
        
        Args:
            response_content: types.Content object from Gemini response
        """
        parts = []
        
        for part in response_content.parts:
            part_dict = {}
            
            # Text content
            if hasattr(part, 'text') and part.text:
                part_dict['text'] = part.text
            
            # Function call
            if hasattr(part, 'function_call') and part.function_call:
                part_dict['function_call'] = {
                    'name': part.function_call.name,
                    'args': dict(part.function_call.args) if part.function_call.args else {}
                }
            
            # Thought signature (critical for context preservation)
            if hasattr(part, 'thought_signature') and part.thought_signature:
                # Base64 encode for JSON serialization
                part_dict['thought_signature'] = base64.b64encode(
                    part.thought_signature.encode() if isinstance(part.thought_signature, str) 
                    else part.thought_signature
                ).decode('utf-8')
            
            # Thought content (if available)
            if hasattr(part, 'thought') and part.thought:
                part_dict['thought'] = True
            
            if part_dict:
                parts.append(part_dict)
        
        self.conversation_history.append({
            "role": "model",
            "parts": parts,
            "timestamp": datetime.now().isoformat()
        })
    
    def add_tool_response(self, name: str, response: Dict[str, Any]):
        """Add tool/function response to history."""
        self.conversation_history.append({
            "role": "user",
            "parts": [{
                "function_response": {
                    "name": name,
                    "response": response
                }
            }],
            "timestamp": datetime.now().isoformat()
        })
    
    def save(self, path: Optional[str] = None) -> str:
        """Save state to JSON file.
        
        Args:
            path: Optional path. If not provided, generates from study_id.
            
        Returns:
            Path to saved file
        """
        if path is None:
            path = f"extraction_state_{self.study_id}.json"
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(asdict(self), f, ensure_ascii=False, indent=2)
        
        return path
    
    @classmethod
    def load(cls, path: str) -> "ExtractionState":
        """Load state from JSON file.
        
        Args:
            path: Path to state file
            
        Returns:
            ExtractionState instance
        """
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return cls(
            study_id=data['study_id'],
            model_name=data['model_name'],
            timestamp=data['timestamp'],
            conversation_history=data['conversation_history'],
            final_result=data['final_result'],
            study_type=data.get('study_type'),
            pdf_paths=data.get('pdf_paths', []),
            extraction_mode=data.get('extraction_mode', 'tool_calling')
        )
    
    def get_summary(self) -> str:
        """Get a brief summary of the extraction state."""
        return f"""
Extraction State Summary
========================
Study ID: {self.study_id}
Study Type: {self.study_type or 'Unknown'}
Model: {self.model_name}
Timestamp: {self.timestamp}
Conversation Turns: {len(self.conversation_history)}
PDFs Processed: {len(self.pdf_paths)}
Has Final Result: {bool(self.final_result)}
"""


def rebuild_conversation_for_gemini(state: ExtractionState) -> List:
    """Rebuild conversation history for Gemini API continuation.
    
    Args:
        state: ExtractionState with saved conversation
        
    Returns:
        List of types.Content objects for Gemini API
    """
    from google.genai import types
    
    contents = []
    
    for turn in state.conversation_history:
        parts = []
        
        for part_dict in turn['parts']:
            # Text part
            if 'text' in part_dict:
                parts.append(types.Part(text=part_dict['text']))
            
            # Function call part
            if 'function_call' in part_dict:
                fc = part_dict['function_call']
                # Create Part with function_call
                part = types.Part(
                    function_call=types.FunctionCall(
                        name=fc['name'],
                        args=fc['args']
                    )
                )
                # Restore thought signature if present
                if 'thought_signature' in part_dict:
                    sig = base64.b64decode(part_dict['thought_signature'])
                    # Thought signature is binary/encrypted, keep as-is or as base64 string
                    if hasattr(part, 'thought_signature'):
                        try:
                            part.thought_signature = sig  # Try bytes first
                        except:
                            part.thought_signature = part_dict['thought_signature']  # Use original base64
                parts.append(part)
            
            # Function response part
            if 'function_response' in part_dict:
                fr = part_dict['function_response']
                parts.append(types.Part(
                    function_response=types.FunctionResponse(
                        name=fr['name'],
                        response=fr['response']
                    )
                ))
        
        if parts:
            contents.append(types.Content(
                role=turn['role'],
                parts=parts
            ))
    
    return contents
