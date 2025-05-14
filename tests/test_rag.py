import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# Add parent directory to path so we can import RAG
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from RAG import ChatBot

class TestChatBot(unittest.TestCase):
    """Test suite for the ChatBot class in RAG.py"""

    @patch('RAG.HuggingFaceEmbeddings')
    @patch('RAG.FAISS')
    def test_init_and_load_faiss_index(self, mock_faiss, mock_embeddings):
        """Test ChatBot initialization and FAISS index loading"""
        # Mock the FAISS.load_local method to return a mock index
        mock_index = MagicMock()
        mock_faiss.load_local.return_value = mock_index
        
        # Create a ChatBot instance
        chatbot = ChatBot()
        
        # Verify the ChatBot has the expected attributes
        self.assertEqual(chatbot.model_name, 'sentence-transformers/all-mpnet-base-v2')
        self.assertEqual(chatbot.k, 5)
        
        # Verify load_faiss_index was called with the correct parameters
        mock_faiss.load_local.assert_called_once()
        
        # Verify the FAISS index was set
        self.assertEqual(chatbot.faiss_index, mock_index)
    
    @patch('RAG.HuggingFaceEmbeddings')
    @patch('RAG.FAISS')
    def test_busca_contexto(self, mock_faiss, mock_embeddings):
        """Test the context search functionality"""
        # Create a mock for the similarity_search method
        mock_index = MagicMock()
        mock_faiss.load_local.return_value = mock_index
        
        # Create mock results
        mock_doc1 = MagicMock()
        mock_doc1.page_content = "Test context 1"
        mock_doc2 = MagicMock()
        mock_doc2.page_content = "Test context 2"
        
        # Set the return value for similarity_search
        mock_index.similarity_search.return_value = [mock_doc1, mock_doc2]
        
        # Create a ChatBot instance
        chatbot = ChatBot()
        
        # Call busca_contexto
        result = chatbot.busca_contexto("test query")
        
        # Verify similarity_search was called with correct parameters
        mock_index.similarity_search.assert_called_once_with("test query", k=5)
        
        # Verify the correct context is returned
        self.assertEqual(result, ["Test context 1", "Test context 2"])
    
    @patch('RAG.HuggingFaceEmbeddings')
    @patch('RAG.FAISS')
    @patch('RAG.Groq')
    def test_llama_response(self, mock_groq, mock_faiss, mock_embeddings):
        """Test the LLM response functionality with mocked Groq client"""
        # Create a mock for the FAISS index
        mock_index = MagicMock()
        mock_faiss.load_local.return_value = mock_index
        
        # Mock busca_contexto to return a specific context
        mock_index.similarity_search.return_value = [
            MagicMock(page_content="Test context")
        ]
        
        # Mock the Groq client's chat.completions.create method
        mock_client = MagicMock()
        mock_groq.return_value = mock_client
        
        mock_completion = MagicMock()
        mock_completion.choices = [MagicMock()]
        mock_completion.choices[0].message.content = "Test response"
        mock_client.chat.completions.create.return_value = mock_completion
        
        # Set environment variable for test
        os.environ['GROQ_API_KEY'] = 'test_key'
        
        # Create a ChatBot instance
        chatbot = ChatBot()
        
        # Call llamaResponse
        response = chatbot.llamaResponse("test query")
        
        # Verify Groq client was initialized with the API key
        mock_groq.assert_called_once_with(api_key='test_key')
        
        # Verify chat.completions.create was called
        mock_client.chat.completions.create.assert_called_once()
        
        # Verify the correct response is returned
        self.assertEqual(response, "Test response")
    
    def test_error_handling_no_api_key(self):
        """Test error handling when no API key is provided"""
        # Remove GROQ_API_KEY from environment
        if 'GROQ_API_KEY' in os.environ:
            del os.environ['GROQ_API_KEY']
        
        # Create a ChatBot instance with mocked FAISS
        with patch('RAG.HuggingFaceEmbeddings'), patch('RAG.FAISS'):
            chatbot = ChatBot()
            
            # Test that llamaResponse raises ValueError when API key is missing
            with self.assertRaises(ValueError):
                chatbot.llamaResponse("test query")

if __name__ == '__main__':
    unittest.main() 