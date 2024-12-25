import urllib.parse
import functools

class Tools:
    def __init__(self) -> None:
        self.tool_definitions = [
            {
                "type": "function",
                "function": {
                    "name": "google_image_search",
                    "description": "Generate a Google Image search URL for the given keywords.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "keywords": {
                                "type": "string",
                                "description": "String containing space-separated search terms for the image search.",
                            }
                        },
                        "required": ["keywords"],
                    },
                },
            },
        ]

        self.names_to_functions = {
            'google_image_search': functools.partial(self.google_image_search),
        }


    def google_image_search(self, keywords: str) -> str:
        """
        Generate a Google Image search URL for the given keywords.
        Args:
            keywords (str): The search terms for the image search.
        Returns:
            str: A URL string linking to the Google Image search results.
        """
        base_url = "https://www.google.com/search"
        params = {
            "tbm": "isch",        # Specifies image search
            "q": keywords         # The search query
        }
        query_string = urllib.parse.urlencode(params)
        search_url = f"{base_url}?{query_string}"

        return search_url