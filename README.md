# Diagrams MCP Server

An MCP (Model Context Protocol) server that integrates with the [Diagrams](https://diagrams.mingrammer.com/) project, allowing users to easily search for cloud services and generate infrastructure diagrams using natural language descriptions.

## Features

### 🔍 Service Search
- Search across all cloud providers (AWS, Azure, GCP, IBM, Alibaba Cloud)
- Filter by provider and category
- Find exact service matches with import paths and icon information
- Extract service classes from Diagrams package files

### 🎨 Diagram Code Generation
- Generate Python diagram code from natural language descriptions
- Automatic component detection and mapping to cloud services
- Relationship extraction between components
- Support for multiple diagram types and styles

### 🖼️ Image Generation
- Execute generated code to create actual diagram images
- Support for multiple output formats (PNG, SVG, PDF, JPG)
- Automatic environment validation
- Error handling and debugging support

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd diagram-mcp

# Install dependencies
uv install

# Install required system dependencies
pip install diagrams graphviz
```

## Usage

### As an MCP Server
```bash
uv run ./src/diagrams_mcp/server.py
```

### Direct Usage

#### Search for Services
```python
from diagrams_mcp.server import search_services

# Search for EC2 services in AWS
result = search_services("ec2", provider="aws")
print(result)
```

#### Generate Diagram Code
```python
from diagrams_mcp.code_generator import CodeGenerator

generator = CodeGenerator()
code = generator.generate_from_description(
    "Load balancer connects to EC2 instances and RDS database",
    provider_preference="aws"
)
print(code)
```

#### Generate Diagram Images
```python
generator = CodeGenerator()
result = generator.generate_diagram_image(
    "API Gateway forwards requests to Lambda functions which store data in DynamoDB",
    provider_preference="aws",
    output_path="my_architecture"
)

if result["success"]:
    print(f"Diagram saved to: {result['generated_files']}")
else:
    print(f"Error: {result['error']}")
```

## MCP Tools

### `search_services`
Search for cloud services across providers.

**Parameters:**
- `query` (str): Search term (e.g., "kubernetes", "database", "storage")
- `provider` (Optional[str]): Provider filter ("aws", "azure", "gcp", "ibm", "alibabacloud")

**Returns:**
- Dictionary with matching services, their import paths, icons, and metadata

### `generate_diagram_code`
Generate Python diagrams code from natural language description.

**Parameters:**
- `description` (str): Natural language description of the architecture
- `provider_preference` (Optional[str]): Preferred cloud provider
- `diagram_type` (str): Type of diagram to generate (default: "basic")

**Returns:**
- Dictionary with generated code, required imports, and execution notes

## Examples

### Simple Web Application
```python
description = "Users access a web application through a load balancer that distributes traffic to multiple EC2 instances. The instances connect to an RDS database for data storage."

code = generator.generate_from_description(description, provider_preference="aws")
```

### Microservices Architecture
```python
description = "API Gateway receives requests and forwards them to Lambda functions. The functions store data in DynamoDB and publish events to SQS queues."

result = generator.generate_diagram_image(description, provider_preference="aws")
```

## Requirements

- Python 3.8+
- [Diagrams](https://diagrams.mingrammer.com/) package
- [Graphviz](https://graphviz.org/) (for image generation)
- MCP compatible client

## Project Structure

```
src/diagrams_mcp/
├── server.py           # Main MCP server
├── service_finder.py   # Service search functionality
├── code_generator.py   # Diagram code generation
└── __init__.py
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Acknowledgments

- [Diagrams](https://diagrams.mingrammer.com/) - The awesome diagrams-as-code library
- [Model Context Protocol](https://modelcontextprotocol.io/) - For the MCP specification
