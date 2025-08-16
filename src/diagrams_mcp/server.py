# src/diagrams_mcp/server.py
import os
from mcp.server.fastmcp import FastMCP
from typing import List, Dict, Any, Optional
import diagrams  # pip-installed package
import json
import logging

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
    category: Optional[str] = None
) -> Dict[str, Any]:
    """
    Search for cloud services across all providers or within a specific provider.

    Args:
        query: Search term (e.g., "kubernetes", "database", "storage")
        provider: Optional provider filter ("aws", "azure", "gcp", "ibm", "alibabacloud")
        category: Optional category filter ("compute", "database", "network", "security")

    Returns:
        Dictionary containing matching services with their import paths and descriptions
    """

    # search logic for services
    logger.info(f"Searching for services with query: {query}, provider: {provider}, category: {category}")

    # list all resource in diagrams
    # each resource will be the name of folder in resource of diagram
    all_services = []
    for root, dirs, files in os.walk(package_path):
        for name in dirs:
            all_services.append(name)

    logger.info(f"Found services: {all_services}")

    if query:
        all_services = [s for s in all_services if query in s.lower()]
        logger.info(f"Filtered services: {all_services}")
    return {"services": all_services, "count": len(all_services)}

if __name__ == "__main__":
    mcp.run()
