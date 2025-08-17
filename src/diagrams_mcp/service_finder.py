import os
import re
import logging
from typing import List, Dict, Any, Optional
import diagrams

logger = logging.getLogger(__name__)

def find_services(
    query: str,
    provider: Optional[str] = None,
    package_path: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Find services in the diagrams package based on query and provider filters.

    Args:
        query: Search term to match against class names
        provider: Optional provider filter ("aws", "azure", "gcp", etc.)
        package_path: Path to diagrams package (defaults to diagrams.__file__ location)

    Returns:
        List of dictionaries containing service information
    """
    if package_path is None:
        package_path = os.path.dirname(diagrams.__file__)

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
    return results
