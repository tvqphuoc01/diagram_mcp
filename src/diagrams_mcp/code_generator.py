# src/diagrams_mcp/code_generator.py
import re
import os
import sys
import tempfile
import subprocess
from typing import Dict, List, Any, Optional
from pathlib import Path

# Add current directory to Python path for imports
sys.path.insert(0, os.path.dirname(__file__))

try:
    from .service_finder import find_services
except ImportError:
    from service_finder import find_services

class CodeGenerator:
    def __init__(self, package_path: Optional[str] = None):
        if package_path is None:
            import diagrams
            package_path = os.path.dirname(diagrams.__file__)
        self.package_path = package_path

    def generate_from_description(
        self, description: str,
        provider_preference: Optional[str] = None,
        diagram_type: str = "basic"
    ) -> str:
        """Generate diagram code from natural language description"""
        components = self._extract_components(description)
        relationships = self._extract_relationships(description)

        # Map components to actual diagram services
        services = self._map_to_services(components, provider_preference)

        # Generate code
        code = self._build_diagram_code(services, relationships, diagram_type)

        return code

    def generate_diagram_image(
        self, description: str,
        provider_preference: Optional[str] = None,
        diagram_type: str = "basic",
        output_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate both code and execute it to create diagram image"""
        # Generate the code
        code = self.generate_from_description(description, provider_preference, diagram_type)

        if code.startswith("# No services found"):
            return {
                "success": False,
                "error": "No services found to generate diagram",
                "code": code
            }

        # Create temporary file to execute the code
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_file:
            # Modify code to save to specific location
            if output_path:
                modified_code = code.replace(
                    'with Diagram("Generated Architecture", show=False):',
                    f'with Diagram("Generated Architecture", filename="{output_path}", show=False):'
                )
            else:
                output_path = "generated_architecture"
                modified_code = code.replace(
                    'with Diagram("Generated Architecture", show=False):',
                    f'with Diagram("Generated Architecture", filename="{output_path}", show=False):'
                )

            temp_file.write(modified_code)
            temp_file_path = temp_file.name

        try:
            # Execute the generated code
            result = subprocess.run(
                [sys.executable, temp_file_path],
                capture_output=True,
                text=True,
                timeout=30
            )

            # Clean up temp file
            os.unlink(temp_file_path)

            if result.returncode == 0:
                # Look for generated image files
                image_extensions = ['.png', '.svg', '.pdf', '.jpg']
                generated_files = []

                for ext in image_extensions:
                    potential_file = f"{output_path}{ext}"
                    if os.path.exists(potential_file):
                        generated_files.append(potential_file)

                return {
                    "success": True,
                    "code": code,
                    "generated_files": generated_files,
                    "output_path": output_path,
                    "stdout": result.stdout,
                    "stderr": result.stderr
                }
            else:
                return {
                    "success": False,
                    "error": f"Execution failed with return code {result.returncode}",
                    "code": code,
                    "stdout": result.stdout,
                    "stderr": result.stderr
                }

        except subprocess.TimeoutExpired:
            os.unlink(temp_file_path)
            return {
                "success": False,
                "error": "Code execution timed out",
                "code": code
            }
        except Exception as e:
            os.unlink(temp_file_path)
            return {
                "success": False,
                "error": f"Execution error: {str(e)}",
                "code": code
            }

    def _extract_components(self, description: str) -> List[str]:
        """Extract architecture components from description"""
        # Use NLP or regex to identify common cloud services
        common_services = [
            "load balancer", "database", "api gateway", "lambda", "function",
            "storage", "cache", "queue", "kubernetes", "container",
            "vpc", "subnet", "firewall", "cdn", "monitoring", "ec2", "s3",
            "rds", "elb", "alb", "nlb", "cloudfront", "route53", "iam",
            "vpc", "subnet", "internet gateway", "nat gateway"
        ]

        found_components = []
        for service in common_services:
            if service.lower() in description.lower():
                found_components.append(service)

        return found_components

    def _extract_relationships(self, description: str) -> List[Dict]:
        """Extract relationships between components from description"""
        # Simple relationship extraction based on common patterns
        relationships = []

        # Look for connection words
        connection_patterns = [
            r"(\w+)\s+connects?\s+to\s+(\w+)",
            r"(\w+)\s+sends?\s+to\s+(\w+)",
            r"(\w+)\s+forwards?\s+to\s+(\w+)",
            r"(\w+)\s+->+\s+(\w+)",
        ]

        for pattern in connection_patterns:
            matches = re.findall(pattern, description, re.IGNORECASE)
            for match in matches:
                relationships.append({
                    "from": match[0],
                    "to": match[1]
                })

        return relationships

    def _map_to_services(
        self, components: List[str],
        provider: Optional[str] = None
    ) -> List[Dict]:
        """Map identified components to actual diagram services"""
        mapped_services = []

        for component in components:
            # Use the find_services function to search for matching services
            search_results = find_services(component, provider, self.package_path)
            if search_results:
                # Pick the most relevant service (first match)
                best_match = search_results[0]
                mapped_services.append(best_match)

        return mapped_services

    def _build_diagram_code(
        self, services: List[Dict],
        relationships: List[Dict],
        diagram_type: str
    ) -> str:
        """Build the actual Python code for the diagram"""
        if not services:
            return "# No services found to generate diagram"

        imports = set()
        service_instances = []
        connections = []

        # Generate imports
        imports.add("from diagrams import Diagram, Cluster")
        for service in services:
            imports.add(f"from {service['import_path']} import {service['name']}")

        # Generate service instances with unique variable names
        service_vars = {}
        for i, service in enumerate(services):
            var_name = f"{service['name'].lower().replace('-', '_')}"
            if var_name in service_vars:
                var_name = f"{var_name}_{i}"
            service_vars[service['name']] = var_name
            service_instances.append(f"    {var_name} = {service['name']}(\"{service['name']}\")")

        # Generate connections based on relationships
        for rel in relationships:
            from_var = service_vars.get(rel['from'])
            to_var = service_vars.get(rel['to'])
            if from_var and to_var:
                connections.append(f"    {from_var} >> {to_var}")

        # Build the complete code
        code_parts = [
            *sorted(imports),
            "",
            "with Diagram(\"Generated Architecture\", show=False):",
            *service_instances
        ]

        if connections:
            code_parts.extend(["", "    # Connections"] + connections)

        return "\n".join(code_parts)

    def get_required_imports(self, code: str) -> List[str]:
        """Extract required imports from generated code"""
        import_lines = []
        for line in code.split('\n'):
            if line.strip().startswith('from ') or line.strip().startswith('import '):
                import_lines.append(line.strip())
        return import_lines

    def get_execution_notes(self) -> str:
        """Return notes about executing the generated code"""
        return """
            To execute this diagram:
            1. Save the code to a .py file
            2. Run: python your_diagram.py
            3. The diagram will be saved as a PNG file in the current directory
            4. Make sure you have graphviz installed: pip install graphviz
        """

    def validate_environment(self) -> Dict[str, Any]:
        """Check if the environment is ready for diagram generation"""
        issues = []

        # Check if graphviz is available
        try:
            subprocess.run(['dot', '-V'], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            issues.append("Graphviz not installed or not in PATH. Install with: pip install graphviz")

        # Check if diagrams package is available
        try:
            import diagrams
        except ImportError:
            issues.append("Diagrams package not installed. Install with: pip install diagrams")

        return {
            "ready": len(issues) == 0,
            "issues": issues
        }
