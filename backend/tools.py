import os
import requests
from typing import Dict, Any
import functools
import json

from dotenv import load_dotenv

# Load environment variables
load_dotenv()
BRAVE_API_KEY = os.getenv('BRAVE_SEARCH_API_KEY')


class Tools:
    def __init__(self) -> None:
        self.tool_definitions = [
            {
                "type": "function",
                "function": {
                    "name": "brave_web_search",
                    "description": "Perform a web search using the Brave Search API and return results.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The space separated search query.",
                            }
                        },
                        "required": ["query"],
                    },
                },
            },
        ]

        self.names_to_functions = {
            'brave_web_search': functools.partial(self.brave_web_search),
        }


    def brave_web_search(self, query: str) -> str:
        """
        Perform a web search using the Brave Search API and return results.

        Args:
            query (str): The search query.

        Returns:
            dict: A dictionary containing the search query, results, and total number of results,
                or an error message in case of failure.
        """
        if not BRAVE_API_KEY:
            return {"error": "Brave Search API key not found in environment variables."}
        
        # Define the Brave Search API endpoint
        api_endpoint = "https://api.search.brave.com/res/v1/web/search"
        headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            "X-Subscription-Token": BRAVE_API_KEY
        }
        params = {
            "q": query,
            "count": 4,
            "safesearch": "off",
        }

        try:
            response = requests.get(api_endpoint, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            # Extract and format the search results
            results = []
            for item in data.get('web', {}).get('results', []):
                result = {
                    "title": item.get('title'),
                    "snippet": item.get('description'),
                    "url": item.get('url'),
                }
                results.append(result)

            return json.dumps({
                "query": query,
                "results": results,
                "total_results": data.get('web', {}).get('total', len(results))
            }, indent=4)

        except requests.exceptions.HTTPError as http_err:
            return {"error": f"HTTP error occurred: {http_err}"}
        except requests.exceptions.ConnectionError:
            return {"error": "Connection error occurred while trying to reach Brave Search API."}
        except requests.exceptions.Timeout:
            return {"error": "The request to Brave Search API timed out."}
        except requests.exceptions.RequestException as req_err:
            return {"error": f"An error occurred: {req_err}"}
        except ValueError:
            return {"error": "Failed to parse JSON response from Brave Search API."}