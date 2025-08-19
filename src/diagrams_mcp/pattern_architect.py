# src/diagrams_mcp/models/pattern.py
from dataclasses import dataclass, field
import os
import sys
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import json
import uuid

# Add current directory to Python path for imports
sys.path.insert(0, os.path.dirname(__file__))

# Import the enums from the previous file
from pattern_cate import PatternCategory, PatternComplexity, PatternMaturity

@dataclass
class ComponentMapping:
    """Mapping of logical components to cloud-specific services"""
    logical_name: str  # e.g., "load_balancer"
    aws_service: Optional[str] = None
    azure_service: Optional[str] = None
    gcp_service: Optional[str] = None
    generic_service: Optional[str] = None
    description: str = ""
    is_required: bool = True
    alternatives: List[str] = field(default_factory=list)

@dataclass
class PatternVariant:
    """Different variants of the same pattern (e.g., basic, standard, enterprise)"""
    name: str
    description: str
    additional_components: List[str] = field(default_factory=list)
    complexity_modifier: float = 1.0  # Multiplier for base complexity
    cost_modifier: float = 1.0  # Multiplier for base cost
    use_cases: List[str] = field(default_factory=list)

@dataclass
class SecurityRequirement:
    """Security requirements and recommendations for the pattern"""
    requirement_type: str  # "mandatory", "recommended", "optional"
    description: str
    implementation_notes: str = ""
    compliance_frameworks: List[str] = field(default_factory=list)
    risk_level: str = "medium"  # "low", "medium", "high", "critical"

@dataclass
class PerformanceCharacteristic:
    """Performance characteristics and benchmarks"""
    metric_name: str  # e.g., "response_time", "throughput", "availability"
    typical_value: str  # e.g., "< 200ms", "1000 RPS", "99.9%"
    peak_value: Optional[str] = None
    measurement_conditions: str = ""
    bottlenecks: List[str] = field(default_factory=list)
    optimization_tips: List[str] = field(default_factory=list)

@dataclass
class CostEstimate:
    """Cost estimation for different scales"""
    scale_level: str  # "small", "medium", "large", "enterprise"
    monthly_range_min: float
    monthly_range_max: float
    currency: str = "USD"
    assumptions: List[str] = field(default_factory=list)
    cost_breakdown: Dict[str, float] = field(default_factory=dict)
    optimization_potential: str = ""

@dataclass
class ImplementationGuide:
    """Step-by-step implementation guidance"""
    phase_name: str
    description: str
    estimated_hours: int
    prerequisites: List[str] = field(default_factory=list)
    deliverables: List[str] = field(default_factory=list)
    risks: List[str] = field(default_factory=list)
    validation_criteria: List[str] = field(default_factory=list)

@dataclass
class PatternRelationship:
    """Relationships between patterns"""
    related_pattern: str  # Pattern name
    relationship_type: str  # "alternative", "evolution", "prerequisite", "complement"
    description: str
    migration_effort: str = "unknown"  # "low", "medium", "high"
    migration_strategy: str = ""

@dataclass
class ArchitecturePattern:
    """
    Complete architecture pattern definition with all metadata,
    characteristics, and implementation guidance.
    """

    # ===== BASIC INFORMATION =====
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    category: PatternCategory = PatternCategory.WEB_APPLICATION
    complexity: PatternComplexity = PatternComplexity.MODERATE
    maturity: PatternMaturity = PatternMaturity.MATURE

    # ===== DESCRIPTION & METADATA =====
    short_description: str = ""
    detailed_description: str = ""
    version: str = "1.0.0"
    created_date: str = field(default_factory=lambda: datetime.now().isoformat())
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())
    author: str = ""
    organization: str = ""

    # ===== APPLICABILITY =====
    suitable_for: List[str] = field(default_factory=list)  # Application types
    not_suitable_for: List[str] = field(default_factory=list)
    industry_focus: List[str] = field(default_factory=list)  # fintech, healthcare, etc.
    business_drivers: List[str] = field(default_factory=list)  # cost, scale, speed, etc.

    # ===== TECHNICAL CAPABILITIES =====
    capabilities: Dict[str, float] = field(default_factory=dict)  # capability -> score (0-1)
    supported_providers: List[str] = field(default_factory=list)  # aws, azure, gcp, etc.
    compatible_technologies: List[str] = field(default_factory=list)
    programming_languages: List[str] = field(default_factory=list)
    frameworks: List[str] = field(default_factory=list)

    # ===== ARCHITECTURE COMPONENTS =====
    required_components: List[ComponentMapping] = field(default_factory=list)
    optional_components: List[ComponentMapping] = field(default_factory=list)
    component_relationships: List[Dict[str, str]] = field(default_factory=list)

    # ===== PATTERN VARIANTS =====
    variants: List[PatternVariant] = field(default_factory=list)
    default_variant: str = "standard"

    # ===== CHARACTERISTICS =====
    # Scale Characteristics
    min_scale: str = "small"  # small, medium, large, enterprise
    max_scale: str = "large"
    supports_auto_scaling: bool = False
    horizontal_scaling: bool = True
    vertical_scaling: bool = True

    # Security Characteristics
    security_level: int = 2  # 1-4 (basic to critical)
    security_requirements: List[SecurityRequirement] = field(default_factory=list)
    compliance_frameworks: List[str] = field(default_factory=list)
    data_protection_level: str = "standard"

    # Performance Characteristics
    performance_metrics: List[PerformanceCharacteristic] = field(default_factory=list)
    typical_response_time_ms: Optional[int] = None
    max_throughput_rps: Optional[int] = None
    availability_target: float = 0.999  # 99.9%

    # Cost Characteristics
    cost_estimates: List[CostEstimate] = field(default_factory=list)
    cost_model: str = "fixed"  # fixed, variable, hybrid
    cost_optimization_potential: str = "medium"

    # ===== IMPLEMENTATION =====
    implementation_phases: List[ImplementationGuide] = field(default_factory=list)
    estimated_implementation_weeks: int = 4
    team_size_recommendation: str = "2-4 people"
    required_skills: List[str] = field(default_factory=list)

    # ===== OPERATION & MAINTENANCE =====
    maintenance_complexity: str = "medium"  # low, medium, high
    monitoring_requirements: List[str] = field(default_factory=list)
    backup_strategy: str = ""
    disaster_recovery_rto: Optional[str] = None  # Recovery Time Objective
    disaster_recovery_rpo: Optional[str] = None  # Recovery Point Objective

    # ===== DOCUMENTATION =====
    documentation_url: str = ""
    tutorial_url: str = ""
    best_practices_url: str = ""
    troubleshooting_guide: str = ""

    # ===== CODE GENERATION =====
    diagram_template: str = ""  # Python diagrams code template
    terraform_template: str = ""  # Terraform template
    cloudformation_template: str = ""  # CloudFormation template
    kubernetes_manifests: str = ""  # K8s manifests

    # ===== PATTERN RELATIONSHIPS =====
    relationships: List[PatternRelationship] = field(default_factory=list)
    prerequisites: List[str] = field(default_factory=list)
    evolution_paths: List[str] = field(default_factory=list)

    # ===== VALIDATION & TESTING =====
    validation_checklist: List[str] = field(default_factory=list)
    testing_strategy: str = ""
    performance_benchmarks: Dict[str, str] = field(default_factory=dict)

    # ===== TAGS & SEARCH =====
    tags: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)
    search_terms: List[str] = field(default_factory=list)

    def __post_init__(self):
        """Initialize computed fields and defaults"""
        if not self.tags:
            self.tags = [self.category.value, self.complexity.value, self.maturity.value]

        if not self.keywords:
            self.keywords = self._generate_keywords()

        if not self.suitable_for:
            self.suitable_for = self.category.get_typical_use_cases()

    def _generate_keywords(self) -> List[str]:
        """Generate search keywords from pattern characteristics"""
        keywords = [
            self.name.lower(),
            self.category.value,
            self.complexity.value,
            self.maturity.value
        ]

        # Add provider keywords
        keywords.extend(self.supported_providers)

        # Add capability keywords
        keywords.extend(self.capabilities.keys())

        # Add component keywords
        for component in self.required_components + self.optional_components:
            keywords.append(component.logical_name)

        return list(set(keywords))  # Remove duplicates

    # ===== FACTORY METHODS =====

    @classmethod
    def create_three_tier_web_app(cls) -> 'ArchitecturePattern':
        """Factory method for 3-tier web application pattern"""
        return cls(
            name="3-Tier Web Application",
            category=PatternCategory.THREE_TIER,
            complexity=PatternComplexity.MODERATE,
            maturity=PatternMaturity.INDUSTRY_STANDARD,
            short_description="Traditional web application with presentation, business logic, and data layers",
            detailed_description="""
            The 3-tier architecture pattern separates an application into three logical layers:

            1. **Presentation Layer**: User interface and user experience components
            2. **Business Logic Layer**: Application logic, business rules, and processing
            3. **Data Layer**: Data storage, retrieval, and management

            This pattern provides clear separation of concerns, making the application easier
            to develop, maintain, and scale. Each layer can be developed and deployed independently,
            allowing for better team organization and technology choices.
            """,
            suitable_for=[
                "Traditional web applications",
                "Enterprise applications",
                "E-commerce platforms",
                "Content management systems"
            ],
            not_suitable_for=[
                "Real-time applications",
                "Microservices architectures",
                "Event-driven systems"
            ],
            capabilities={
                "user_authentication": 0.9,
                "database_integration": 1.0,
                "session_management": 0.8,
                "caching": 0.7,
                "load_balancing": 0.8,
                "monitoring": 0.6,
                "backup": 0.7
            },
            supported_providers=["aws", "azure", "gcp", "on_premises"],
            required_components=[
                ComponentMapping(
                    logical_name="load_balancer",
                    aws_service="Application Load Balancer",
                    azure_service="Application Gateway",
                    gcp_service="HTTP(S) Load Balancer",
                    description="Distributes incoming requests across multiple instances"
                ),
                ComponentMapping(
                    logical_name="web_server",
                    aws_service="EC2",
                    azure_service="Virtual Machines",
                    gcp_service="Compute Engine",
                    description="Hosts the web application and business logic"
                ),
                ComponentMapping(
                    logical_name="database",
                    aws_service="RDS",
                    azure_service="SQL Database",
                    gcp_service="Cloud SQL",
                    description="Stores application data"
                )
            ],
            optional_components=[
                ComponentMapping(
                    logical_name="cdn",
                    aws_service="CloudFront",
                    azure_service="Azure CDN",
                    gcp_service="Cloud CDN",
                    description="Content delivery network for static assets",
                    is_required=False
                ),
                ComponentMapping(
                    logical_name="cache",
                    aws_service="ElastiCache",
                    azure_service="Azure Cache for Redis",
                    gcp_service="Memorystore",
                    description="In-memory caching for improved performance",
                    is_required=False
                )
            ],
            variants=[
                PatternVariant(
                    name="basic",
                    description="Minimal setup with single instance and basic database",
                    complexity_modifier=0.7,
                    cost_modifier=0.5,
                    use_cases=["Small applications", "Prototypes", "Development environments"]
                ),
                PatternVariant(
                    name="standard",
                    description="Production-ready with load balancing and managed database",
                    complexity_modifier=1.0,
                    cost_modifier=1.0,
                    use_cases=["Production applications", "Business systems"]
                ),
                PatternVariant(
                    name="enterprise",
                    description="High availability with multiple AZs, CDN, and advanced monitoring",
                    additional_components=["cdn", "cache", "monitoring", "backup"],
                    complexity_modifier=1.5,
                    cost_modifier=2.0,
                    use_cases=["Mission-critical applications", "High-traffic websites"]
                )
            ],
            performance_metrics=[
                PerformanceCharacteristic(
                    metric_name="response_time",
                    typical_value="< 500ms",
                    peak_value="< 1s",
                    measurement_conditions="Average load, cached responses",
                    bottlenecks=["Database queries", "Network latency"],
                    optimization_tips=["Implement caching", "Optimize database queries", "Use CDN"]
                ),
                PerformanceCharacteristic(
                    metric_name="throughput",
                    typical_value="1000 requests/second",
                    peak_value="5000 requests/second",
                    measurement_conditions="With auto-scaling enabled",
                    bottlenecks=["Database connections", "Server capacity"]
                )
            ],
            security_requirements=[
                SecurityRequirement(
                    requirement_type="mandatory",
                    description="HTTPS encryption for all client communication",
                    implementation_notes="Use TLS 1.2 or higher",
                    risk_level="high"
                ),
                SecurityRequirement(
                    requirement_type="recommended",
                    description="Web Application Firewall (WAF)",
                    implementation_notes="Protect against OWASP Top 10 vulnerabilities",
                    risk_level="medium"
                )
            ],
            cost_estimates=[
                CostEstimate(
                    scale_level="small",
                    monthly_range_min=100,
                    monthly_range_max=300,
                    assumptions=["Single AZ", "Basic monitoring", "Standard support"],
                    cost_breakdown={
                        "compute": 60,
                        "database": 80,
                        "load_balancer": 25,
                        "data_transfer": 35
                    }
                ),
                CostEstimate(
                    scale_level="medium",
                    monthly_range_min=500,
                    monthly_range_max=1200,
                    assumptions=["Multi-AZ", "Auto-scaling", "Enhanced monitoring"],
                    cost_breakdown={
                        "compute": 400,
                        "database": 300,
                        "load_balancer": 50,
                        "cdn": 100,
                        "monitoring": 100,
                        "data_transfer": 250
                    }
                )
            ],
            implementation_phases=[
                ImplementationGuide(
                    phase_name="Infrastructure Setup",
                    description="Set up basic cloud infrastructure and networking",
                    estimated_hours=16,
                    prerequisites=["Cloud provider account", "Basic networking knowledge"],
                    deliverables=["VPC configuration", "Security groups", "Load balancer"],
                    validation_criteria=["Network connectivity test", "Security scan"]
                ),
                ImplementationGuide(
                    phase_name="Database Configuration",
                    description="Set up and configure the database layer",
                    estimated_hours=12,
                    prerequisites=["Database design", "Schema definition"],
                    deliverables=["Database instance", "Initial schema", "Backup configuration"],
                    validation_criteria=["Connection test", "Performance baseline"]
                ),
                ImplementationGuide(
                    phase_name="Application Deployment",
                    description="Deploy and configure the web application",
                    estimated_hours=20,
                    prerequisites=["Application code", "Deployment scripts"],
                    deliverables=["Running application", "Health checks", "Monitoring"],
                    validation_criteria=["Functional tests", "Performance tests", "Security scan"]
                )
            ],
            relationships=[
                PatternRelationship(
                    related_pattern="Microservices Architecture",
                    relationship_type="evolution",
                    description="Can evolve to microservices as application grows",
                    migration_effort="high",
                    migration_strategy="Decompose business layer into independent services"
                ),
                PatternRelationship(
                    related_pattern="Serverless Web Application",
                    relationship_type="alternative",
                    description="Serverless alternative with similar functionality",
                    migration_effort="medium",
                    migration_strategy="Replace compute layer with functions"
                )
            ],
            diagram_template='''
from diagrams import Diagram, Cluster
from diagrams.{provider}.network import {load_balancer}
from diagrams.{provider}.compute import {compute}
from diagrams.{provider}.database import {database}

with Diagram("{app_name}", show=False, direction="TB"):
    lb = {load_balancer}("Load Balancer")

    with Cluster("Web Tier"):
        web_servers = [{compute}("Web-1"), {compute}("Web-2")]

    with Cluster("Database Tier"):
        db = {database}("Database")

    lb >> web_servers >> db
            ''',
            validation_checklist=[
                "Load balancer health checks configured",
                "Database backup strategy implemented",
                "SSL/TLS certificates configured",
                "Monitoring and alerting set up",
                "Security groups properly configured",
                "Auto-scaling policies defined"
            ],
            required_skills=[
                "Cloud platform knowledge (AWS/Azure/GCP)",
                "Web application development",
                "Database design and administration",
                "Load balancing concepts",
                "Basic networking",
                "Security best practices"
            ]
        )

    @classmethod
    def create_serverless_pattern(cls) -> 'ArchitecturePattern':
        """Factory method for serverless architecture pattern"""
        return cls(
            name="Serverless Architecture",
            category=PatternCategory.SERVERLESS,
            complexity=PatternComplexity.SIMPLE,
            maturity=PatternMaturity.MATURE,
            short_description="Event-driven architecture using cloud functions without server management",
            detailed_description="""
            Serverless architecture allows you to build and run applications without managing servers.
            The cloud provider automatically provisions, scales, and manages the infrastructure required
            to run your code. You only pay for the compute time you consume.

            Key characteristics:
            - Event-driven execution
            - Automatic scaling
            - Pay-per-use pricing
            - No server management
            - Built-in high availability
            """,
            suitable_for=[
                "Event-driven applications",
                "APIs with variable traffic",
                "Data processing workflows",
                "Microservices",
                "Rapid prototyping"
            ],
            not_suitable_for=[
                "Long-running processes",
                "Applications requiring persistent connections",
                "High-performance computing",
                "Legacy applications with specific runtime requirements"
            ],
            capabilities={
                "auto_scaling": 1.0,
                "cost_optimization": 0.9,
                "event_driven": 1.0,
                "high_availability": 0.9,
                "rapid_deployment": 1.0,
                "maintenance_free": 1.0
            },
            supported_providers=["aws", "azure", "gcp"],
            required_components=[
                ComponentMapping(
                    logical_name="functions",
                    aws_service="Lambda",
                    azure_service="Functions",
                    gcp_service="Cloud Functions",
                    description="Serverless compute functions"
                ),
                ComponentMapping(
                    logical_name="api_gateway",
                    aws_service="API Gateway",
                    azure_service="API Management",
                    gcp_service="Cloud Endpoints",
                    description="HTTP API endpoint management"
                )
            ],
            optional_components=[
                ComponentMapping(
                    logical_name="database",
                    aws_service="DynamoDB",
                    azure_service="Cosmos DB",
                    gcp_service="Firestore",
                    description="NoSQL database for serverless applications",
                    is_required=False
                ),
                ComponentMapping(
                    logical_name="storage",
                    aws_service="S3",
                    azure_service="Blob Storage",
                    gcp_service="Cloud Storage",
                    description="Object storage for files and static content",
                    is_required=False
                )
            ],
            min_scale="small",
            max_scale="enterprise",
            supports_auto_scaling=True,
            horizontal_scaling=True,
            vertical_scaling=False,
            typical_response_time_ms=100,
            availability_target=0.999,
            cost_model="variable",
            estimated_implementation_weeks=2,
            team_size_recommendation="1-3 people",
            maintenance_complexity="low"
        )

    @classmethod
    def create_microservices_pattern(cls) -> 'ArchitecturePattern':
        """Factory method for microservices architecture pattern"""
        return cls(
            name="Microservices Architecture",
            category=PatternCategory.MICROSERVICES,
            complexity=PatternComplexity.COMPLEX,
            maturity=PatternMaturity.MATURE,
            short_description="Distributed architecture with independent, loosely coupled services",
            detailed_description="""
            Microservices architecture structures an application as a collection of loosely coupled services.
            Each service is independently deployable and scalable, owns its data, and communicates via APIs.

            Benefits:
            - Independent deployment and scaling
            - Technology diversity
            - Team autonomy
            - Fault isolation
            - Better testability

            Challenges:
            - Increased complexity
            - Network latency
            - Data consistency
            - Monitoring complexity
            """,
            suitable_for=[
                "Large, complex applications",
                "Multiple development teams",
                "Need for independent scaling",
                "Technology diversity requirements",
                "High availability requirements"
            ],
            not_suitable_for=[
                "Small applications",
                "Single development team",
                "Simple CRUD applications",
                "Applications requiring ACID transactions"
            ],
            capabilities={
                "scalability": 1.0,
                "fault_tolerance": 0.9,
                "technology_diversity": 1.0,
                "team_autonomy": 1.0,
                "independent_deployment": 1.0,
                "monitoring_complexity": 0.3  # Higher complexity = lower score
            },
            supported_providers=["aws", "azure", "gcp", "kubernetes"],
            min_scale="medium",
            max_scale="enterprise",
            supports_auto_scaling=True,
            horizontal_scaling=True,
            estimated_implementation_weeks=12,
            team_size_recommendation="8+ people",
            maintenance_complexity="high"
        )

    # ===== UTILITY METHODS =====

    def get_component_by_provider(self, component_name: str, provider: str) -> Optional[str]:
        """Get the cloud-specific service name for a component"""
        for component in self.required_components + self.optional_components:
            if component.logical_name == component_name:
                return getattr(component, f"{provider}_service", None)
        return None

    def get_estimated_cost(self, scale_level: str) -> Optional[CostEstimate]:
        """Get cost estimate for a specific scale level"""
        for estimate in self.cost_estimates:
            if estimate.scale_level == scale_level:
                return estimate
        return None

    def get_variant(self, variant_name: str) -> Optional[PatternVariant]:
        """Get a specific pattern variant"""
        for variant in self.variants:
            if variant.name == variant_name:
                return variant
        return None

    def calculate_suitability_score(self, requirements: Dict[str, Any]) -> float:
        """Calculate how well this pattern fits the given requirements"""
        score = 0.0
        factors = 0

        # Application type compatibility
        app_type = requirements.get('application_type', '')
        if app_type in self.suitable_for:
            score += 1.0
        elif app_type in self.not_suitable_for:
            score += 0.1
        else:
            score += 0.5
        factors += 1

        # Scale compatibility
        required_scale = requirements.get('scale_level', 'medium')
        scale_order = ['small', 'medium', 'large', 'enterprise']

        if (scale_order.index(self.min_scale) <= scale_order.index(required_scale) <=
            scale_order.index(self.max_scale)):
            score += 1.0
        else:
            score += 0.3
        factors += 1

        # Complexity appropriateness
        team_experience = requirements.get('team_experience', 'intermediate')
        complexity_scores = {
            'beginner': {'simple': 1.0, 'moderate': 0.6, 'complex': 0.2, 'very_complex': 0.1},
            'intermediate': {'simple': 0.8, 'moderate': 1.0, 'complex': 0.7, 'very_complex': 0.3},
            'advanced': {'simple': 0.6, 'moderate': 0.8, 'complex': 1.0, 'very_complex': 0.8},
            'expert': {'simple': 0.5, 'moderate': 0.7, 'complex': 0.9, 'very_complex': 1.0}
        }

        if team_experience in complexity_scores:
            score += complexity_scores[team_experience].get(self.complexity.value, 0.5)
            factors += 1

        return score / factors if factors > 0 else 0.5

    def generate_diagram_code(self, provider: str = "aws", app_name: str = "Architecture") -> str:
        """Generate Python diagrams code for this pattern"""
        if not self.diagram_template:
            return self._generate_basic_diagram_code(provider, app_name)

        # Replace template variables
        template = self.diagram_template

        # Map components to provider-specific services
        component_mappings = {}
        for component in self.required_components:
            service = self.get_component_by_provider(component.logical_name, provider)
            if service:
                component_mappings[component.logical_name] = service

        # Format template
        try:
            return template.format(
                provider=provider,
                app_name=app_name,
                **component_mappings
            )
        except KeyError as e:
            return f"# Error generating code: Missing mapping for {e}"

    def _generate_basic_diagram_code(self, provider: str, app_name: str) -> str:
        """Generate basic diagram code when no template is available"""
        imports = []
        components = []

        for component in self.required_components[:3]:  # Limit to first 3 for simplicity
            service = self.get_component_by_provider(component.logical_name, provider)
            if service:
                # Simplified import generation
                category = "compute" if "compute" in component.logical_name else "general"
                imports.append(f"from diagrams.{provider}.{category} import {service}")
                components.append(f'{component.logical_name} = {service}("{component.logical_name.title()}")')

        return f'''
from diagrams import Diagram

{chr(10).join(imports)}

with Diagram("{app_name}", show=False):
    {chr(10).join(components)}
'''

    def to_dict(self) -> Dict[str, Any]:
        """Convert pattern to dictionary for serialization"""
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category.value,
            'complexity': self.complexity.value,
            'maturity': self.maturity.value,
            'short_description': self.short_description,
            'detailed_description': self.detailed_description,
            'suitable_for': self.suitable_for,
            'capabilities': self.capabilities,
            'supported_providers': self.supported_providers,
            'required_components': [
                {
                    'logical_name': c.logical_name,
                    'aws_service': c.aws_service,
                    'azure_service': c.azure_service,
                    'gcp_service': c.gcp_service,
                    'description': c.description,
                    'is_required': c.is_required
                }
                for c in self.required_components
            ],
            'cost_estimates': [
                {
                    'scale_level': c.scale_level,
                    'monthly_range_min': c.monthly_range_min,
                    'monthly_range_max': c.monthly_range_max,
                    'cost_breakdown': c.cost_breakdown
                }
                for c in self.cost_estimates
            ],
            'implementation_weeks': self.estimated_implementation_weeks,
            'team_size': self.team_size_recommendation,
            'tags': self.tags
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ArchitecturePattern':
        """Create pattern from dictionary"""
        # Convert enum strings back to enums
        category = PatternCategory(data.get('category', 'web_application'))
        complexity = PatternComplexity(data.get('complexity', 'moderate'))
        maturity = PatternMaturity(data.get('maturity', 'mature'))

        # Create basic pattern
        pattern = cls(
            id=data.get('id', str(uuid.uuid4())),
            name=data.get('name', ''),
            category=category,
            complexity=complexity,
            maturity=maturity,
            short_description=data.get('short_description', ''),
            detailed_description=data.get('detailed_description', ''),
            suitable_for=data.get('suitable_for', []),
            capabilities=data.get('capabilities', {}),
            supported_providers=data.get('supported_providers', []),
            estimated_implementation_weeks=data.get('implementation_weeks', 4),
            team_size_recommendation=data.get('team_size', '2-4 people'),
            tags=data.get('tags', [])
        )

        # Reconstruct component mappings
        for comp_data in data.get('required_components', []):
            component = ComponentMapping(
                logical_name=comp_data['logical_name'],
                aws_service=comp_data.get('aws_service'),
                azure_service=comp_data.get('azure_service'),
                gcp_service=comp_data.get('gcp_service'),
                description=comp_data.get('description', ''),
                is_required=comp_data.get('is_required', True)
            )
            pattern.required_components.append(component)

        # Reconstruct cost estimates
        for cost_data in data.get('cost_estimates', []):
            cost_estimate = CostEstimate(
                scale_level=cost_data['scale_level'],
                monthly_range_min=cost_data['monthly_range_min'],
                monthly_range_max=cost_data['monthly_range_max'],
                cost_breakdown=cost_data.get('cost_breakdown', {})
            )
            pattern.cost_estimates.append(cost_estimate)

        return pattern


# ===== PATTERN REGISTRY =====

class PatternRegistry:
    """Registry for managing and discovering architecture patterns"""

    def __init__(self):
        self.patterns: Dict[str, ArchitecturePattern] = {}
        self._initialize_default_patterns()

    def _initialize_default_patterns(self):
        """Initialize with default patterns"""
        patterns = [
            ArchitecturePattern.create_three_tier_web_app(),
            ArchitecturePattern.create_serverless_pattern(),
            ArchitecturePattern.create_microservices_pattern()
        ]

        for pattern in patterns:
            self.register_pattern(pattern)

    def register_pattern(self, pattern: ArchitecturePattern):
        """Register a new pattern"""
        self.patterns[pattern.id] = pattern

    def get_pattern(self, pattern_id: str) -> Optional[ArchitecturePattern]:
        """Get pattern by ID"""
        return self.patterns.get(pattern_id)

    def find_patterns_by_category(self, category: PatternCategory) -> List[ArchitecturePattern]:
        """Find patterns by category"""
        return [p for p in self.patterns.values() if p.category == category]

    def find_patterns_by_provider(self, provider: str) -> List[ArchitecturePattern]:
        """Find patterns supporting a specific provider"""
        return [p for p in self.patterns.values() if provider in p.supported_providers]

    def search_patterns(self, query: str) -> List[ArchitecturePattern]:
        """Search patterns by name, description, or keywords"""
        query = query.lower()
        results = []

        for pattern in self.patterns.values():
            # Search in name and description
            if (query in pattern.name.lower() or
                query in pattern.short_description.lower() or
                query in pattern.detailed_description.lower()):
                results.append(pattern)
                continue

            # Search in keywords and tags
            if any(query in keyword.lower() for keyword in pattern.keywords + pattern.tags):
                results.append(pattern)
                continue

            # Search in suitable_for
            if any(query in use_case.lower() for use_case in pattern.suitable_for):
                results.append(pattern)

        return results

    def get_patterns_by_complexity(self, max_complexity: PatternComplexity) -> List[ArchitecturePattern]:
        """Get patterns up to a certain complexity level"""
        complexity_order = [
            PatternComplexity.SIMPLE,
            PatternComplexity.MODERATE,
            PatternComplexity.COMPLEX,
            PatternComplexity.VERY_COMPLEX
        ]

        max_index = complexity_order.index(max_complexity)
        return [
            p for p in self.patterns.values()
            if complexity_order.index(p.complexity) <= max_index
        ]

    def recommend_patterns(self, requirements: Dict[str, Any]) -> List[Tuple[ArchitecturePattern, float]]:
        """Recommend patterns based on requirements with scores"""
        recommendations = []

        for pattern in self.patterns.values():
            score = pattern.calculate_suitability_score(requirements)
            if score > 0.4:  # Minimum threshold
                recommendations.append((pattern, score))

        # Sort by score (highest first)
        recommendations.sort(key=lambda x: x[1], reverse=True)
        return recommendations[:10]  # Top 10 recommendations

    def export_patterns(self, file_path: str):
        """Export all patterns to JSON file"""
        patterns_data = {
            'patterns': [pattern.to_dict() for pattern in self.patterns.values()],
            'exported_at': datetime.now().isoformat(),
            'version': '1.0'
        }

        with open(file_path, 'w') as f:
            json.dump(patterns_data, f, indent=2)

    def import_patterns(self, file_path: str):
        """Import patterns from JSON file"""
        with open(file_path, 'r') as f:
            data = json.load(f)

        for pattern_data in data.get('patterns', []):
            pattern = ArchitecturePattern.from_dict(pattern_data)
            self.register_pattern(pattern)
