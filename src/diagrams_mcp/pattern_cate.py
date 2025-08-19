# src/diagrams_mcp/models/pattern.py

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
import json

class PatternCategory(Enum):
    """Categories of architecture patterns"""

    # Web Application Patterns
    WEB_APPLICATION = "web_application"
    THREE_TIER = "three_tier"
    JAMSTACK = "jamstack"
    PROGRESSIVE_WEB_APP = "progressive_web_app"
    SINGLE_PAGE_APP = "single_page_app"

    # API & Service Patterns
    API_GATEWAY = "api_gateway"
    MICROSERVICES = "microservices"
    SERVICE_MESH = "service_mesh"
    RESTFUL_API = "restful_api"
    GRAPHQL_API = "graphql_api"

    # Serverless Patterns
    SERVERLESS = "serverless"
    FUNCTION_AS_SERVICE = "function_as_service"
    EVENT_DRIVEN = "event_driven"
    SERVERLESS_API = "serverless_api"

    # Data Processing Patterns
    DATA_PIPELINE = "data_pipeline"
    BATCH_PROCESSING = "batch_processing"
    STREAM_PROCESSING = "stream_processing"
    ETL_PIPELINE = "etl_pipeline"
    DATA_LAKE = "data_lake"
    DATA_WAREHOUSE = "data_warehouse"

    # Container & Orchestration Patterns
    CONTAINERIZED = "containerized"
    KUBERNETES = "kubernetes"
    DOCKER_SWARM = "docker_swarm"
    CONTAINER_ORCHESTRATION = "container_orchestration"

    # Distributed System Patterns
    DISTRIBUTED_SYSTEM = "distributed_system"
    LOAD_BALANCED = "load_balanced"
    AUTO_SCALING = "auto_scaling"
    HIGH_AVAILABILITY = "high_availability"
    DISASTER_RECOVERY = "disaster_recovery"

    # E-commerce Specific
    E_COMMERCE = "e_commerce"
    MARKETPLACE = "marketplace"
    PAYMENT_PROCESSING = "payment_processing"
    INVENTORY_MANAGEMENT = "inventory_management"

    # Mobile & IoT Patterns
    MOBILE_BACKEND = "mobile_backend"
    IOT_PLATFORM = "iot_platform"
    EDGE_COMPUTING = "edge_computing"
    REAL_TIME_MESSAGING = "real_time_messaging"

    # Security Patterns
    ZERO_TRUST = "zero_trust"
    MULTI_TENANT = "multi_tenant"
    SECURE_API = "secure_api"
    COMPLIANCE_READY = "compliance_ready"

    # Content & Media Patterns
    CONTENT_MANAGEMENT = "content_management"
    MEDIA_STREAMING = "media_streaming"
    CDN_OPTIMIZED = "cdn_optimized"
    STATIC_SITE = "static_site"

    # Analytics & ML Patterns
    ANALYTICS_PLATFORM = "analytics_platform"
    MACHINE_LEARNING = "machine_learning"
    DATA_SCIENCE = "data_science"
    BUSINESS_INTELLIGENCE = "business_intelligence"

    # Legacy & Hybrid Patterns
    MONOLITHIC = "monolithic"
    HYBRID_CLOUD = "hybrid_cloud"
    MULTI_CLOUD = "multi_cloud"
    LEGACY_MODERNIZATION = "legacy_modernization"

    # Specialized Patterns
    FINTECH = "fintech"
    HEALTHCARE = "healthcare"
    GAMING = "gaming"
    SOCIAL_MEDIA = "social_media"

    def get_display_name(self) -> str:
        """Get human-readable display name"""
        display_names = {
            # Web Applications
            self.WEB_APPLICATION: "Web Application",
            self.THREE_TIER: "3-Tier Web Application",
            self.JAMSTACK: "JAMstack",
            self.PROGRESSIVE_WEB_APP: "Progressive Web App",
            self.SINGLE_PAGE_APP: "Single Page Application",

            # API & Services
            self.API_GATEWAY: "API Gateway",
            self.MICROSERVICES: "Microservices",
            self.SERVICE_MESH: "Service Mesh",
            self.RESTFUL_API: "RESTful API",
            self.GRAPHQL_API: "GraphQL API",

            # Serverless
            self.SERVERLESS: "Serverless",
            self.FUNCTION_AS_SERVICE: "Function as a Service",
            self.EVENT_DRIVEN: "Event-Driven Architecture",
            self.SERVERLESS_API: "Serverless API",

            # Data Processing
            self.DATA_PIPELINE: "Data Pipeline",
            self.BATCH_PROCESSING: "Batch Processing",
            self.STREAM_PROCESSING: "Stream Processing",
            self.ETL_PIPELINE: "ETL Pipeline",
            self.DATA_LAKE: "Data Lake",
            self.DATA_WAREHOUSE: "Data Warehouse",

            # Containers
            self.CONTAINERIZED: "Containerized Application",
            self.KUBERNETES: "Kubernetes",
            self.DOCKER_SWARM: "Docker Swarm",
            self.CONTAINER_ORCHESTRATION: "Container Orchestration",

            # Distributed Systems
            self.DISTRIBUTED_SYSTEM: "Distributed System",
            self.LOAD_BALANCED: "Load Balanced",
            self.AUTO_SCALING: "Auto Scaling",
            self.HIGH_AVAILABILITY: "High Availability",
            self.DISASTER_RECOVERY: "Disaster Recovery",

            # E-commerce
            self.E_COMMERCE: "E-commerce Platform",
            self.MARKETPLACE: "Marketplace",
            self.PAYMENT_PROCESSING: "Payment Processing",
            self.INVENTORY_MANAGEMENT: "Inventory Management",

            # Mobile & IoT
            self.MOBILE_BACKEND: "Mobile Backend",
            self.IOT_PLATFORM: "IoT Platform",
            self.EDGE_COMPUTING: "Edge Computing",
            self.REAL_TIME_MESSAGING: "Real-time Messaging",

            # Security
            self.ZERO_TRUST: "Zero Trust",
            self.MULTI_TENANT: "Multi-Tenant",
            self.SECURE_API: "Secure API",
            self.COMPLIANCE_READY: "Compliance Ready",

            # Content & Media
            self.CONTENT_MANAGEMENT: "Content Management",
            self.MEDIA_STREAMING: "Media Streaming",
            self.CDN_OPTIMIZED: "CDN Optimized",
            self.STATIC_SITE: "Static Site",

            # Analytics & ML
            self.ANALYTICS_PLATFORM: "Analytics Platform",
            self.MACHINE_LEARNING: "Machine Learning",
            self.DATA_SCIENCE: "Data Science",
            self.BUSINESS_INTELLIGENCE: "Business Intelligence",

            # Legacy & Hybrid
            self.MONOLITHIC: "Monolithic",
            self.HYBRID_CLOUD: "Hybrid Cloud",
            self.MULTI_CLOUD: "Multi-Cloud",
            self.LEGACY_MODERNIZATION: "Legacy Modernization",

            # Specialized
            self.FINTECH: "Financial Technology",
            self.HEALTHCARE: "Healthcare",
            self.GAMING: "Gaming",
            self.SOCIAL_MEDIA: "Social Media"
        }

        return display_names.get(self, self.value.replace('_', ' ').title())

    def get_description(self) -> str:
        """Get detailed description of the pattern category"""
        descriptions = {
            # Web Applications
            self.THREE_TIER: "Traditional web application with presentation, business logic, and data layers",
            self.JAMSTACK: "Modern web development architecture based on client-side JavaScript, reusable APIs, and prebuilt Markup",
            self.PROGRESSIVE_WEB_APP: "Web applications that provide native app-like experience with offline capabilities",

            # API & Services
            self.MICROSERVICES: "Architecture style that structures an application as a collection of loosely coupled services",
            self.API_GATEWAY: "Single entry point for all client requests, providing routing, authentication, and rate limiting",
            self.SERVICE_MESH: "Dedicated infrastructure layer for handling service-to-service communication",

            # Serverless
            self.SERVERLESS: "Cloud computing model where the cloud provider manages the infrastructure",
            self.EVENT_DRIVEN: "Architecture pattern that produces and consumes events to trigger and communicate between services",

            # Data Processing
            self.DATA_PIPELINE: "Series of data processing steps to move data from source to destination",
            self.STREAM_PROCESSING: "Real-time processing of continuous data streams",
            self.DATA_LAKE: "Centralized repository for storing structured and unstructured data at scale",

            # Containers
            self.KUBERNETES: "Container orchestration platform for automating deployment, scaling, and operations",
            self.CONTAINERIZED: "Applications packaged with their dependencies in lightweight, portable containers",

            # E-commerce
            self.E_COMMERCE: "Online platform for buying and selling products or services",
            self.MARKETPLACE: "Platform that connects multiple sellers with buyers",

            # Mobile & IoT
            self.MOBILE_BACKEND: "Server-side infrastructure specifically designed to support mobile applications",
            self.IOT_PLATFORM: "Infrastructure for connecting, managing, and processing data from IoT devices",

            # Security
            self.ZERO_TRUST: "Security model that requires verification for every user and device",
            self.MULTI_TENANT: "Architecture where multiple customers share the same application instance",

            # Analytics & ML
            self.ANALYTICS_PLATFORM: "Infrastructure for collecting, processing, and analyzing large datasets",
            self.MACHINE_LEARNING: "Platform for developing, training, and deploying ML models",

            # Legacy & Hybrid
            self.MONOLITHIC: "Traditional application architecture where all components are interconnected and interdependent",
            self.HYBRID_CLOUD: "Computing environment that combines on-premises and cloud resources"
        }

        return descriptions.get(self, f"Architecture pattern: {self.get_display_name()}")

    def get_typical_use_cases(self) -> List[str]:
        """Get typical use cases for this pattern category"""
        use_cases = {
            self.THREE_TIER: [
                "Traditional web applications",
                "Enterprise applications",
                "E-commerce websites",
                "Content management systems"
            ],
            self.MICROSERVICES: [
                "Large-scale applications",
                "Multiple development teams",
                "Independent service scaling",
                "Technology diversity requirements"
            ],
            self.SERVERLESS: [
                "Event-driven applications",
                "Variable workloads",
                "Cost-optimized solutions",
                "Rapid prototyping"
            ],
            self.DATA_PIPELINE: [
                "ETL processes",
                "Data integration",
                "Analytics workflows",
                "Data migration"
            ],
            self.KUBERNETES: [
                "Container orchestration",
                "Multi-cloud deployments",
                "Auto-scaling applications",
                "DevOps workflows"
            ],
            self.E_COMMERCE: [
                "Online stores",
                "Digital marketplaces",
                "B2B platforms",
                "Subscription services"
            ],
            self.MOBILE_BACKEND: [
                "Mobile app APIs",
                "Push notifications",
                "User authentication",
                "Data synchronization"
            ],
            self.IOT_PLATFORM: [
                "Device management",
                "Sensor data processing",
                "Industrial monitoring",
                "Smart home systems"
            ],
            self.ANALYTICS_PLATFORM: [
                "Business intelligence",
                "Real-time dashboards",
                "Data visualization",
                "Performance monitoring"
            ]
        }

        return use_cases.get(self, ["General purpose applications"])

    def get_complexity_level(self) -> str:
        """Get typical complexity level for this pattern category"""
        complexity_levels = {
            # Simple patterns
            self.STATIC_SITE: "simple",
            self.JAMSTACK: "simple",
            self.SERVERLESS_API: "simple",

            # Moderate patterns
            self.THREE_TIER: "moderate",
            self.RESTFUL_API: "moderate",
            self.CONTAINERIZED: "moderate",
            self.MOBILE_BACKEND: "moderate",

            # Complex patterns
            self.MICROSERVICES: "complex",
            self.KUBERNETES: "complex",
            self.DATA_PIPELINE: "complex",
            self.E_COMMERCE: "complex",

            # Very complex patterns
            self.SERVICE_MESH: "very_complex",
            self.MULTI_CLOUD: "very_complex",
            self.ZERO_TRUST: "very_complex",
            self.IOT_PLATFORM: "very_complex"
        }

        return complexity_levels.get(self, "moderate")

    @classmethod
    def get_categories_by_application_type(cls, app_type: str) -> List['PatternCategory']:
        """Get relevant pattern categories for an application type"""
        mappings = {
            'web_application': [
                cls.THREE_TIER, cls.JAMSTACK, cls.PROGRESSIVE_WEB_APP,
                cls.SINGLE_PAGE_APP, cls.MONOLITHIC
            ],
            'api_service': [
                cls.API_GATEWAY, cls.RESTFUL_API, cls.GRAPHQL_API,
                cls.MICROSERVICES, cls.SERVERLESS_API
            ],
            'mobile_app': [
                cls.MOBILE_BACKEND, cls.API_GATEWAY, cls.SERVERLESS,
                cls.REAL_TIME_MESSAGING
            ],
            'e_commerce': [
                cls.E_COMMERCE, cls.MARKETPLACE, cls.PAYMENT_PROCESSING,
                cls.THREE_TIER, cls.MICROSERVICES
            ],
            'data_analytics': [
                cls.ANALYTICS_PLATFORM, cls.DATA_PIPELINE, cls.DATA_LAKE,
                cls.DATA_WAREHOUSE, cls.STREAM_PROCESSING
            ],
            'iot': [
                cls.IOT_PLATFORM, cls.EDGE_COMPUTING, cls.STREAM_PROCESSING,
                cls.EVENT_DRIVEN
            ],
            'fintech': [
                cls.FINTECH, cls.SECURE_API, cls.COMPLIANCE_READY,
                cls.ZERO_TRUST, cls.MICROSERVICES
            ],
            'social_media': [
                cls.SOCIAL_MEDIA, cls.REAL_TIME_MESSAGING, cls.MICROSERVICES,
                cls.CDN_OPTIMIZED
            ]
        }

        return mappings.get(app_type, [cls.WEB_APPLICATION])


class PatternComplexity(Enum):
    """Complexity levels for architecture patterns"""
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"
    VERY_COMPLEX = "very_complex"

    def get_description(self) -> str:
        descriptions = {
            self.SIMPLE: "Easy to implement and maintain, suitable for beginners",
            self.MODERATE: "Balanced complexity, good for most teams",
            self.COMPLEX: "Requires experienced team, advanced features",
            self.VERY_COMPLEX: "Expert-level implementation, enterprise features"
        }
        return descriptions[self]

    def get_team_requirements(self) -> Dict[str, Any]:
        requirements = {
            self.SIMPLE: {
                "min_team_size": 1,
                "experience_level": "beginner",
                "setup_time_weeks": 1,
                "maintenance_effort": "low"
            },
            self.MODERATE: {
                "min_team_size": 2,
                "experience_level": "intermediate",
                "setup_time_weeks": 4,
                "maintenance_effort": "medium"
            },
            self.COMPLEX: {
                "min_team_size": 5,
                "experience_level": "experienced",
                "setup_time_weeks": 8,
                "maintenance_effort": "high"
            },
            self.VERY_COMPLEX: {
                "min_team_size": 10,
                "experience_level": "expert",
                "setup_time_weeks": 16,
                "maintenance_effort": "very_high"
            }
        }
        return requirements[self]


class PatternMaturity(Enum):
    """Maturity levels for architecture patterns"""
    EXPERIMENTAL = "experimental"
    EMERGING = "emerging"
    MATURE = "mature"
    INDUSTRY_STANDARD = "industry_standard"
    LEGACY = "legacy"

    def get_risk_level(self) -> str:
        risk_levels = {
            self.EXPERIMENTAL: "high",
            self.EMERGING: "medium-high",
            self.MATURE: "low",
            self.INDUSTRY_STANDARD: "very_low",
            self.LEGACY: "medium"
        }
        return risk_levels[self]

    def get_description(self) -> str:
        descriptions = {
            self.EXPERIMENTAL: "Cutting-edge, unproven in production",
            self.EMERGING: "Gaining adoption, some production use",
            self.MATURE: "Well-established, proven in production",
            self.INDUSTRY_STANDARD: "Widely adopted, battle-tested",
            self.LEGACY: "Older approach, being replaced"
        }
        return descriptions[self]


@dataclass
class ArchitecturePattern:
    """Complete architecture pattern definition"""

    # Basic Information
    name: str
    category: PatternCategory
    complexity: PatternComplexity
    maturity: PatternMaturity
    description: str

    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    version: str = "1.0"
    created_date: str = ""
    last_updated: str = ""

    # Capabilities and Features
    capabilities: Dict[str, float] = field(default_factory=dict)  # capability -> score (0-1)
    supported_providers: List[str] = field(default_factory=list)  # aws, azure, gcp, etc.
    compatible_technologies: List[str] = field(default_factory=list)

    # Characteristics
    scale_characteristics: Dict[str, Any] = field(default_factory=dict)
    security_characteristics: Dict[str, Any] = field(default_factory=dict)
    performance_characteristics: Dict[str, Any] = field(default_factory=dict)
    cost_characteristics: Dict[str, Any] = field(default_factory=dict)
    implementation_characteristics: Dict[str, Any] = field(default_factory=dict)

    # Architecture Components
    required_components: List[str] = field(default_factory=list)
    optional_components: List[str] = field(default_factory=list)
    service_mappings: Dict[str, Dict[str, str]] = field(default_factory=dict)  # provider -> component -> service

    # Documentation and Examples
    documentation_url: str = ""
    example_code: str = ""
    diagram_template: str = ""

    # Pattern Relationships
    alternatives: List[str] = field(default_factory=list)  # Alternative pattern names
    evolution_paths: List[str] = field(default_factory=list)  # Patterns this can evolve to
    prerequisites: List[str] = field(default_factory=list)  # Required knowledge/infrastructure

    def __post_init__(self):
        """Initialize default values based on category"""
        if not self.metadata:
            self.metadata = {
                "suitable_for": self.category.get_typical_use_cases(),
                "tags": [self.category.value],
                "difficulty": self.complexity.value
            }

        if not self.scale_characteristics:
            self.scale_characteristics = self._get_default_scale_characteristics()

        if not self.security_characteristics:
            self.security_characteristics = self._get_default_security_characteristics()

    def _get_default_scale_characteristics(self) -> Dict[str, Any]:
        """Get default scale characteristics based on category"""
        defaults = {
            PatternCategory.SERVERLESS: {
                "supported_scales": ["small", "medium", "large"],
                "auto_scaling": True,
                "max_concurrent_users": 1000000,
                "scaling_method": "automatic"
            },
            PatternCategory.MICROSERVICES: {
                "supported_scales": ["medium", "large", "enterprise"],
                "auto_scaling": True,
                "max_concurrent_users": 10000000,
                "scaling_method": "horizontal"
            },
            PatternCategory.THREE_TIER: {
                "supported_scales": ["small", "medium", "large"],
                "auto_scaling": False,
                "max_concurrent_users": 100000,
                "scaling_method": "vertical"
            }
        }

        return defaults.get(self.category, {
            "supported_scales": ["small", "medium"],
            "auto_scaling": False,
            "max_concurrent_users": 10000,
            "scaling_method": "manual"
        })

    def _get_default_security_characteristics(self) -> Dict[str, Any]:
        """Get default security characteristics based on category"""
        defaults = {
            PatternCategory.ZERO_TRUST: {
                "security_level": 4,
                "encryption_at_rest": True,
                "encryption_in_transit": True,
                "authentication_required": True,
                "compliance_frameworks": ["SOC2", "PCI-DSS", "HIPAA"]
            },
            PatternCategory.FINTECH: {
                "security_level": 4,
                "encryption_at_rest": True,
                "encryption_in_transit": True,
                "authentication_required": True,
                "compliance_frameworks": ["PCI-DSS", "SOX"]
            }
        }

        return defaults.get(self.category, {
            "security_level": 2,
            "encryption_at_rest": False,
            "encryption_in_transit": True,
            "authentication_required": True,
            "compliance_frameworks": []
        })

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ArchitecturePattern':
        """Create ArchitecturePattern from dictionary"""
        # Convert string enums back to enum objects
        category = PatternCategory(data.get('category', 'web_application'))
        complexity = PatternComplexity(data.get('complexity', 'moderate'))
        maturity = PatternMaturity(data.get('maturity', 'mature'))

        return cls(
            name=data['name'],
            category=category,
            complexity=complexity,
            maturity=maturity,
            description=data.get('description', ''),
            metadata=data.get('metadata', {}),
            capabilities=data.get('capabilities', {}),
            supported_providers=data.get('supported_providers', []),
            compatible_technologies=data.get('compatible_technologies', []),
            scale_characteristics=data.get('scale_characteristics', {}),
            security_characteristics=data.get('security_characteristics', {}),
            performance_characteristics=data.get('performance_characteristics', {}),
            cost_characteristics=data.get('cost_characteristics', {}),
            implementation_characteristics=data.get('implementation_characteristics', {}),
            required_components=data.get('required_components', []),
            optional_components=data.get('optional_components', []),
            service_mappings=data.get('service_mappings', {}),
            alternatives=data.get('alternatives', []),
            evolution_paths=data.get('evolution_paths', []),
            prerequisites=data.get('prerequisites', [])
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert ArchitecturePattern to dictionary"""
        return {
            'name': self.name,
            'category': self.category.value,
            'complexity': self.complexity.value,
            'maturity': self.maturity.value,
            'description': self.description,
            'metadata': self.metadata,
            'capabilities': self.capabilities,
            'supported_providers': self.supported_providers,
            'compatible_technologies': self.compatible_technologies,
            'scale_characteristics': self.scale_characteristics,
            'security_characteristics': self.security_characteristics,
            'performance_characteristics': self.performance_characteristics,
            'cost_characteristics': self.cost_characteristics,
            'implementation_characteristics': self.implementation_characteristics,
            'required_components': self.required_components,
            'optional_components': self.optional_components,
            'service_mappings': self.service_mappings,
            'alternatives': self.alternatives,
            'evolution_paths': self.evolution_paths,
            'prerequisites': self.prerequisites
        }

    def get_suitability_score(self, app_type: str, scale: str, security_level: int) -> float:
        """Calculate suitability score for given requirements"""
        score = 0.0
        factors = 0

        # Application type fit
        suitable_apps = self.metadata.get('suitable_for', [])
        if app_type in [app.lower() for app in suitable_apps]:
            score += 1.0
        elif any(app_type in app.lower() for app in suitable_apps):
            score += 0.7
        else:
            score += 0.3
        factors += 1

        # Scale fit
        supported_scales = self.scale_characteristics.get('supported_scales', [])
        if scale in supported_scales:
            score += 1.0
        elif self.scale_characteristics.get('auto_scaling'):
            score += 0.8
        else:
            score += 0.4
        factors += 1

        # Security fit
        pattern_security = self.security_characteristics.get('security_level', 2)
        if pattern_security >= security_level:
            score += 1.0
        else:
            score += max(0.3, 1.0 - (security_level - pattern_security) * 0.2)
        factors += 1

        return score / factors if factors > 0 else 0.5


# Example usage and pattern definitions
def create_example_patterns():
    """Create example pattern definitions"""

    # 3-Tier Web Application Pattern
    three_tier = ArchitecturePattern(
        name="3-Tier Web Application",
        category=PatternCategory.THREE_TIER,
        complexity=PatternComplexity.MODERATE,
        maturity=PatternMaturity.INDUSTRY_STANDARD,
        description="Traditional web application with presentation, business logic, and data layers",
        capabilities={
            "user_authentication": 0.9,
            "database": 1.0,
            "load_balancing": 0.8,
            "caching": 0.7,
            "monitoring": 0.6
        },
        supported_providers=["aws", "azure", "gcp"],
        required_components=["load_balancer", "compute", "database"],
        optional_components=["cdn", "cache", "monitoring"],
        service_mappings={
            "aws": {
                "load_balancer": "ALB",
                "compute": "EC2",
                "database": "RDS",
                "cdn": "CloudFront"
            },
            "azure": {
                "load_balancer": "Application Gateway",
                "compute": "Virtual Machines",
                "database": "SQL Database",
                "cdn": "Azure CDN"
            }
        }
    )

    # Serverless Pattern
    serverless = ArchitecturePattern(
        name="Serverless Architecture",
        category=PatternCategory.SERVERLESS,
        complexity=PatternComplexity.SIMPLE,
        maturity=PatternMaturity.MATURE,
        description="Event-driven compute without server management",
        capabilities={
            "auto_scaling": 1.0,
            "cost_optimization": 0.9,
            "event_driven": 1.0,
            "pay_per_use": 1.0
        },
        supported_providers=["aws", "azure", "gcp"],
        required_components=["functions", "api_gateway"],
        optional_components=["database", "storage", "messaging"],
        cost_characteristics={"cost_level": "low", "pricing_model": "pay_per_use"}
    )

    return [three_tier, serverless]
