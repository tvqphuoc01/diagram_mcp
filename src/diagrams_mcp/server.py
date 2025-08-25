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
from diagram_generator import MultiDiagramService

# Add current directory to Python path for imports
sys.path.insert(0, os.path.dirname(__file__))

# Initialize FastMCP server
mcp = FastMCP("diagrams")

# Initialize the multi-diagram service
multi_diagram_service = MultiDiagramService()

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

@mcp.tool()
def generate_sequence_diagram(
    description: str,
    output_format: str = "mermaid",
    title: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generate a sequence diagram from a natural language description.

    Args:
        description: Natural language description of the interaction flow
                    Example: "User logs in, system validates credentials, database returns user data"
        output_format: Output format - "mermaid", "plantuml", or "python_diagrams" (default: "mermaid")
        title: Optional custom title for the diagram

    Returns:
        Dictionary with generated diagram code and metadata
    """
    try:
        result = multi_diagram_service.generate_diagram(
            description=description,
            diagram_type="sequence",
            output_format=output_format,
            title=title
        )

        if result.get("success"):
            return {
                "success": True,
                "diagram_type": "sequence",
                "title": result["title"],
                "description": description,
                "generated_code": result["diagram_code"],
                "output_format": output_format,
                "metadata": {
                    "actors_found": result["spec"]["elements"],
                    "interactions_found": result["spec"]["connections"],
                    "parsing_method": "natural_language"
                },
                "usage_instructions": _get_usage_instructions(output_format),
                "example_rendering": f"Copy the generated {output_format} code to visualize the sequence diagram"
            }
        else:
            return {
                "success": False,
                "error": result.get("error"),
                "supported_formats": result.get("supported_formats", ["mermaid", "plantuml", "python_diagrams"]),
                "suggestions": [
                    "Try describing the flow step by step",
                    "Include actors like 'user', 'system', 'database'",
                    "Use action words like 'sends', 'receives', 'validates'"
                ]
            }

    except Exception as e:
        logger.error(f"Error generating sequence diagram: {e}")
        return {
            "success": False,
            "error": f"Failed to generate sequence diagram: {str(e)}",
            "description": description,
            "troubleshooting": [
                "Check that the description includes interactions between actors",
                "Try using simpler language",
                "Ensure the description follows a logical flow"
            ]
        }

@mcp.tool()
def generate_flowchart(
    description: str,
    output_format: str = "mermaid",
    title: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generate a flowchart from a process description.

    Args:
        description: Natural language description of a process or workflow
                    Example: "User places order, check inventory, if available process payment, send confirmation"
        output_format: Output format - "mermaid" or "python_diagrams" (default: "mermaid")
        title: Optional custom title for the flowchart

    Returns:
        Dictionary with generated flowchart code and metadata
    """
    try:
        result = multi_diagram_service.generate_diagram(
            description=description,
            diagram_type="flowchart",
            output_format=output_format,
            title=title
        )

        if result.get("success"):
            return {
                "success": True,
                "diagram_type": "flowchart",
                "title": result["title"],
                "description": description,
                "generated_code": result["diagram_code"],
                "output_format": output_format,
                "metadata": {
                    "process_steps": result["spec"]["elements"],
                    "decision_points": result["spec"]["connections"],
                    "complexity": "simple" if result["spec"]["elements"] < 5 else "moderate"
                },
                "usage_instructions": _get_usage_instructions(output_format),
                "process_optimization_tips": [
                    "Consider parallel processes for efficiency",
                    "Add error handling steps",
                    "Include validation checkpoints"
                ]
            }
        else:
            return {
                "success": False,
                "error": result.get("error"),
                "supported_formats": result.get("supported_formats", ["mermaid", "python_diagrams"]),
                "suggestions": [
                    "Describe the process step by step",
                    "Include decision points with 'if/then' statements",
                    "Use numbered steps or sequence words like 'first', 'then', 'finally'"
                ]
            }

    except Exception as e:
        logger.error(f"Error generating flowchart: {e}")
        return {
            "success": False,
            "error": f"Failed to generate flowchart: {str(e)}",
            "description": description,
            "troubleshooting": [
                "Ensure the description includes clear process steps",
                "Add decision points for branching logic",
                "Use action-oriented language"
            ]
        }

@mcp.tool()
def generate_class_diagram(
    description: str,
    output_format: str = "mermaid",
    title: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generate a class diagram from a domain model description.

    Args:
        description: Natural language description of entities and their relationships
                    Example: "User has name and email, User creates Orders, Order contains Products"
        output_format: Output format - "mermaid", "plantuml", or "python_diagrams" (default: "mermaid")
        title: Optional custom title for the class diagram

    Returns:
        Dictionary with generated class diagram code and metadata
    """
    try:
        result = multi_diagram_service.generate_diagram(
            description=description,
            diagram_type="class",
            output_format=output_format,
            title=title
        )

        if result.get("success"):
            return {
                "success": True,
                "diagram_type": "class",
                "title": result["title"],
                "description": description,
                "generated_code": result["diagram_code"],
                "output_format": output_format,
                "metadata": {
                    "classes_identified": result["spec"]["elements"],
                    "relationships_found": result["spec"]["connections"],
                    "domain_complexity": "simple" if result["spec"]["elements"] < 4 else "complex"
                },
                "usage_instructions": _get_usage_instructions(output_format),
                "design_suggestions": [
                    "Consider adding interfaces for better abstraction",
                    "Review relationships for proper cardinality",
                    "Add key business methods to classes"
                ]
            }
        else:
            return {
                "success": False,
                "error": result.get("error"),
                "supported_formats": result.get("supported_formats", ["mermaid", "plantuml", "python_diagrams"]),
                "suggestions": [
                    "Describe entities/classes and their properties",
                    "Include relationships like 'has', 'contains', 'inherits from'",
                    "Mention key attributes and behaviors"
                ]
            }

    except Exception as e:
        logger.error(f"Error generating class diagram: {e}")
        return {
            "success": False,
            "error": f"Failed to generate class diagram: {str(e)}",
            "description": description,
            "troubleshooting": [
                "Describe entities and their attributes clearly",
                "Include relationships between entities",
                "Use object-oriented terminology"
            ]
        }

@mcp.tool()
def generate_diagram(
    description: str,
    diagram_type: str,
    output_format: str = "mermaid",
    title: Optional[str] = None
) -> Dict[str, Any]:
    """
    Universal diagram generator - automatically creates the appropriate diagram type.

    Args:
        description: Natural language description of what to diagram
        diagram_type: Type of diagram - "sequence", "flowchart", "class", or "architecture"
        output_format: Output format (varies by diagram type)
        title: Optional custom title

    Returns:
        Dictionary with generated diagram code and metadata
    """

    # Route to appropriate specialized function
    if diagram_type.lower() == "sequence":
        return generate_sequence_diagram(description, output_format, title)
    elif diagram_type.lower() == "flowchart":
        return generate_flowchart(description, output_format, title)
    elif diagram_type.lower() == "class":
        return generate_class_diagram(description, output_format, title)
    elif diagram_type.lower() == "architecture":
        # Route to existing architecture diagram generation
        return generate_diagram_code(description, None, "basic")  # Assuming this exists
    else:
        return {
            "success": False,
            "error": f"Unsupported diagram type: {diagram_type}",
            "supported_types": [
                "sequence - For interaction flows and workflows",
                "flowchart - For process flows and decision trees",
                "class - For entity relationships and domain models",
                "architecture - For infrastructure and system diagrams"
            ],
            "examples": {
                "sequence": "User authentication flow with multiple systems",
                "flowchart": "Order processing workflow with decisions",
                "class": "E-commerce domain model with entities",
                "architecture": "3-tier web application infrastructure"
            }
        }

@mcp.tool()
def get_diagram_capabilities() -> Dict[str, Any]:
    """
    Get information about all supported diagram types and their capabilities.

    Returns:
        Dictionary with supported diagram types, formats, and usage guidance
    """
    try:
        supported_types = multi_diagram_service.get_supported_types_and_formats()

        return {
            "supported_diagram_types": {
                "sequence": {
                    "description": "Show interactions between actors/systems over time",
                    "use_cases": ["API workflows", "User journeys", "System interactions", "Process flows"],
                    "formats": supported_types.get("sequence", ["mermaid", "plantuml"]),
                    "example_input": "User logs in, frontend validates with backend, backend checks database"
                },
                "flowchart": {
                    "description": "Visualize process flows and decision trees",
                    "use_cases": ["Business processes", "Algorithms", "Decision workflows", "User flows"],
                    "formats": supported_types.get("flowchart", ["mermaid"]),
                    "example_input": "Customer places order, check inventory, if available process payment"
                },
                "class": {
                    "description": "Show entity relationships and system structure",
                    "use_cases": ["Domain models", "Database schemas", "OOP design", "System architecture"],
                    "formats": supported_types.get("class", ["mermaid", "plantuml"]),
                    "example_input": "User has name and email, User creates Orders, Order contains Products"
                },
                "architecture": {
                    "description": "Infrastructure and system component diagrams",
                    "use_cases": ["Cloud architecture", "System design", "Infrastructure planning"],
                    "formats": ["python_diagrams"],
                    "example_input": "3-tier web application with load balancer, web servers, and database"
                }
            },
            "output_formats": {
                "mermaid": {
                    "description": "Web-friendly format, supported by GitHub, GitLab, and many documentation tools",
                    "best_for": "Documentation, web embedding, collaborative editing"
                },
                "plantuml": {
                    "description": "Enterprise-standard format with detailed control and styling options",
                    "best_for": "Professional documentation, complex diagrams, enterprise tools"
                },
                "python_diagrams": {
                    "description": "Generates Python code using the diagrams library",
                    "best_for": "Infrastructure as code, automated generation, programmatic creation"
                }
            },
            "tips": {
                "sequence_diagrams": [
                    "Include clear actors (user, system, database)",
                    "Describe interactions step by step",
                    "Use action words like 'sends', 'receives', 'validates'"
                ],
                "flowcharts": [
                    "Number your steps or use sequence words",
                    "Include decision points with conditions",
                    "Describe the complete process from start to end"
                ],
                "class_diagrams": [
                    "Mention entities and their attributes",
                    "Include relationships like 'has', 'contains', 'inherits'",
                    "Describe key behaviors or methods"
                ]
            }
        }

    except Exception as e:
        logger.error(f"Error getting diagram capabilities: {e}")
        return {
            "error": f"Failed to retrieve capabilities: {str(e)}",
            "basic_types": ["sequence", "flowchart", "class", "architecture"]
        }

@mcp.tool()
def convert_diagram_format(
    diagram_code: str,
    from_format: str,
    to_format: str,
    diagram_type: str
) -> Dict[str, Any]:
    """
    Convert a diagram from one format to another.

    Args:
        diagram_code: Existing diagram code to convert
        from_format: Source format (e.g., "mermaid", "plantuml")
        to_format: Target format (e.g., "mermaid", "plantuml", "python_diagrams")
        diagram_type: Type of diagram ("sequence", "flowchart", "class")

    Returns:
        Dictionary with converted diagram code
    """
    try:
        # This is a simplified conversion - in practice, you'd need format parsers
        # For now, we'll indicate this feature needs development

        if from_format == to_format:
            return {
                "success": True,
                "converted_code": diagram_code,
                "message": "No conversion needed - formats are the same"
            }

        return {
            "success": False,
            "error": "Format conversion not yet implemented",
            "suggestion": f"Please regenerate the {diagram_type} diagram directly in {to_format} format",
            "available_alternative": f"Use generate_{diagram_type}_diagram() with output_format='{to_format}'"
        }

    except Exception as e:
        logger.error(f"Error converting diagram format: {e}")
        return {
            "success": False,
            "error": f"Failed to convert diagram format: {str(e)}"
        }

def _get_usage_instructions(output_format: str) -> str:
    """Get format-specific usage instructions"""
    instructions = {
        "mermaid": """
To render this Mermaid diagram:
1. Copy the code to mermaid.live for online preview
2. Use in GitHub/GitLab markdown (supports mermaid code blocks)
3. Integrate with documentation tools that support Mermaid
4. Use Mermaid CLI for generating images: `mmdc -i diagram.mmd -o diagram.png`
        """.strip(),

        "plantuml": """
To render this PlantUML diagram:
1. Copy the code to plantuml.com/plantuml for online preview
2. Use PlantUML plugin in IDEs like VS Code, IntelliJ
3. Generate images with PlantUML jar: `java -jar plantuml.jar diagram.puml`
4. Integrate with documentation systems that support PlantUML
        """.strip(),

        "python_diagrams": """
To render this Python diagrams code:
1. Install the diagrams library: `pip install diagrams`
2. Install Graphviz: `brew install graphviz` (macOS) or appropriate package manager
3. Run the Python code: `python diagram.py`
4. The diagram will be generated as a PNG file
        """.strip()
    }

    return instructions.get(output_format, "Copy and use the generated code with appropriate tools for this format.")

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
