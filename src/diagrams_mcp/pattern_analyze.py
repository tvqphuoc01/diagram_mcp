# src/diagrams_mcp/ai/requirement_analyzer.py

import re
import json
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class RequirementType(Enum):
    FUNCTIONAL = "functional"
    NON_FUNCTIONAL = "non_functional"
    TECHNICAL = "technical"
    BUSINESS = "business"

class ScaleLevel(Enum):
    SMALL = "small"          # < 1000 users
    MEDIUM = "medium"        # 1K - 100K users
    LARGE = "large"          # 100K - 1M users
    ENTERPRISE = "enterprise" # > 1M users

class SecurityLevel(Enum):
    BASIC = "basic"
    STANDARD = "standard"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class AnalyzedRequirement:
    """Represents a single analyzed requirement"""
    text: str
    type: RequirementType
    confidence: float
    keywords: List[str]
    implications: List[str]

@dataclass
class RequirementAnalysis:
    """Complete analysis of user requirements"""
    raw_input: str
    application_type: str
    scale_level: ScaleLevel
    security_level: SecurityLevel
    performance_requirements: Dict[str, Any]
    functional_requirements: List[AnalyzedRequirement]
    technical_constraints: Dict[str, Any]
    business_constraints: Dict[str, Any]
    suggested_services: List[str]
    architecture_complexity: str
    estimated_timeline: str
    budget_range: str

class RequirementAnalyzer:
    """
    Analyzes natural language requirements and extracts structured information
    for architecture pattern matching and code generation.
    """

    def __init__(self):
        self.service_keywords = self._load_service_keywords()
        self.pattern_keywords = self._load_pattern_keywords()
        self.scale_indicators = self._load_scale_indicators()
        self.security_indicators = self._load_security_indicators()

    def analyze_requirements(self, requirements: str) -> RequirementAnalysis:
        """
        Main entry point: Analyze natural language requirements.

        Args:
            requirements: User's natural language description of their needs

        Returns:
            RequirementAnalysis object with structured analysis
        """
        logger.info(f"Analyzing requirements: {requirements[:100]}...")

        # Clean and normalize input
        normalized_text = self._normalize_text(requirements)

        # Extract different types of information
        app_type = self._identify_application_type(normalized_text)
        scale = self._determine_scale_level(normalized_text)
        security = self._assess_security_level(normalized_text)
        performance = self._extract_performance_requirements(normalized_text)
        functional = self._extract_functional_requirements(normalized_text)
        technical = self._extract_technical_constraints(normalized_text)
        business = self._extract_business_constraints(normalized_text)
        services = self._suggest_services(normalized_text, app_type)
        complexity = self._assess_complexity(functional, technical, scale)
        timeline = self._estimate_timeline(complexity, scale)
        budget = self._estimate_budget_range(scale, complexity)

        analysis = RequirementAnalysis(
            raw_input=requirements,
            application_type=app_type,
            scale_level=scale,
            security_level=security,
            performance_requirements=performance,
            functional_requirements=functional,
            technical_constraints=technical,
            business_constraints=business,
            suggested_services=services,
            architecture_complexity=complexity,
            estimated_timeline=timeline,
            budget_range=budget
        )

        logger.info(f"Analysis complete: {app_type} application, {scale.value} scale, {security.value} security")
        return analysis

    def _normalize_text(self, text: str) -> str:
        """Clean and normalize input text"""
        # Convert to lowercase
        text = text.lower()
        # Remove extra whitespace
        text = ' '.join(text.split())
        # Remove special characters but keep alphanumeric and common punctuation
        text = re.sub(r'[^\w\s\-\.,!?]', ' ', text)
        return text.strip()

    def _identify_application_type(self, text: str) -> str:
        """Identify the type of application being described"""
        app_type_patterns = {
            'e-commerce': [
                'e-commerce', 'ecommerce', 'online store', 'shopping', 'marketplace',
                'cart', 'checkout', 'payment', 'product catalog', 'inventory'
            ],
            'social_media': [
                'social media', 'social network', 'chat', 'messaging', 'feed',
                'posts', 'followers', 'likes', 'comments', 'sharing'
            ],
            'content_management': [
                'cms', 'content management', 'blog', 'articles', 'publishing',
                'editorial', 'content creation', 'website builder'
            ],
            'fintech': [
                'fintech', 'banking', 'financial', 'trading', 'investment',
                'payment processing', 'cryptocurrency', 'lending', 'insurance'
            ],
            'healthcare': [
                'healthcare', 'medical', 'patient', 'hospital', 'clinic',
                'telemedicine', 'health records', 'appointment'
            ],
            'iot': [
                'iot', 'internet of things', 'sensors', 'devices', 'telemetry',
                'monitoring', 'smart home', 'industrial'
            ],
            'data_analytics': [
                'analytics', 'dashboard', 'reporting', 'bi', 'business intelligence',
                'data visualization', 'metrics', 'kpi'
            ],
            'api_service': [
                'api', 'microservice', 'backend', 'service', 'integration',
                'webhook', 'rest api', 'graphql'
            ],
            'mobile_app': [
                'mobile app', 'ios', 'android', 'mobile backend', 'push notifications',
                'mobile first', 'responsive'
            ],
            'web_application': [
                'web app', 'website', 'web application', 'portal', 'dashboard',
                'spa', 'single page application'
            ]
        }

        # Score each application type
        scores = {}
        for app_type, keywords in app_type_patterns.items():
            score = 0
            for keyword in keywords:
                if keyword in text:
                    # Weighted scoring based on keyword importance
                    if keyword == app_type.replace('_', ' '):
                        score += 3  # Exact match gets highest score
                    else:
                        score += 1
            scores[app_type] = score

        # Return the highest scoring type, default to web_application
        if max(scores.values()) > 0:
            return max(scores, key=scores.get)
        else:
            return 'web_application'  # Default fallback

    def _determine_scale_level(self, text: str) -> ScaleLevel:
        """Determine the expected scale/size of the application"""
        scale_patterns = {
            ScaleLevel.ENTERPRISE: [
                'enterprise', 'large scale', 'millions of users', 'global',
                'high volume', 'enterprise grade', 'fortune 500'
            ],
            ScaleLevel.LARGE: [
                'large', 'thousands of users', 'high traffic', 'scalable',
                'production ready', 'commercial'
            ],
            ScaleLevel.MEDIUM: [
                'medium', 'hundreds of users', 'growing', 'startup',
                'moderate traffic', 'regional'
            ],
            ScaleLevel.SMALL: [
                'small', 'prototype', 'mvp', 'personal project', 'demo',
                'proof of concept', 'internal tool'
            ]
        }

        # Check for explicit user/traffic numbers
        user_numbers = re.findall(r'(\d+)\s*(?:k|thousand|m|million)?\s*users?', text)
        if user_numbers:
            num_str = user_numbers[0]
            if 'k' in text or 'thousand' in text:
                num = int(num_str) * 1000
            elif 'm' in text or 'million' in text:
                num = int(num_str) * 1000000
            else:
                num = int(num_str)

            if num >= 1000000:
                return ScaleLevel.ENTERPRISE
            elif num >= 100000:
                return ScaleLevel.LARGE
            elif num >= 1000:
                return ScaleLevel.MEDIUM
            else:
                return ScaleLevel.SMALL

        # Check for scale keywords
        for scale, keywords in scale_patterns.items():
            for keyword in keywords:
                if keyword in text:
                    return scale

        return ScaleLevel.MEDIUM  # Default assumption

    def _assess_security_level(self, text: str) -> SecurityLevel:
        """Assess required security level"""
        security_patterns = {
            SecurityLevel.CRITICAL: [
                'hipaa', 'pci dss', 'sox', 'government', 'classified',
                'high security', 'critical security', 'zero trust'
            ],
            SecurityLevel.HIGH: [
                'gdpr', 'compliance', 'audit', 'financial data', 'personal data',
                'encrypted', 'secure', 'authentication', 'authorization'
            ],
            SecurityLevel.STANDARD: [
                'login', 'user accounts', 'password', 'https', 'ssl',
                'basic security', 'user management'
            ],
            SecurityLevel.BASIC: [
                'simple', 'basic', 'internal', 'prototype', 'demo'
            ]
        }

        for level, keywords in security_patterns.items():
            for keyword in keywords:
                if keyword in text:
                    return level

        return SecurityLevel.STANDARD  # Default assumption

    def _extract_performance_requirements(self, text: str) -> Dict[str, Any]:
        """Extract performance-related requirements"""
        performance = {
            'response_time': None,
            'throughput': None,
            'availability': None,
            'concurrent_users': None
        }

        # Response time patterns
        response_patterns = [
            r'(\d+)\s*(?:ms|milliseconds?)',
            r'(\d+)\s*(?:s|seconds?)\s*response',
            r'under\s*(\d+)\s*(?:ms|seconds?)',
            r'less than\s*(\d+)\s*(?:ms|seconds?)'
        ]

        for pattern in response_patterns:
            match = re.search(pattern, text)
            if match:
                performance['response_time'] = f"{match.group(1)}ms"
                break

        # Availability patterns
        availability_patterns = [
            r'(\d+(?:\.\d+)?)\s*%\s*(?:uptime|availability)',
            r'(\d+)\s*nines',
            r'99\.(\d+)%'
        ]

        for pattern in availability_patterns:
            match = re.search(pattern, text)
            if match:
                if 'nines' in pattern:
                    nines = int(match.group(1))
                    performance['availability'] = f"99.{'9' * (nines-2)}%"
                else:
                    performance['availability'] = f"{match.group(1)}%"
                break

        # Concurrent users
        concurrent_patterns = [
            r'(\d+)\s*concurrent\s*users?',
            r'(\d+)\s*simultaneous\s*users?'
        ]

        for pattern in concurrent_patterns:
            match = re.search(pattern, text)
            if match:
                performance['concurrent_users'] = int(match.group(1))
                break

        return performance

    def _extract_functional_requirements(self, text: str) -> List[AnalyzedRequirement]:
        """Extract functional requirements from text"""
        functional_patterns = {
            'user_authentication': {
                'keywords': ['login', 'signup', 'authentication', 'user accounts', 'register'],
                'implications': ['Need identity provider', 'Session management', 'Password security']
            },
            'data_storage': {
                'keywords': ['database', 'store data', 'persist', 'save information'],
                'implications': ['Database design needed', 'Backup strategy', 'Data modeling']
            },
            'file_upload': {
                'keywords': ['upload files', 'file storage', 'images', 'documents'],
                'implications': ['Object storage needed', 'File validation', 'CDN for delivery']
            },
            'real_time': {
                'keywords': ['real-time', 'live updates', 'websockets', 'instant'],
                'implications': ['WebSocket support', 'Event streaming', 'Low latency']
            },
            'search': {
                'keywords': ['search', 'find', 'filter', 'query'],
                'implications': ['Search engine', 'Indexing strategy', 'Search UX']
            },
            'notifications': {
                'keywords': ['notifications', 'alerts', 'email', 'push notifications'],
                'implications': ['Notification service', 'Message queuing', 'User preferences']
            },
            'analytics': {
                'keywords': ['analytics', 'tracking', 'metrics', 'reporting'],
                'implications': ['Event tracking', 'Data warehouse', 'Visualization tools']
            },
            'payment': {
                'keywords': ['payment', 'billing', 'subscription', 'checkout'],
                'implications': ['Payment gateway', 'PCI compliance', 'Invoice management']
            }
        }

        requirements = []

        for req_type, config in functional_patterns.items():
            for keyword in config['keywords']:
                if keyword in text:
                    requirement = AnalyzedRequirement(
                        text=f"Application needs {req_type.replace('_', ' ')}",
                        type=RequirementType.FUNCTIONAL,
                        confidence=0.8,
                        keywords=[keyword],
                        implications=config['implications']
                    )
                    requirements.append(requirement)
                    break  # Don't duplicate requirements

        return requirements

    def _extract_technical_constraints(self, text: str) -> Dict[str, Any]:
        """Extract technical constraints and preferences"""
        constraints = {
            'preferred_cloud': None,
            'budget_conscious': False,
            'existing_stack': [],
            'compliance_requirements': [],
            'geographic_requirements': []
        }

        # Cloud provider preferences
        cloud_patterns = {
            'aws': ['aws', 'amazon web services'],
            'azure': ['azure', 'microsoft azure'],
            'gcp': ['gcp', 'google cloud', 'google cloud platform'],
            'multi_cloud': ['multi-cloud', 'multiple clouds', 'cloud agnostic']
        }

        for cloud, keywords in cloud_patterns.items():
            for keyword in keywords:
                if keyword in text:
                    constraints['preferred_cloud'] = cloud
                    break

        # Budget sensitivity
        budget_keywords = ['cheap', 'cost-effective', 'budget', 'low cost', 'minimal cost']
        constraints['budget_conscious'] = any(keyword in text for keyword in budget_keywords)

        # Existing technology stack
        tech_keywords = ['kubernetes', 'docker', 'node.js', 'python', 'java', 'react', 'angular']
        constraints['existing_stack'] = [tech for tech in tech_keywords if tech in text]

        # Compliance requirements
        compliance_keywords = ['gdpr', 'hipaa', 'pci dss', 'sox', 'iso 27001']
        constraints['compliance_requirements'] = [comp for comp in compliance_keywords if comp in text]

        # Geographic requirements
        geo_keywords = ['europe', 'eu', 'asia', 'us', 'global', 'multi-region']
        constraints['geographic_requirements'] = [geo for geo in geo_keywords if geo in text]

        return constraints

    def _extract_business_constraints(self, text: str) -> Dict[str, Any]:
        """Extract business-related constraints"""
        constraints = {
            'time_to_market': None,
            'team_size': None,
            'experience_level': None,
            'maintenance_preference': None
        }

        # Time to market
        time_patterns = [
            r'(\d+)\s*(?:weeks?|months?)\s*(?:to launch|deadline)',
            r'quickly?|fast|rapid|asap',
            r'mvp|minimum viable product'
        ]

        for pattern in time_patterns:
            if re.search(pattern, text):
                if 'quick' in pattern or 'fast' in pattern:
                    constraints['time_to_market'] = 'urgent'
                elif 'mvp' in pattern:
                    constraints['time_to_market'] = 'mvp_focused'
                break

        # Team experience
        experience_patterns = {
            'beginner': ['new to cloud', 'learning', 'beginner', 'first time'],
            'intermediate': ['some experience', 'familiar with'],
            'expert': ['experienced', 'expert', 'advanced', 'senior team']
        }

        for level, keywords in experience_patterns.items():
            if any(keyword in text for keyword in keywords):
                constraints['experience_level'] = level
                break

        # Maintenance preference
        if any(word in text for word in ['managed', 'serverless', 'low maintenance']):
            constraints['maintenance_preference'] = 'low_maintenance'
        elif any(word in text for word in ['full control', 'custom', 'on-premises']):
            constraints['maintenance_preference'] = 'full_control'

        return constraints

    def _suggest_services(self, text: str, app_type: str) -> List[str]:
        """Suggest relevant cloud services based on requirements"""
        base_services = {
            'web_application': ['load_balancer', 'compute', 'database', 'cdn'],
            'api_service': ['api_gateway', 'compute', 'database'],
            'mobile_app': ['api_gateway', 'compute', 'database', 'push_notifications'],
            'e-commerce': ['load_balancer', 'compute', 'database', 'cdn', 'payment_gateway'],
            'data_analytics': ['data_warehouse', 'compute', 'visualization', 'storage'],
            'iot': ['message_queue', 'stream_processing', 'database', 'compute']
        }

        services = base_services.get(app_type, ['compute', 'database'])

        # Add services based on specific requirements
        if 'file' in text or 'upload' in text:
            services.append('object_storage')
        if 'search' in text:
            services.append('search_engine')
        if 'real-time' in text or 'websocket' in text:
            services.append('message_queue')
        if 'notification' in text or 'email' in text:
            services.append('notification_service')
        if 'analytics' in text or 'tracking' in text:
            services.append('analytics_service')

        return list(set(services))  # Remove duplicates

    def _assess_complexity(self, functional_reqs: List[AnalyzedRequirement],
                          technical_constraints: Dict[str, Any],
                          scale: ScaleLevel) -> str:
        """Assess overall architecture complexity"""
        complexity_score = 0

        # Base complexity from scale
        scale_scores = {
            ScaleLevel.SMALL: 1,
            ScaleLevel.MEDIUM: 2,
            ScaleLevel.LARGE: 3,
            ScaleLevel.ENTERPRISE: 4
        }
        complexity_score += scale_scores[scale]

        # Add complexity from functional requirements
        complexity_score += len(functional_reqs)

        # Add complexity from technical constraints
        if technical_constraints.get('compliance_requirements'):
            complexity_score += 2
        if technical_constraints.get('geographic_requirements'):
            complexity_score += 1

        if complexity_score <= 3:
            return 'simple'
        elif complexity_score <= 6:
            return 'moderate'
        elif complexity_score <= 9:
            return 'complex'
        else:
            return 'very_complex'

    def _estimate_timeline(self, complexity: str, scale: ScaleLevel) -> str:
        """Estimate development timeline"""
        base_times = {
            'simple': 2,      # weeks
            'moderate': 6,    # weeks
            'complex': 12,    # weeks
            'very_complex': 24 # weeks
        }

        scale_multipliers = {
            ScaleLevel.SMALL: 1.0,
            ScaleLevel.MEDIUM: 1.2,
            ScaleLevel.LARGE: 1.5,
            ScaleLevel.ENTERPRISE: 2.0
        }

        base_weeks = base_times[complexity]
        final_weeks = int(base_weeks * scale_multipliers[scale])

        if final_weeks <= 4:
            return f"{final_weeks} weeks"
        elif final_weeks <= 12:
            return f"{final_weeks // 4} months"
        else:
            return f"{final_weeks // 12} quarters"

    def _estimate_budget_range(self, scale: ScaleLevel, complexity: str) -> str:
        """Estimate budget range for infrastructure"""
        base_costs = {
            'simple': 100,     # USD per month
            'moderate': 500,
            'complex': 2000,
            'very_complex': 10000
        }

        scale_multipliers = {
            ScaleLevel.SMALL: 1.0,
            ScaleLevel.MEDIUM: 2.0,
            ScaleLevel.LARGE: 5.0,
            ScaleLevel.ENTERPRISE: 20.0
        }

        base_cost = base_costs[complexity]
        final_cost = int(base_cost * scale_multipliers[scale])

        if final_cost < 500:
            return f"${final_cost}-{final_cost*2}/month"
        elif final_cost < 5000:
            return f"${final_cost//1000}K-{(final_cost*2)//1000}K/month"
        else:
            return f"${final_cost//1000}K+/month"

    def _load_service_keywords(self) -> Dict[str, List[str]]:
        """Load service-related keywords for pattern matching"""
        # This would normally load from a data file
        return {
            'compute': ['server', 'instance', 'vm', 'container', 'lambda', 'function'],
            'database': ['database', 'db', 'storage', 'data', 'sql', 'nosql'],
            'networking': ['load balancer', 'cdn', 'dns', 'vpc', 'subnet'],
            'security': ['firewall', 'waf', 'ssl', 'encryption', 'authentication']
        }

    def _load_pattern_keywords(self) -> Dict[str, List[str]]:
        """Load pattern-related keywords"""
        return {
            'microservices': ['microservice', 'api', 'service-oriented'],
            'serverless': ['serverless', 'function', 'event-driven'],
            'three_tier': ['web application', 'traditional', 'layered'],
            'event_driven': ['event', 'queue', 'streaming', 'real-time']
        }

    def _load_scale_indicators(self) -> Dict[str, List[str]]:
        """Load scale-related indicators"""
        return {
            'traffic': ['users', 'requests', 'load', 'volume'],
            'data': ['terabytes', 'petabytes', 'big data'],
            'geographic': ['global', 'worldwide', 'international']
        }

    def _load_security_indicators(self) -> Dict[str, List[str]]:
        """Load security-related indicators"""
        return {
            'compliance': ['gdpr', 'hipaa', 'pci', 'sox'],
            'data_sensitivity': ['personal', 'financial', 'medical'],
            'access_control': ['authentication', 'authorization', 'rbac']
        }
