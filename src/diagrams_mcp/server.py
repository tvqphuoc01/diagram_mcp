# src/diagrams_mcp/server.py
import os
import sys
from mcp.server.fastmcp import FastMCP
from typing import Dict, Any, Optional
import diagrams
import json
import logging

# internal import
from service_finder import find_services

# Add current directory to Python path for imports
sys.path.insert(0, os.path.dirname(__file__))

# Initialize FastMCP server
mcp = FastMCP("diagrams")

# Configure logging (stderr only for STDIO servers)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

package_path = os.path.dirname(diagrams.__file__)

@mcp.tool()
def search_services(
    query: str,
    provider: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Search for cloud services across all providers or within a specific provider.

    Args:
        query: Search term (e.g., "kubernetes", "database", "storage")
        provider: Optional provider filter ("aws", "azure", "gcp", "ibm", "alibabacloud")

    Returns:
        Dictionary containing matching services with their import paths and descriptions
    """

    logger.info(f"Searching for services with query: {query}, provider: {provider}")

    results = find_services(query, provider, package_path)

    return {"services": results, "count": len(results)}

if __name__ == "__main__":
    # this while is used to test service search
    '''Service search test loop
    while True:
        user_query = input("Enter service search query (or 'exit' to quit): ").strip()
        provider_query = input("Enter provider filter (or 'exit' to quit): ").strip()

        if user_query.lower() == 'exit' or provider_query.lower() == 'exit':
            break
        result = search_services(user_query, provider=provider_query)
        print(json.dumps(result, indent=2))
    '''
    mcp.run()
