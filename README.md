# Diagrams MCP Server

An MCP (Model Context Protocol) server that integrates with the [Diagrams](https://diagrams.mingrammer.com/) project for intelligent cloud service discovery and infrastructure diagram generation.

## Features

### 🔍 Intelligent Service Discovery
- Search across all cloud providers (AWS, Azure, GCP, IBM, Alibaba Cloud)
- Fuzzy search with typo tolerance and partial matching
- Semantic search by purpose ("container orchestration" → EKS, AKS, GKE)
- Category filtering (compute, database, network, security, storage)
- Alias support for common service names

### 🎨 Advanced Code Generation
- Generate Python diagram code from natural language descriptions
- Architecture pattern recognition and templates
- Multi-cloud and hybrid architecture support
- Best practices integration with security recommendations
- Automatic component relationship mapping

### 🖼️ Enhanced Image Generation
- Create actual diagram images from generated code
- Support for PNG, SVG, PDF, JPG formats
- Advanced clustering and nested diagram support
- Interactive diagram builder with step-by-step guidance
- Custom styling and layout options

### 📊 Multi-Type Diagram Support
- **Infrastructure Diagrams**: Traditional cloud architecture diagrams
- **Sequence Diagrams**: API interactions, service communication flows
- **Flowcharts**: Business processes, decision trees, workflows
- **Class Diagrams**: System design, data models, component relationships
- **Network Diagrams**: Connectivity, traffic flow, security boundaries
- **Data Flow Diagrams**: Information processing, ETL pipelines

### 🔄 Cross-Provider Intelligence
- Find equivalent services across cloud providers
- Migration assistance with cost implications
- Feature comparison between equivalent services
- Automated architecture migration between providers

### 💰 Cost Analysis & Optimization
- Real-time cost estimation for architectures
- Monthly cost breakdowns by service
- Cost optimization recommendations
- Budget constraint analysis
- Track architecture costs over time

### 🛡️ Security & Compliance
- Architecture security analysis
- Compliance checking (SOC2, PCI-DSS, HIPAA, GDPR)
- Security vulnerability identification
- Best practice recommendations
- Organizational policy enforcement

### 🤖 AI-Powered Features
- Intelligent architecture recommendations
- Auto-generated technical documentation
- Performance optimization suggestions
- Failure scenario simulation
- Service trend analysis and insights

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

### Core Tools

#### `search_services`
Search for cloud services with intelligent matching.
- `query` (string): Search term (e.g., "database", "kubernetes")
- `provider` (optional): Filter by provider ("aws", "azure", "gcp", "ibm", "alibabacloud")

#### `generate_diagram_code`
Generate Python diagrams code from natural language.
- `description` (string): Architecture description
- `provider_preference` (optional): Preferred cloud provider
- `diagram_type` (optional): Diagram type ("infrastructure", "sequence", "flowchart", "class", "network", "dataflow")

#### `generate_sequence_diagram`
Generate sequence diagrams for API interactions and service flows.
- `description` (string): Description of the interaction flow
- `participants` (optional): List of system participants/actors
- `format` (optional): Output format (default: "mermaid")

#### `generate_flowchart`
Generate flowcharts for business processes and decision flows.
- `description` (string): Process or workflow description
- `process_type` (optional): Type of process ("business", "technical", "decision")
- `format` (optional): Output format ("mermaid", "drawio", "plantuml")

#### `generate_class_diagram`
Generate class diagrams for system design and data models.
- `description` (string): System or data model description
- `entities` (optional): List of main entities/classes
- `relationships` (optional): Specify relationship types

#### `find_architecture_patterns`
Find suitable architecture patterns based on requirements.
- `requirements` (string): System requirements and constraints
- `constraints` (optional): Additional constraints

### Advanced Tools

#### `analyze_architecture`
Analyze existing diagram code for optimization opportunities.
- `diagram_code` (string): Python diagrams code to analyze
- Returns security issues, cost optimizations, performance suggestions

#### `estimate_architecture_cost`
Estimate monthly costs for architecture with detailed breakdown.
- `diagram_code` (string): Python diagrams code
- `region` (string): Cloud region for pricing (default: "us-east-1")
- `usage_pattern` (string): Usage pattern ("low", "medium", "high")

#### `check_compliance`
Check architecture against compliance frameworks.
- `diagram_code` (string): Python diagrams code
- `framework` (string): Compliance framework (SOC2, PCI-DSS, HIPAA, GDPR)

#### `get_architecture_recommendations`
Get AI-powered architecture recommendations.
- `requirements` (string): Architecture requirements
- `constraints` (optional): Budget and technical constraints

#### `validate_architecture`
Validate architecture for common issues and best practices.
- `diagram_code` (string): Python diagrams code
- `validation_type` (string): Validation scope (default: "comprehensive")

#### `generate_architecture_documentation`
Generate comprehensive documentation from diagrams.
- `diagram_code` (string): Python diagrams code
- `doc_type` (string): Documentation type ("technical", "executive", "deployment")

## Examples

### Basic Usage
```python
# Search for services
search_services("container orchestration")

# Generate infrastructure diagram
generate_diagram_code(
    "Web application with load balancer, auto-scaling servers, and database",
    provider_preference="aws",
    diagram_type="infrastructure"
)

# Generate sequence diagram
generate_sequence_diagram(
    "User logs in, system validates credentials, returns JWT token, user accesses protected resource"
)

# Generate flowchart
generate_flowchart(
    "Order processing: receive order, validate payment, check inventory, fulfill order, send confirmation"
)

# Generate class diagram
generate_class_diagram(
    "E-commerce system with User, Product, Order, and Payment entities"
)

# Find architecture patterns
find_architecture_patterns("E-commerce platform with high availability")
```

### Common Patterns

**Infrastructure Diagrams:**
```
"Users access web application through load balancer that distributes traffic to multiple servers connected to a database"
```

**Sequence Diagrams:**
```
"API Gateway receives request, authenticates user via Auth service, forwards to Business Logic service, queries Database, returns response"
```

**Flowcharts:**
```
"User registration process: collect user data, validate email, check if user exists, create account, send welcome email"
```

**Class Diagrams:**
```
"Social media platform with User, Post, Comment, Like entities and their relationships"
```

## Project Structure

```
src/diagrams_mcp/
├── server.py              # Main MCP server with all tools
├── service_finder.py      # Intelligent service discovery
├── code_generator.py      # Advanced diagram generation
├── sequence_generator.py  # Sequence diagram generation
├── flowchart_generator.py # Flowchart and process diagrams
├── class_generator.py     # Class and entity diagrams
├── pattern_analyze.py     # Requirements analysis
├── pattern_engine.py      # Pattern matching
├── cost_estimator.py      # Cost analysis and optimization
├── compliance_checker.py  # Security and compliance
├── ai_recommendations.py  # AI-powered suggestions
└── __init__.py
```

## Requirements

- Python 3.9+
- [Diagrams](https://diagrams.mingrammer.com/) package
- [Graphviz](https://graphviz.org/) (for infrastructure diagrams)
- [Mermaid CLI](https://mermaid.js.org/) (for sequence/flowcharts - optional)
- [PlantUML](https://plantuml.com/) (for UML diagrams - optional)
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
