import unittest
import os
from src.document_processor import DocumentProcessor
from src.summarizer import LegalSummarizer

class TestLegalSummarizer(unittest.TestCase):
    def setUp(self):
        self.doc_processor = DocumentProcessor()
        self.summarizer = LegalSummarizer()
        self.test_file = os.path.join('data', 'sample_agreement.txt')

    def test_document_reading(self):
        """Test if the document can be read correctly"""
        text = self.doc_processor.read_document(self.test_file)
        self.assertIsNotNone(text)
        self.assertIn("SOFTWARE LICENSE AGREEMENT", text)

    def test_document_preprocessing(self):
        """Test text preprocessing"""
        text = self.doc_processor.read_document(self.test_file)
        processed_text = self.doc_processor.preprocess_text(text)
        self.assertIsNotNone(processed_text)
        self.assertNotEqual(processed_text, '')

    def test_metadata_extraction(self):
        """Test metadata extraction functionality"""
        text = self.doc_processor.read_document(self.test_file)
        metadata = self.doc_processor.extract_metadata(text)
        
        self.assertIsInstance(metadata, dict)
        self.assertIn('agreement_type', metadata)
        self.assertIn('parties', metadata)
        self.assertIn('dates', metadata)
        self.assertIn('amounts', metadata)
        
        # Test specific content
        self.assertIn('SOFTWARE LICENSE AGREEMENT', metadata['agreement_type'])
        self.assertTrue(any('LICENSOR' in party for party in metadata['parties']))

    def test_summarization_with_metadata(self):
        """Test summarization with metadata integration"""
        text = self.doc_processor.read_document(self.test_file)
        processed_text = self.doc_processor.preprocess_text(text)
        metadata = self.doc_processor.extract_metadata(text)
        
        summary = self.summarizer.generate_summary(processed_text, metadata=metadata)
        self.assertIsNotNone(summary)
        self.assertNotEqual(summary, '')
        
        # Check for structured output
        self.assertTrue(any(heading in summary for heading in [
            "Agreement Type & Parties",
            "Key Terms & Conditions",
            "Important Dates & Deadlines"
        ]))

    def test_summary_length_limit(self):
        """Test summary length limitation"""
        text = self.doc_processor.read_document(self.test_file)
        processed_text = self.doc_processor.preprocess_text(text)
        max_length = 500
        
        summary = self.summarizer.generate_summary(processed_text, max_length=max_length)
        self.assertLessEqual(len(summary), max_length)
        self.assertIn("[Summary truncated", summary)

    def test_summarization(self):
        """Test document summarization"""
        text = self.doc_processor.read_document(self.test_file)
        processed_text = self.doc_processor.preprocess_text(text)
        summary = self.summarizer.generate_summary(processed_text)
        self.assertIsNotNone(summary)
        self.assertNotEqual(summary, '')

if __name__ == '__main__':
    unittest.main()