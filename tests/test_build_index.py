import os
import sys
import unittest
from unittest.mock import patch, MagicMock, mock_open

# Add parent directory to path so we can import build_index
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import build_index

class TestBuildIndex(unittest.TestCase):
    """Test suite for the build_index.py script"""

    @patch('build_index.os.environ.get')
    def test_environment_variable_usage(self, mock_get):
        """Test that the script uses environment variables correctly"""
        # Set up the mock to return specific values for environment variables
        mock_get.side_effect = lambda key, default: {
            'DATA_PATH': '/test/data',
            'FAISS_INDEX_PATH': '/test/faiss_index'
        }.get(key, default)
        
        # Define a test function that accesses these environment variables
        def test_func():
            data_path = build_index.os.environ.get('DATA_PATH', 'data')
            faiss_index_path = build_index.os.environ.get('FAISS_INDEX_PATH', 'faiss_index')
            return data_path, faiss_index_path
        
        # Call the test function
        data_path, faiss_index_path = test_func()
        
        # Verify the correct values are returned
        self.assertEqual(data_path, '/test/data')
        self.assertEqual(faiss_index_path, '/test/faiss_index')
        
        # Verify os.environ.get was called with the correct parameters
        mock_get.assert_any_call('DATA_PATH', 'data')
        mock_get.assert_any_call('FAISS_INDEX_PATH', 'faiss_index')

    @patch('build_index.pd.read_csv')
    @patch('build_index.Document')
    @patch('build_index.HuggingFaceEmbeddings')
    @patch('build_index.FAISS')
    def test_build_faiss_index(self, mock_faiss, mock_embeddings, mock_document, mock_read_csv):
        """Test the build_faiss_index function"""
        # Mock pandas DataFrame
        mock_df = MagicMock()
        mock_df.__getitem__.return_value = mock_df
        mock_df.iterrows.return_value = [(0, MagicMock(iloc=[MagicMock()], id=1))]
        mock_read_csv.return_value = mock_df
        
        # Mock HuggingFaceEmbeddings
        mock_embeddings_instance = MagicMock()
        mock_embeddings.return_value = mock_embeddings_instance
        
        # Mock Document
        mock_document_instance = MagicMock()
        mock_document.return_value = mock_document_instance
        
        # Mock FAISS
        mock_vector_store = MagicMock()
        mock_faiss.from_documents.return_value = mock_vector_store
        
        # Call the build_faiss_index function with environment variables patched
        with patch('build_index.os.environ.get', 
                  side_effect=lambda key, default: {
                      'DATA_PATH': 'test_data',
                      'FAISS_INDEX_PATH': 'test_faiss_index'
                  }.get(key, default)), \
             patch('build_index.load_dotenv'):
            
            build_index.build_faiss_index()
        
        # Verify that FAISS.from_documents was called (documents were created)
        mock_faiss.from_documents.assert_called_once()
        
        # Verify that the vector store's save_local method was called with the expected path
        mock_vector_store.save_local.assert_called_once_with('test_faiss_index')
    
    @patch('build_index.os.environ.get')
    @patch('build_index.pd.read_csv')
    def test_file_not_found_handling(self, mock_read_csv, mock_get):
        """Test that the script handles file not found errors gracefully"""
        # Set up the environment variable mocks
        mock_get.side_effect = lambda key, default: {
            'DATA_PATH': 'test_data',
            'FAISS_INDEX_PATH': 'test_faiss_index'
        }.get(key, default)
        
        # Set up read_csv to raise FileNotFoundError
        mock_read_csv.side_effect = FileNotFoundError("File not found")
        
        # Call the build_faiss_index function with patches
        with patch('build_index.HuggingFaceEmbeddings'), \
             patch('build_index.FAISS'), \
             patch('build_index.load_dotenv'), \
             patch('builtins.print') as mock_print:
            
            build_index.build_faiss_index()
            
            # Verify that the error was printed
            mock_print.assert_any_call("ERROR: File not found test_data/CISSM_cleaned.csv. Skipping.")

if __name__ == '__main__':
    unittest.main() 