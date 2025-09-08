import os
from typing import Optional, Dict
from docx import Document
from PyPDF2 import PdfReader
import nltk
from nltk.tokenize import sent_tokenize
import re

class DocumentProcessor:
    def __init__(self):
        # Download required NLTK data
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt')

    def read_document(self, file_path: str) -> Optional[str]:
        """Read document content based on file extension"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        file_extension = os.path.splitext(file_path)[1].lower()

        try:
            if file_extension == '.txt':
                with open(file_path, 'r', encoding='utf-8') as file:
                    return file.read()
            elif file_extension == '.docx':
                doc = Document(file_path)
                return '\n'.join([paragraph.text for paragraph in doc.paragraphs])
            elif file_extension == '.pdf':
                reader = PdfReader(file_path)
                return '\n'.join([page.extract_text() for page in reader.pages])
            else:
                raise ValueError(f"Unsupported file format: {file_extension}")
        except Exception as e:
            print(f"Error reading file: {str(e)}")
            return None

    def extract_metadata(self, text: str) -> Dict[str, str]:
        """Extract key metadata from the legal document"""
        metadata = {
            'parties': [],
            'dates': [],
            'amounts': [],
            'agreement_type': ''
        }
        
        # Extract agreement type
        agreement_match = re.search(r'^(.+?)\s*AGREEMENT', text, re.IGNORECASE | re.MULTILINE)
        if agreement_match:
            metadata['agreement_type'] = agreement_match.group(0).strip()

        # Extract parties
        party_matches = re.finditer(r'(?:LICENSOR|LICENSEE|PARTY A|PARTY B|SELLER|BUYER|VENDOR|CLIENT):\s*([^\n]+)', text, re.IGNORECASE)
        metadata['parties'] = [match.group(1).strip() for match in party_matches]

        # Extract dates
        date_pattern = r'\b\d{1,2}[-/]\d{1,2}[-/]\d{2,4}\b|\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{4}\b'
        metadata['dates'] = re.findall(date_pattern, text)

        # Extract monetary amounts
        amount_pattern = r'\$\s*\d+(?:,\d{3})*(?:\.\d{2})?'
        metadata['amounts'] = re.findall(amount_pattern, text)

        return metadata

    def preprocess_text(self, text: str) -> str:
        """Preprocess the text for better summarization"""
        if not text:
            return ""

        # Remove multiple newlines and spaces
        text = re.sub(r'\n+', '\n', text)
        text = re.sub(r'\s+', ' ', text)
        
        # Split into sentences
        sentences = sent_tokenize(text)
        
        # Basic preprocessing
        processed_sentences = []
        for sentence in sentences:
            # Remove extra whitespace
            cleaned = ' '.join(sentence.split())
            
            # Convert all-caps sentences to title case if they're not headings
            if sentence.isupper() and len(sentence.split()) > 3:
                cleaned = cleaned.title()
                
            # Standardize legal terms
            cleaned = re.sub(r'(?i)\b(party a|party b)\b', lambda m: m.group(1).upper(), cleaned)
            
            processed_sentences.append(cleaned)

        # Join sentences with proper spacing
        processed_text = ' '.join(processed_sentences)
        
        # Ensure section numbers are properly formatted
        processed_text = re.sub(r'(\d+\.)(\d+)', r'\1\2', processed_text)
        
        return processed_text