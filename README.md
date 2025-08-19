# Diagrams MCP Server

An MCP (Model Context Protocol) server that integrates with the [Diagrams](https://diagrams.mingrammer.com/) project for intelligent cloud service discovery and infrastructure diagram generation.

## Features

### 🔍 Service Discovery
- Search across all cloud providers (AWS, Azure, GCP, IBM, Alibaba Cloud)
- Filter by provider and category
- Find services with fuzzy matching and aliases
- Get import paths and service information

### 🎨 Code Generation
- Generate Python diagram code from natural language descriptions
- Automatic component detection and mapping
- Support for multiple providers and diagram types
- Best practices integration

### 🖼️ Image Generation
- Create actual diagram images from generated code
- Support for PNG, SVG, PDF, JPG formats
- Cluster and nested diagram support
- Error handling and validation

### 🔄 Cross-Provider Mapping
- Find equivalent services across cloud providers
- Migration assistance between providers
- Feature and cost comparisons

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd diagrams-mcp

# Install dependencies
uv install

# Install system requirements
pip install diagrams graphviz
```

### System Dependencies
- **macOS**: `brew install graphviz`
- **Ubuntu/Debian**: `sudo apt-get install graphviz`
- **Windows**: Download from [graphviz.org](https://graphviz.org/download/)

## Usage

### Starting the MCP Server
```bash
uv run ./src/diagrams_mcp/server.py
```

### MCP Configuration
Add to your MCP client configuration:
```json
{
  "mcpServers": {
    "diagrams": {
      "command": "uv",
      "args": ["run", "./src/diagrams_mcp/server.py"]
    }
  }
}
```

## Available Tools

### `search_services`
Search for cloud services across providers.

**Parameters:**
- `query` (string): Search term (e.g., "database", "kubernetes")
- `provider` (optional): Filter by provider ("aws", "azure", "gcp", "ibm", "alibabacloud")

### `generate_diagram_code`
Generate Python diagrams code from natural language.

**Parameters:**
- `description` (string): Architecture description
- `provider_preference` (optional): Preferred cloud provider
- `diagram_type` (optional): Type of diagram (default: "basic")

### `find_architecture_patterns`
Find suitable architecture patterns based on requirements.

**Parameters:**
- `requirements` (string): System requirements and constraints
- `constraints` (optional): Additional constraints

## Examples

### Basic Usage
```python
# Search for services
search_services("container orchestration")

# Generate diagram code
generate_diagram_code(
    "Web application with load balancer, auto-scaling servers, and database",
    provider_preference="aws"
)

# Find architecture patterns
find_architecture_patterns("E-commerce platform with high availability")
```

### Common Patterns

**Three-tier Web Application:**
```
"Users access web application through load balancer that distributes traffic to multiple servers connected to a database"
```

**Microservices Architecture:**
```
"API Gateway routes requests to Lambda functions that store data in DynamoDB and publish to SQS queues"
```

**Data Pipeline:**
```
"Data flows from S3 bucket through Lambda processing to RDS database with CloudWatch monitoring"
```

## Project Structure

```
src/diagrams_mcp/
├── server.py           # Main MCP server
├── service_finder.py   # Service search functionality
├── code_generator.py   # Diagram code generation
├── pattern_analyze.py  # Requirements analysis
└── pattern_engine.py   # Pattern matching
```

## Requirements

- Python 3.9+
- [Diagrams](https://diagrams.mingrammer.com/) package
- [Graphviz](https://graphviz.org/) (for image generation)
- MCP compatible client

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

MIT License

## Acknowledgments

- [Diagrams](https://diagrams.mingrammer.com/) - The awesome diagrams-as-code library
- [Model Context Protocol](https://modelcontextprotocol.io/) - For the MCP specification
