import google.generativeai as genai
from typing import Optional, Dict
import os
from dotenv import load_dotenv
import json

class LegalSummarizer:
    def __init__(self):
        load_dotenv()
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")
        
        genai.configure(api_key=api_key)
        # Use a current Gemini model. 'gemini-pro' is deprecated on some API versions.
        # You can switch to 'gemini-1.5-pro' for higher quality if desired.
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def generate_summary(self, text: str, max_length: Optional[int] = None, metadata: Optional[Dict] = None) -> str:
        """
        Generate a structured summary of the legal document using Google's Gemini
        """
        # Include metadata in the prompt if available
        metadata_str = ""
        if metadata:
            metadata_str = "Document Metadata:\n"
            for key, value in metadata.items():
                if value:  # Only include non-empty metadata
                    metadata_str += f"- {key.title()}: {value}\n"

        prompt = f"""
        You are a legal expert. Analyze and summarize the following legal document, incorporating the provided metadata.
        
        {metadata_str}

        Legal Document:
        {text}

        Provide a structured summary with the following sections:
        1. Agreement Type & Parties
        2. Key Terms & Conditions
        3. Important Dates & Deadlines
        4. Financial Terms
        5. Critical Obligations
        6. Special Clauses & Conditions
        7. Termination & Duration
        8. Key Risks & Limitations

        Format the summary in markdown with clear headings and bullet points.
        Be concise but comprehensive, focusing on the most important legal aspects.
        """

        try:
            response = self.model.generate_content(prompt)
            summary = response.text
            
            # Add metadata section at the end if available
            if metadata and metadata.get('parties') or metadata.get('dates') or metadata.get('amounts'):
                summary += "\n\n### Quick Reference\n"
                if metadata.get('parties'):
                    summary += f"- **Parties Involved**: {', '.join(metadata['parties'])}\n"
                if metadata.get('dates'):
                    summary += f"- **Key Dates**: {', '.join(metadata['dates'])}\n"
                if metadata.get('amounts'):
                    summary += f"- **Financial Terms**: {', '.join(metadata['amounts'])}\n"
            
            return self._format_summary(summary, max_length)
        except Exception as e:
            return f"Error generating summary: {str(e)}"

    def _format_summary(self, summary: str, max_length: Optional[int] = None) -> str:
        """Format the summary and truncate if needed"""
        if max_length and len(summary) > max_length:
            # Try to truncate at a markdown section boundary
            sections = summary.split('\n\n')
            formatted_summary = ''
            
            for section in sections:
                if len(formatted_summary + section) > max_length:
                    break
                formatted_summary += section + '\n\n'
            
            return formatted_summary.strip() + "\n\n[Summary truncated due to length]"
        return summary