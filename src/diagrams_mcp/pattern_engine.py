# src/diagrams_mcp/core/pattern_matcher.py

import json
import math
import os
import sys
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging

# Add current directory to Python path for imports
sys.path.insert(0, os.path.dirname(__file__))

from pattern_analyze import RequirementAnalysis, RequirementAnalyzer, ScaleLevel, SecurityLevel
from pattern_cate import PatternCategory
from pattern_architect import ArchitecturePattern

logger = logging.getLogger(__name__)

@dataclass
class PatternMatch:
    """Represents a pattern match with scoring details"""
    pattern: ArchitecturePattern
    match_score: float
    confidence: float
    match_reasons: List[str]
    concerns: List[str]
    fit_analysis: Dict[str, float]
    estimated_cost: str
    implementation_effort: str
    pros: List[str]
    cons: List[str]

@dataclass
class MatchingCriteria:
    """Criteria used for pattern matching"""
    functional_weight: float = 0.3
    technical_weight: float = 0.25
    scale_weight: float = 0.2
    security_weight: float = 0.15
    complexity_weight: float = 0.1

class PatternMatcher:
    """
    Matches user requirements against available architecture patterns
    using intelligent scoring algorithms.
    """

    def __init__(self, patterns_data_path: str = "data/patterns/pattern_catalog.json"):
        self.patterns = self._load_patterns(patterns_data_path)
        self.matching_criteria = MatchingCriteria()
        self.cost_calculator = CostCalculator()

    def match_patterns(
        self,
        analyzed_needs: RequirementAnalyzer,
        constraints: Optional[Dict[str, Any]] = None
    ) -> List[PatternMatch]:
        """
        Main pattern matching function that finds suitable architecture patterns
        based on analyzed requirements and constraints.

        Args:
            analyzed_needs: Structured analysis of user requirements
            constraints: Additional constraints (budget, timeline, etc.)

        Returns:
            List of PatternMatch objects ranked by suitability score
        """
        logger.info(f"Matching patterns for {analyzed_needs.application_type} application")

        # Normalize constraints
        if constraints is None:
            constraints = {}

        # Filter patterns by basic compatibility
        compatible_patterns = self._filter_compatible_patterns(analyzed_needs, constraints)

        # Score each compatible pattern
        pattern_matches = []
        for pattern in compatible_patterns:
            match = self._score_pattern_match(pattern, analyzed_needs, constraints)
            if match.match_score > 0.3:  # Minimum threshold
                pattern_matches.append(match)

        # Sort by match score (highest first)
        pattern_matches.sort(key=lambda x: x.match_score, reverse=True)

        # Apply post-processing adjustments
        pattern_matches = self._apply_post_processing(pattern_matches, analyzed_needs, constraints)

        logger.info(f"Found {len(pattern_matches)} suitable patterns")
        return pattern_matches[:5]  # Return top 5 matches

    def _load_patterns(self, patterns_path: str) -> List[ArchitecturePattern]:
        """Load architecture patterns from configuration"""
        try:
            with open(patterns_path, 'r') as f:
                patterns_data = json.load(f)

            patterns = []
            for pattern_data in patterns_data.get('patterns', []):
                pattern = ArchitecturePattern.from_dict(pattern_data)
                patterns.append(pattern)

            logger.info(f"Loaded {len(patterns)} architecture patterns")
            return patterns

        except FileNotFoundError:
            logger.warning(f"Pattern file not found: {patterns_path}, using default patterns")
            return self._get_default_patterns()

    def _filter_compatible_patterns(
        self,
        analyzed_needs: RequirementAnalysis,
        constraints: Dict[str, Any]
    ) -> List[ArchitecturePattern]:
        """Filter patterns based on basic compatibility requirements"""
        compatible = []

        for pattern in self.patterns:
            # Check scale compatibility
            if not self._is_scale_compatible(pattern, analyzed_needs.scale_level):
                continue

            # Check security compatibility
            if not self._is_security_compatible(pattern, analyzed_needs.security_level):
                continue

            # Check constraint compatibility
            if not self._meets_constraints(pattern, constraints):
                continue

            # Check application type compatibility
            if not self._is_app_type_compatible(pattern, analyzed_needs.application_type):
                continue

            compatible.append(pattern)

        logger.debug(f"Filtered to {len(compatible)} compatible patterns")
        return compatible

    def _score_pattern_match(
        self,
        pattern: ArchitecturePattern,
        analyzed_needs: RequirementAnalysis,
        constraints: Dict[str, Any]
    ) -> PatternMatch:
        """Score how well a pattern matches the analyzed requirements"""

        # Calculate individual scoring components
        functional_score = self._score_functional_fit(pattern, analyzed_needs)
        technical_score = self._score_technical_fit(pattern, analyzed_needs, constraints)
        scale_score = self._score_scale_fit(pattern, analyzed_needs.scale_level)
        security_score = self._score_security_fit(pattern, analyzed_needs.security_level)
        complexity_score = self._score_complexity_fit(pattern, analyzed_needs, constraints)

        # Calculate weighted overall score
        criteria = self.matching_criteria
        overall_score = (
            functional_score * criteria.functional_weight +
            technical_score * criteria.technical_weight +
            scale_score * criteria.scale_weight +
            security_score * criteria.security_weight +
            complexity_score * criteria.complexity_weight
        )

        # Calculate confidence based on data quality and pattern maturity
        confidence = self._calculate_confidence(pattern, analyzed_needs)

        # Generate explanations
        match_reasons = self._generate_match_reasons(
            pattern, analyzed_needs,
            functional_score, technical_score, scale_score, security_score
        )
        concerns = self._identify_concerns(pattern, analyzed_needs, constraints)
        pros_cons = self._analyze_pros_cons(pattern, analyzed_needs)

        # Estimate costs and effort
        estimated_cost = self.cost_calculator.estimate_pattern_cost(pattern, analyzed_needs)
        implementation_effort = self._estimate_implementation_effort(pattern, analyzed_needs)

        return PatternMatch(
            pattern=pattern,
            match_score=overall_score,
            confidence=confidence,
            match_reasons=match_reasons,
            concerns=concerns,
            fit_analysis={
                'functional': functional_score,
                'technical': technical_score,
                'scale': scale_score,
                'security': security_score,
                'complexity': complexity_score
            },
            estimated_cost=estimated_cost,
            implementation_effort=implementation_effort,
            pros=pros_cons['pros'],
            cons=pros_cons['cons']
        )

    def _score_functional_fit(
        self,
        pattern: ArchitecturePattern,
        analyzed_needs: RequirementAnalysis
    ) -> float:
        """Score how well pattern supports functional requirements"""
        if not analyzed_needs.functional_requirements:
            return 0.5  # Neutral score if no functional requirements

        total_score = 0.0
        total_weight = 0.0

        # Map functional requirements to pattern capabilities
        requirement_mappings = {
            'user_authentication': ['authentication', 'identity_management', 'user_management'],
            'data_storage': ['database', 'storage', 'persistence'],
            'file_upload': ['object_storage', 'file_storage', 'cdn'],
            'real_time': ['websockets', 'streaming', 'event_driven', 'real_time'],
            'search': ['search_engine', 'indexing', 'elasticsearch'],
            'notifications': ['messaging', 'notifications', 'email', 'push'],
            'analytics': ['analytics', 'monitoring', 'tracking', 'metrics'],
            'payment': ['payment_gateway', 'billing', 'financial']
        }

        for functional_req in analyzed_needs.functional_requirements:
            req_name = functional_req.text.lower()
            req_weight = functional_req.confidence

            # Find matching pattern capabilities
            pattern_score = 0.0
            for req_key, pattern_capabilities in requirement_mappings.items():
                if req_key in req_name:
                    # Check if pattern supports these capabilities
                    for capability in pattern_capabilities:
                        if capability in pattern.capabilities:
                            pattern_score = max(pattern_score, pattern.capabilities[capability])
                    break

            total_score += pattern_score * req_weight
            total_weight += req_weight

        return total_score / total_weight if total_weight > 0 else 0.5

    def _score_technical_fit(
        self,
        pattern: ArchitecturePattern,
        analyzed_needs: RequirementAnalysis,
        constraints: Dict[str, Any]
    ) -> float:
        """Score technical compatibility"""
        score = 0.0
        factors = 0

        # Cloud provider preference
        preferred_cloud = analyzed_needs.technical_constraints.get('preferred_cloud')
        if preferred_cloud:
            if preferred_cloud in pattern.supported_providers:
                score += 1.0
            elif 'multi_cloud' in pattern.supported_providers:
                score += 0.8
            else:
                score += 0.3
            factors += 1

        # Existing technology stack compatibility
        existing_stack = analyzed_needs.technical_constraints.get('existing_stack', [])
        if existing_stack:
            compatible_techs = 0
            for tech in existing_stack:
                if tech in pattern.compatible_technologies:
                    compatible_techs += 1

            if existing_stack:
                score += compatible_techs / len(existing_stack)
                factors += 1

        # Performance requirements
        perf_reqs = analyzed_needs.performance_requirements
        if perf_reqs.get('response_time'):
            target_ms = self._parse_response_time(perf_reqs['response_time'])
            if target_ms:
                if target_ms <= pattern.performance_characteristics.get('typical_response_time_ms', 1000):
                    score += 1.0
                else:
                    score += 0.5
                factors += 1

        # Availability requirements
        if perf_reqs.get('availability'):
            target_availability = self._parse_availability(perf_reqs['availability'])
            pattern_availability = pattern.performance_characteristics.get('availability', 0.99)
            if target_availability <= pattern_availability:
                score += 1.0
            else:
                score += 0.6
            factors += 1

        return score / factors if factors > 0 else 0.8

    def _score_scale_fit(self, pattern: ArchitecturePattern, scale_level: ScaleLevel) -> float:
        """Score how well pattern handles the required scale"""
        scale_mappings = {
            ScaleLevel.SMALL: 'small',
            ScaleLevel.MEDIUM: 'medium',
            ScaleLevel.LARGE: 'large',
            ScaleLevel.ENTERPRISE: 'enterprise'
        }

        target_scale = scale_mappings[scale_level]
        supported_scales = pattern.scale_characteristics.get('supported_scales', [])

        if target_scale in supported_scales:
            return 1.0
        elif 'auto_scaling' in pattern.capabilities:
            # Patterns with auto-scaling can handle variable scales
            return 0.9
        else:
            # Calculate partial fit based on scale similarity
            scale_order = ['small', 'medium', 'large', 'enterprise']
            if supported_scales:
                closest_scale = min(supported_scales,
                                  key=lambda x: abs(scale_order.index(x) - scale_order.index(target_scale)))
                distance = abs(scale_order.index(closest_scale) - scale_order.index(target_scale))
                return max(0.3, 1.0 - (distance * 0.2))
            else:
                return 0.5  # Unknown scale support

    def _score_security_fit(self, pattern: ArchitecturePattern, security_level: SecurityLevel) -> float:
        """Score security compatibility"""
        security_mappings = {
            SecurityLevel.BASIC: 1,
            SecurityLevel.STANDARD: 2,
            SecurityLevel.HIGH: 3,
            SecurityLevel.CRITICAL: 4
        }

        required_level = security_mappings[security_level]
        pattern_level = pattern.security_characteristics.get('security_level', 2)

        if pattern_level >= required_level:
            return 1.0
        else:
            # Penalty for insufficient security
            return max(0.2, 1.0 - (required_level - pattern_level) * 0.3)

    def _score_complexity_fit(
        self,
        pattern: ArchitecturePattern,
        analyzed_needs: RequirementAnalysis,
        constraints: Dict[str, Any]
    ) -> float:
        """Score complexity appropriateness"""
        # Map complexity levels to scores
        complexity_mappings = {
            'simple': 1,
            'moderate': 2,
            'complex': 3,
            'very_complex': 4
        }

        required_complexity = complexity_mappings.get(analyzed_needs.architecture_complexity, 2)
        pattern_complexity = complexity_mappings.get(pattern.complexity.value, 2)

        # Consider team experience
        team_experience = analyzed_needs.business_constraints.get('experience_level', 'intermediate')
        experience_mappings = {'beginner': 0.8, 'intermediate': 1.0, 'expert': 1.2}
        experience_factor = experience_mappings[team_experience]

        # Calculate fit
        if pattern_complexity <= required_complexity * experience_factor:
            return 1.0
        else:
            # Penalty for overly complex patterns
            return max(0.3, 1.0 - (pattern_complexity - required_complexity) * 0.2)

    def _calculate_confidence(
        self,
        pattern: ArchitecturePattern,
        analyzed_needs: RequirementAnalysis
    ) -> float:
        """Calculate confidence in the pattern match"""
        confidence = 0.8  # Base confidence

        # Adjust based on pattern maturity
        maturity_bonus = {
            'experimental': -0.2,
            'emerging': -0.1,
            'mature': 0.1,
            'industry_standard': 0.2
        }
        confidence += maturity_bonus.get(pattern.maturity, 0)

        # Adjust based on requirement clarity
        if len(analyzed_needs.functional_requirements) >= 3:
            confidence += 0.1

        # Adjust based on constraint specificity
        if analyzed_needs.technical_constraints.get('preferred_cloud'):
            confidence += 0.1

        return min(1.0, max(0.3, confidence))

    def _generate_match_reasons(
        self,
        pattern: ArchitecturePattern,
        analyzed_needs: RequirementAnalysis,
        functional_score: float,
        technical_score: float,
        scale_score: float,
        security_score: float
    ) -> List[str]:
        """Generate human-readable reasons for the pattern match"""
        reasons = []

        # Application type match
        if pattern.category.value in analyzed_needs.application_type:
            reasons.append(f"Perfect fit for {analyzed_needs.application_type} applications")

        # Functional requirements
        if functional_score >= 0.8:
            reasons.append("Supports all key functional requirements")
        elif functional_score >= 0.6:
            reasons.append("Supports most functional requirements")

        # Scale handling
        if scale_score >= 0.9:
            reasons.append(f"Excellent for {analyzed_needs.scale_level.value} scale applications")

        # Security
        if security_score >= 0.9:
            reasons.append(f"Meets {analyzed_needs.security_level.value} security requirements")

        # Technical fit
        preferred_cloud = analyzed_needs.technical_constraints.get('preferred_cloud')
        if preferred_cloud and preferred_cloud in pattern.supported_providers:
            reasons.append(f"Native support for {preferred_cloud.upper()}")

        # Performance
        perf_reqs = analyzed_needs.performance_requirements
        if perf_reqs.get('response_time') and technical_score >= 0.8:
            reasons.append("Meets response time requirements")

        # Complexity appropriateness
        team_exp = analyzed_needs.business_constraints.get('experience_level')
        if team_exp == 'beginner' and pattern.complexity.value in ['simple', 'moderate']:
            reasons.append("Appropriate complexity for team experience level")

        return reasons

    def _identify_concerns(
        self,
        pattern: ArchitecturePattern,
        analyzed_needs: RequirementAnalysis,
        constraints: Dict[str, Any]
    ) -> List[str]:
        """Identify potential concerns or limitations"""
        concerns = []

        # Complexity concerns
        team_exp = analyzed_needs.business_constraints.get('experience_level', 'intermediate')
        if team_exp == 'beginner' and pattern.complexity.value in ['complex', 'very_complex']:
            concerns.append("Pattern may be complex for beginner team")

        # Cost concerns
        if analyzed_needs.technical_constraints.get('budget_conscious') and pattern.cost_characteristics.get('cost_level') == 'high':
            concerns.append("Higher cost pattern for budget-conscious requirements")

        # Time to market concerns
        ttm = analyzed_needs.business_constraints.get('time_to_market')
        if ttm == 'urgent' and pattern.implementation_characteristics.get('setup_time') == 'long':
            concerns.append("Longer setup time may impact urgent timeline")

        # Scale limitations
        if analyzed_needs.scale_level == ScaleLevel.ENTERPRISE and 'enterprise' not in pattern.scale_characteristics.get('supported_scales', []):
            concerns.append("May need modifications for enterprise scale")

        # Vendor lock-in
        if len(pattern.supported_providers) == 1 and analyzed_needs.technical_constraints.get('preferred_cloud') != 'multi_cloud':
            concerns.append(f"Creates vendor lock-in with {pattern.supported_providers[0]}")

        return concerns

    def _analyze_pros_cons(
        self,
        pattern: ArchitecturePattern,
        analyzed_needs: RequirementAnalysis
    ) -> Dict[str, List[str]]:
        """Analyze pros and cons of the pattern for this specific use case"""
        pros = []
        cons = []

        # Pattern-specific pros
        if pattern.category == PatternCategory.SERVERLESS:
            pros.extend(["No server management", "Pay-per-use pricing", "Auto-scaling"])
            if analyzed_needs.scale_level in [ScaleLevel.SMALL, ScaleLevel.MEDIUM]:
                pros.append("Cost-effective for variable workloads")
            else:
                cons.append("Can be expensive at high scale")

        elif pattern.category == PatternCategory.MICROSERVICES:
            pros.extend(["Independent deployments", "Technology diversity", "Team scalability"])
            if analyzed_needs.scale_level in [ScaleLevel.LARGE, ScaleLevel.ENTERPRISE]:
                pros.append("Excellent for large teams and complex applications")
            else:
                cons.append("May be overkill for smaller applications")

        elif pattern.category == PatternCategory.MONOLITHIC:
            pros.extend(["Simple deployment", "Easy debugging", "Good performance"])
            if analyzed_needs.scale_level in [ScaleLevel.SMALL, ScaleLevel.MEDIUM]:
                pros.append("Perfect for smaller teams and applications")
            else:
                cons.append("Scaling challenges for large applications")

        # Security pros/cons
        if analyzed_needs.security_level in [SecurityLevel.HIGH, SecurityLevel.CRITICAL]:
            if 'encryption' in pattern.security_characteristics:
                pros.append("Built-in encryption and security")
            else:
                cons.append("May need additional security hardening")

        # Cost pros/cons
        if analyzed_needs.technical_constraints.get('budget_conscious'):
            cost_level = pattern.cost_characteristics.get('cost_level', 'medium')
            if cost_level == 'low':
                pros.append("Cost-effective solution")
            elif cost_level == 'high':
                cons.append("Higher operational costs")

        return {'pros': pros, 'cons': cons}

    def _apply_post_processing(
        self,
        pattern_matches: List[PatternMatch],
        analyzed_needs: RequirementAnalysis,
        constraints: Dict[str, Any]
    ) -> List[PatternMatch]:
        """Apply post-processing adjustments to pattern matches"""

        # Boost patterns that match specific business constraints
        for match in pattern_matches:
            # Boost for urgent timeline
            if analyzed_needs.business_constraints.get('time_to_market') == 'urgent':
                if match.pattern.implementation_characteristics.get('setup_time') == 'fast':
                    match.match_score *= 1.1

            # Boost for budget constraints
            if analyzed_needs.technical_constraints.get('budget_conscious'):
                if match.pattern.cost_characteristics.get('cost_level') == 'low':
                    match.match_score *= 1.1

            # Boost for team experience
            team_exp = analyzed_needs.business_constraints.get('experience_level')
            if team_exp == 'beginner' and match.pattern.complexity.value in ['simple', 'moderate']:
                match.match_score *= 1.05

        # Re-sort after adjustments
        pattern_matches.sort(key=lambda x: x.match_score, reverse=True)

        return pattern_matches

    # Helper methods
    def _is_scale_compatible(self, pattern: ArchitecturePattern, scale_level: ScaleLevel) -> bool:
        """Check if pattern can handle the required scale"""
        scale_mappings = {
            ScaleLevel.SMALL: 'small',
            ScaleLevel.MEDIUM: 'medium',
            ScaleLevel.LARGE: 'large',
            ScaleLevel.ENTERPRISE: 'enterprise'
        }

        target_scale = scale_mappings[scale_level]
        supported_scales = pattern.scale_characteristics.get('supported_scales', [])

        return target_scale in supported_scales or 'auto_scaling' in pattern.capabilities

    def _is_security_compatible(self, pattern: ArchitecturePattern, security_level: SecurityLevel) -> bool:
        """Check if pattern meets minimum security requirements"""
        security_mappings = {
            SecurityLevel.BASIC: 1,
            SecurityLevel.STANDARD: 2,
            SecurityLevel.HIGH: 3,
            SecurityLevel.CRITICAL: 4
        }

        required_level = security_mappings[security_level]
        pattern_level = pattern.security_characteristics.get('security_level', 2)

        return pattern_level >= required_level

    def _meets_constraints(self, pattern: ArchitecturePattern, constraints: Dict[str, Any]) -> bool:
        """Check if pattern meets additional constraints"""
        # Budget constraints
        max_cost = constraints.get('max_monthly_cost')
        if max_cost:
            pattern_cost = self.cost_calculator.estimate_base_cost(pattern)
            if pattern_cost > max_cost:
                return False

        # Timeline constraints
        max_timeline = constraints.get('max_timeline_weeks')
        if max_timeline:
            pattern_timeline = pattern.implementation_characteristics.get('typical_timeline_weeks', 8)
            if pattern_timeline > max_timeline:
                return False

        return True

    def _is_app_type_compatible(self, pattern: ArchitecturePattern, app_type: str) -> bool:
        """Check if pattern is suitable for the application type"""
        # Get pattern's suitable application types
        suitable_apps = pattern.metadata.get('suitable_for', [])

        if not suitable_apps:
            return True  # No restrictions

        # Check direct match
        if app_type in suitable_apps:
            return True

        # Check category matches
        app_categories = {
            'web_application': ['web', 'application'],
            'api_service': ['api', 'service', 'backend'],
            'mobile_app': ['mobile', 'api', 'backend'],
            'e_commerce': ['web', 'application', 'e_commerce'],
            'data_analytics': ['data', 'analytics', 'processing']
        }

        user_categories = app_categories.get(app_type, [])
        return any(category in suitable_apps for category in user_categories)

    def _parse_response_time(self, response_time_str: str) -> Optional[int]:
        """Parse response time string to milliseconds"""
        import re
        match = re.search(r'(\d+)\s*(ms|s|seconds?)', response_time_str.lower())
        if match:
            value = int(match.group(1))
            unit = match.group(2)
            if unit.startswith('s'):
                return value * 1000
            else:
                return value
        return None

    def _parse_availability(self, availability_str: str) -> Optional[float]:
        """Parse availability string to decimal"""
        import re
        match = re.search(r'(\d+(?:\.\d+)?)', availability_str)
        if match:
            value = float(match.group(1))
            if value > 1:  # Percentage
                return value / 100
            else:  # Already decimal
                return value
        return None

    def _estimate_implementation_effort(
        self,
        pattern: ArchitecturePattern,
        analyzed_needs: RequirementAnalysis
    ) -> str:
        """Estimate implementation effort"""
        base_effort = pattern.implementation_characteristics.get('base_effort_weeks', 4)

        # Adjust for complexity
        complexity_multipliers = {
            'simple': 0.8,
            'moderate': 1.0,
            'complex': 1.5,
            'very_complex': 2.0
        }

        complexity = analyzed_needs.architecture_complexity
        effort_weeks = base_effort * complexity_multipliers.get(complexity, 1.0)

        # Adjust for team experience
        team_exp = analyzed_needs.business_constraints.get('experience_level', 'intermediate')
        exp_multipliers = {'beginner': 1.5, 'intermediate': 1.0, 'expert': 0.8}
        effort_weeks *= exp_multipliers[team_exp]

        effort_weeks = int(effort_weeks)

        if effort_weeks <= 2:
            return "1-2 weeks"
        elif effort_weeks <= 4:
            return "2-4 weeks"
        elif effort_weeks <= 8:
            return "1-2 months"
        elif effort_weeks <= 16:
            return "2-4 months"
        else:
            return "4+ months"

    def _get_default_patterns(self) -> List[ArchitecturePattern]:
        """Return default patterns if configuration file is not available"""
        # This would return a basic set of hardcoded patterns
        return []


class CostCalculator:
    """Helper class for cost estimation"""

    def estimate_pattern_cost(
        self,
        pattern: ArchitecturePattern,
        analyzed_needs: RequirementAnalysis
    ) -> str:
        """Estimate monthly cost for pattern with given requirements"""
        base_cost = self.estimate_base_cost(pattern)

        # Scale adjustment
        scale_multipliers = {
            ScaleLevel.SMALL: 1.0,
            ScaleLevel.MEDIUM: 3.0,
            ScaleLevel.LARGE: 10.0,
            ScaleLevel.ENTERPRISE: 50.0
        }

        scaled_cost = base_cost * scale_multipliers[analyzed_needs.scale_level]

        if scaled_cost < 100:
            return f"${int(scaled_cost)}/month"
        elif scaled_cost < 1000:
            return f"${int(scaled_cost)}/month"
        else:
            return f"${scaled_cost/1000:.1f}K/month"

    def estimate_base_cost(self, pattern: ArchitecturePattern) -> float:
        """Estimate base monthly cost for pattern"""
        cost_levels = {
            'very_low': 50,
            'low': 200,
            'medium': 500,
            'high': 2000,
            'very_high': 10000
        }

        cost_level = pattern.cost_characteristics.get('cost_level', 'medium')
        return cost_levels.get(cost_level, 500)
