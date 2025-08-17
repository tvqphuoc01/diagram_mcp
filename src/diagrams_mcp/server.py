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

    results = []
    for root, dirs, files in os.walk(package_path):
        for file in files:
            if file.endswith('.py') and not file.startswith('__'):
                # Check provider and category in the path
                rel_path = os.path.relpath(root, package_path)
                path_parts = rel_path.split(os.sep)
                # Provider is usually the first folder under diagrams/resources
                service_provider = path_parts[0] if len(path_parts) > 0 else ""
                service_category = path_parts[1] if len(path_parts) > 1 else ""
                # Filter by provider and category if specified
                logger.debug(f"Processing file: {file}, provider: {service_provider}, category: {service_category}")
                if provider and provider.lower() != service_provider.lower():
                    continue
                logger.info(f"Processing file: {file}, provider: {service_provider}, category: {service_category}")

                # Parse file content to extract classes
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # Extract class definitions - updated regex pattern
                    import re
                    class_pattern = r'class\s+(\w+)\([^)]*\):\s*\n\s*_icon\s*=\s*["\']([^"\']+)["\']'
                    logger.debug(f"Parsing file: {file_path} for classes matching pattern: {class_pattern}")
                    matches = re.findall(class_pattern, content, re.MULTILINE)

                    for class_name, icon_file in matches:
                        # Apply query filter if specified
                        if query and query.lower() not in class_name.lower():
                            continue

                        # Build icon path
                        icon_dir = f"resources/{service_provider}/{service_category}"
                        icon_full_path = os.path.join(package_path, "..", "..", icon_dir, icon_file)
                        icon_exists = os.path.exists(icon_full_path)

                        results.append({
                            "name": class_name,
                            "provider": service_provider,
                            "category": service_category,
                            "location": os.path.join(rel_path, file),
                            "icon": icon_file,
                            "icon_path": icon_full_path if icon_exists else None,
                            "import_path": f"diagrams.{rel_path.replace(os.sep, '.')}.{class_name}"
                        })

                except Exception as e:
                    logger.warning(f"Error parsing file {file_path}: {e}")
                    continue

    logger.info(f"Found {len(results)} matching services")
    return {"services": results, "count": len(results)}

if __name__ == "__main__":
    # this while is used to test service search
    '''
    while True:
        user_query = input("Enter service search query (or 'exit' to quit): ").strip()
        provider_query = input("Enter provider filter (or 'exit' to quit): ").strip()
        category_query = input("Enter category filter (or 'exit' to quit): ").strip()

        if user_query.lower() == 'exit' or provider_query.lower() == 'exit' or category_query.lower() == 'exit':
            break
        result = search_services(user_query, provider=provider_query)
        print(json.dumps(result, indent=2))
    '''
    mcp.run()
