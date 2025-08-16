# src/diagrams_mcp/server.py
from mcp.server.fastmcp import FastMCP
from typing import List, Dict, Any, Optional
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
    # Implementation will be added in Phase 2
    return {
        "services": []
    }

if __name__ == "__main__":
    mcp.run()
