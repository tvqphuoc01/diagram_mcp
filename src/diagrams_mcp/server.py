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
from code_generator import CodeGenerator
from pattern_analyze import RequirementAnalyzer
from pattern_engine import PatternMatcher

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

@mcp.tool()
def generate_diagram_code(
    description: str,
    provider_preference: Optional[str] = None,
    diagram_type: str = "basic"
) -> Dict[str, Any]:
    """Generate Python diagrams code from natural language description"""
    generator = CodeGenerator()
    code = generator.generate_from_description(
        description, provider_preference, diagram_type
    )

    return {
        "description": description,
        "generated_code": code,
        "imports_needed": generator.get_required_imports(code),
        "execution_notes": generator.get_execution_notes()
    }

@mcp.tool()
def find_architecture_patterns(
    requirements: str,
    constraints: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Find suitable architecture patterns based on requirements.

    Args:
        requirements: Description of what you're building
        constraints: Budget, compliance, performance requirements

    Returns:
        Ranked list of suitable patterns with explanations
    """

    # Analyze requirements using NLP/AI
    analyzed_needs = RequirementAnalyzer().analyze_requirements(requirements)

    # Match against pattern database
    suitable_patterns = PatternMatcher().match_patterns(analyzed_needs, constraints)

    return {
        "recommended_patterns": [
            {
                "match_score": pattern.match_score,
                "reasons": pattern.match_reasons,
                "pros": pattern.pros,
                "cons": pattern.cons,
                "estimated_cost": pattern.estimated_cost,
                "complexity": pattern.implementation_effort
            }
            for pattern in suitable_patterns
        ],
        "requirements_analysis": analyzed_needs
    }

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

    # this while is used to test diagram generation
    """
    while True:
        user_description = input("Enter diagram description (or 'exit' to quit): ").strip()
        provider_query = input("Enter provider filter (or 'exit' to quit): ").strip()

        if user_description.lower() == 'exit' or provider_query.lower() == 'exit':
            break
        result = generate_diagram_code(user_description, provider_preference=provider_query)
        print(json.dumps(result, indent=2))
    """
    mcp.run()
