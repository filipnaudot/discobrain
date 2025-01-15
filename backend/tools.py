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
                    "name": "search_the_web",
                    "description": "Perform a web search using a search engine API and return results.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "The space-separated search query."},
                            "video": {"type": "boolean", "description": "Whether to return only videos (true) or all types of results (false)."},
                        },
                        "required": ["query", "video"],
                    },
                },
            },
        ]

        self.names_to_functions = {
            'search_the_web': functools.partial(self.search_the_web),
        }


    def search_the_web(self, query: str, video: bool = False) -> dict:
        """
        Perform a web or video search using the Brave Search API and return results.

        Args:
            query (str): The search query.
            video (bool): If True, perform a video search; otherwise, perform a web search.

        Returns:
            dict: A dictionary containing the search query, results, and total number of results.
        """

        if not BRAVE_API_KEY:
            return {"error": "Brave Search API key not found in environment variables."}

        # Define the Brave Search API endpoint
        api_endpoint = "https://api.search.brave.com/res/v1/videos/search" if video else "https://api.search.brave.com/res/v1/web/search"
        headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            "X-Subscription-Token": BRAVE_API_KEY
        }
        params = {
            "q": query,
            "count": 5,
            "safesearch": "moderate"
        }
        if not video:
            params["extra_snippets"] = True

        try:
            response = requests.get(api_endpoint, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            # Extract and format the search results
            results = []
            if video:
                for item in data.get('results', []):
                    result = {
                        "title": item.get('title'),
                        "description": item.get('description'),
                        "url": item.get('url'),
                        "age": item.get('age'),
                        "duration": item.get('video', {}).get('duration'),
                        "views": item.get('video', {}).get('views'),
                    }
                    results.append(result)
            else:
                for item in data.get('web', {}).get('results', []):
                    result = {
                        "title": item.get('title'),
                        "description": item.get('description'),
                        "url": item.get('url'),
                        "age": item.get('age'),
                        "extra_snippets": item.get('extra_snippets')
                    }
                    results.append(result)

            return {
                "query": query,
                "results": results,
                "total_results": len(results)
            }

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
        


if __name__ == "__main__":
    # This is used for development purposes
    tools = Tools()
    result = tools.search_the_web("Paris", video=False)
    print(f"\n{result}")