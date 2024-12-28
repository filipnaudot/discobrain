
import os
import json

import requests
import pytest
from unittest.mock import patch, MagicMock
from backend.tools import Tools

# Test fixture for Tools instance
@pytest.fixture
def tools_instance():
    return Tools()

# Test for successful API key loading
def test_api_key_loading():
    assert os.getenv('BRAVE_SEARCH_API_KEY') is not None, "Environment variable BRAVE_SEARCH_API_KEY is not set."

# Test for brave_web_search with a valid query
@patch('backend.tools.requests.get')
def test_brave_web_search_success(mock_get, tools_instance):
    # Mocked response data
    mock_response_data = {
        'web': {
            'results': [
                {'title': 'Result 1', 'description': 'Snippet 1', 'url': 'http://example.com/1'},
                {'title': 'Result 2', 'description': 'Snippet 2', 'url': 'http://example.com/2'},
            ],
            'total': 2
        }
    }

    # Configure the mock to return a response with JSON data
    mock_response = MagicMock()
    mock_response.json.return_value = mock_response_data
    mock_response.status_code = 200
    mock_get.return_value = mock_response

    query = "test query"
    result = tools_instance.brave_web_search(query)
    result_dict = json.loads(result)

    assert result_dict["query"] == query
    assert len(result_dict["results"]) == 2
    assert result_dict["results"][0]["title"] == "Result 1"

# Test for missing API key
def test_brave_web_search_missing_api_key(tools_instance):
    with patch('backend.tools.BRAVE_API_KEY', None):
        result = tools_instance.brave_web_search("test query")
        assert "error" in result
        assert result["error"] == "Brave Search API key not found in environment variables."

# Test for HTTPError handling
@patch('backend.tools.requests.get')
def test_brave_web_search_http_error(mock_get, tools_instance):
    mock_get.side_effect = requests.exceptions.HTTPError("HTTP error occurred")

    result = tools_instance.brave_web_search("test query")
    assert "error" in result
    assert "HTTP error occurred" in result["error"]

# Test for connection error handling
@patch('backend.tools.requests.get')
def test_brave_web_search_connection_error(mock_get, tools_instance):
    mock_get.side_effect = requests.exceptions.ConnectionError()

    result = tools_instance.brave_web_search("test query")
    assert "error" in result
    assert "Connection error occurred" in result["error"]

# Test for timeout error handling
@patch('backend.tools.requests.get')
def test_brave_web_search_timeout_error(mock_get, tools_instance):
    mock_get.side_effect = requests.exceptions.Timeout()

    result = tools_instance.brave_web_search("test query")
    assert "error" in result
    assert "The request to Brave Search API timed out." in result["error"]

# Test for request exception handling
@patch('backend.tools.requests.get')
def test_brave_web_search_request_exception(mock_get, tools_instance):
    mock_get.side_effect = requests.exceptions.RequestException("General request error")

    result = tools_instance.brave_web_search("test query")
    assert "error" in result
    assert "An error occurred: General request error" in result["error"]

# Test for JSON decoding failure
@patch('backend.tools.requests.get')
def test_brave_web_search_json_error(mock_get, tools_instance):
    mock_response = MagicMock()
    mock_response.json.side_effect = ValueError("Invalid JSON")
    mock_get.return_value = mock_response

    result = tools_instance.brave_web_search("test query")
    assert "error" in result
    assert "Failed to parse JSON response" in result["error"]
