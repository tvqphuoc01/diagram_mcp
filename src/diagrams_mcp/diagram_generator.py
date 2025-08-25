# src/diagrams_mcp/core/diagram_generator.py

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Union, Tuple
from enum import Enum
import json
import re
import logging

def sanitize_mermaid_label(label: str, is_pipe_wrapped: bool = False) -> str:
    """
    Sanitize labels for Mermaid diagrams to prevent syntax issues.

    Args:
        label: The label text to sanitize
        is_pipe_wrapped: Whether the label will be wrapped in pipes |label|

    Returns:
        Sanitized label safe for Mermaid syntax
    """
    if not label:
        return ""

    # Replace problematic characters
    sanitized = label

    # Replace double quotes with single quotes
    sanitized = sanitized.replace('"', "'")

    # If pipe-wrapped, escape or remove pipe characters to prevent syntax breaking
    if is_pipe_wrapped:
        sanitized = sanitized.replace('|', '/')

    # Replace other potentially problematic characters
    sanitized = sanitized.replace('\n', ' ').replace('\r', ' ')

    # Trim excessive whitespace
    sanitized = ' '.join(sanitized.split())

    return sanitized

logger = logging.getLogger(__name__)

class DiagramType(Enum):
    """Supported diagram types"""
    ARCHITECTURE = "architecture"          # Infrastructure diagrams (existing)
    SEQUENCE = "sequence"                  # Sequence diagrams for workflows
    FLOWCHART = "flowchart"               # Process flow diagrams
    CLASS = "class"                       # Class/entity relationship diagrams
    NETWORK = "network"                   # Network topology diagrams
    DEPLOYMENT = "deployment"             # Deployment diagrams
    COMPONENT = "component"               # Component interaction diagrams
    STATE_MACHINE = "state_machine"       # State transition diagrams
    GANTT = "gantt"                       # Project timeline diagrams
    MINDMAP = "mindmap"                   # Concept mapping diagrams

class DiagramFormat(Enum):
    """Output formats for diagrams"""
    PYTHON_DIAGRAMS = "python_diagrams"   # Python diagrams library (existing)
    MERMAID = "mermaid"                   # Mermaid.js syntax
    PLANTUML = "plantuml"                 # PlantUML syntax
    GRAPHVIZ = "graphviz"                 # DOT notation
    D2 = "d2"                             # D2 syntax
    SVG = "svg"                           # Direct SVG generation
    ASCII = "ascii"                       # ASCII art diagrams

@dataclass
class DiagramElement:
    """Base element for all diagram types"""
    id: str
    label: str
    element_type: str
    properties: Dict[str, Any] = field(default_factory=dict)
    style: Dict[str, str] = field(default_factory=dict)

@dataclass
class DiagramConnection:
    """Connection between diagram elements"""
    from_element: str
    to_element: str
    label: Optional[str] = None
    connection_type: str = "arrow"
    properties: Dict[str, Any] = field(default_factory=dict)

@dataclass
class DiagramSpec:
    """Complete diagram specification"""
    diagram_type: DiagramType
    title: str
    description: str
    elements: List[DiagramElement] = field(default_factory=list)
    connections: List[DiagramConnection] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    style_config: Dict[str, Any] = field(default_factory=dict)

# ===== ABSTRACT BASE GENERATOR =====

class DiagramGenerator(ABC):
    """Abstract base class for diagram generators"""

    @abstractmethod
    def generate(self, spec: DiagramSpec, output_format: DiagramFormat) -> str:
        """Generate diagram code in the specified format"""
        pass

    @abstractmethod
    def parse_natural_language(self, description: str) -> DiagramSpec:
        """Parse natural language description into diagram specification"""
        pass

    @abstractmethod
    def get_supported_formats(self) -> List[DiagramFormat]:
        """Get list of supported output formats"""
        pass

# ===== SEQUENCE DIAGRAM GENERATOR =====

@dataclass
class SequenceActor:
    """Actor in sequence diagram"""
    id: str
    name: str
    actor_type: str = "person"  # person, system, service, database
    stereotype: Optional[str] = None

@dataclass
class SequenceMessage:
    """Message between actors"""
    from_actor: str
    to_actor: str
    message: str
    message_type: str = "sync"  # sync, async, return, create, destroy
    activation: bool = False
    order: int = 1

class SequenceDiagramGenerator(DiagramGenerator):
    """Generator for sequence diagrams showing interaction flows"""

    def __init__(self):
        self.actors = []
        self.messages = []

    def parse_natural_language(self, description: str) -> DiagramSpec:
        """Parse natural language into sequence diagram spec"""

        # Extract actors from text
        actors = self._extract_actors(description)

        # Extract interactions/messages
        messages = self._extract_messages(description, actors)

        # Create diagram elements
        elements = []
        for actor in actors:
            elements.append(DiagramElement(
                id=actor.id,
                label=actor.name,
                element_type="actor",
                properties={
                    "actor_type": actor.actor_type,
                    "stereotype": actor.stereotype
                }
            ))

        # Create connections from messages
        connections = []
        for msg in messages:
            connections.append(DiagramConnection(
                from_element=msg.from_actor,
                to_element=msg.to_actor,
                label=msg.message,
                connection_type=msg.message_type,
                properties={"order": msg.order, "activation": msg.activation}
            ))

        return DiagramSpec(
            diagram_type=DiagramType.SEQUENCE,
            title=self._extract_title(description),
            description=description,
            elements=elements,
            connections=connections,
            metadata={"total_actors": len(actors), "total_messages": len(messages)}
        )

    def _extract_actors(self, description: str) -> List[SequenceActor]:
        """Extract actors from natural language description"""
        actors = []
        actor_patterns = [
            r'(?:user|customer|client|person|admin)\s+(\w+)',
            r'(?:system|service|api|server|database|app)\s+(\w+)',
            r'(\w+)\s+(?:system|service|api|server|database)',
            r'(?:the\s+)?(\w+)\s+(?:sends|receives|calls|requests)',
            r'(?:when\s+)?(\w+)\s+(?:wants to|tries to|needs to)'
        ]

        found_actors = set()

        for pattern in actor_patterns:
            matches = re.finditer(pattern, description, re.IGNORECASE)
            for match in matches:
                actor_name = match.group(1).lower()
                if len(actor_name) > 2 and actor_name not in found_actors:
                    actor_type = self._determine_actor_type(actor_name, description)
                    actors.append(SequenceActor(
                        id=f"actor_{actor_name}",
                        name=actor_name.title(),
                        actor_type=actor_type
                    ))
                    found_actors.add(actor_name)

        # Ensure we have at least user and system
        if not any(a.actor_type == "person" for a in actors):
            actors.insert(0, SequenceActor("actor_user", "User", "person"))

        if not any(a.actor_type == "system" for a in actors):
            actors.append(SequenceActor("actor_system", "System", "system"))

        return actors[:8]  # Limit to 8 actors for readability

    def _determine_actor_type(self, actor_name: str, description: str) -> str:
        """Determine the type of actor based on context"""
        person_keywords = ["user", "customer", "client", "person", "admin", "operator"]
        system_keywords = ["system", "service", "api", "server", "app", "application"]
        database_keywords = ["database", "db", "storage", "repository"]

        actor_lower = actor_name.lower()

        if any(keyword in actor_lower for keyword in person_keywords):
            return "person"
        elif any(keyword in actor_lower for keyword in database_keywords):
            return "database"
        elif any(keyword in actor_lower for keyword in system_keywords):
            return "system"
        else:
            # Analyze context around the actor name
            context_window = 20
            actor_pos = description.lower().find(actor_lower)
            if actor_pos != -1:
                start = max(0, actor_pos - context_window)
                end = min(len(description), actor_pos + len(actor_lower) + context_window)
                context = description[start:end].lower()

                if any(keyword in context for keyword in person_keywords):
                    return "person"
                elif any(keyword in context for keyword in database_keywords):
                    return "database"
                elif any(keyword in context for keyword in system_keywords):
                    return "system"

            return "system"  # Default

    def _extract_messages(self, description: str, actors: List[SequenceActor]) -> List[SequenceMessage]:
        """Extract message interactions from description"""
        messages = []
        actor_names = {actor.name.lower(): actor.id for actor in actors}

        # Patterns for different types of interactions
        message_patterns = [
            (r'(\w+)\s+(?:sends|calls|requests|asks)\s+(\w+)\s+(?:to|for)\s+(.+?)(?:\.|$)', "sync"),
            (r'(\w+)\s+(?:receives|gets|obtains)\s+(.+?)\s+from\s+(\w+)', "return"),
            (r'(\w+)\s+(?:notifies|alerts|informs)\s+(\w+)\s+(?:about|that)\s+(.+?)(?:\.|$)', "async"),
            (r'(\w+)\s+(?:creates|generates|produces)\s+(.+?)\s+(?:in|for)\s+(\w+)', "create"),
            (r'(\w+)\s+(?:authenticates|logs in|signs in)(?:\s+to\s+(\w+))?', "sync"),
            (r'(\w+)\s+(?:validates|verifies|checks)\s+(.+?)(?:\.|$)', "sync"),
            (r'(\w+)\s+(?:stores|saves|persists)\s+(.+?)\s+(?:in|to)\s+(\w+)', "sync"),
            (r'(\w+)\s+(?:queries|searches|looks up)\s+(.+?)\s+(?:in|from)\s+(\w+)', "sync")
        ]

        order = 1
        for pattern, msg_type in message_patterns:
            matches = re.finditer(pattern, description, re.IGNORECASE)
            for match in matches:
                groups = match.groups()

                # Handle different pattern structures
                if len(groups) >= 3 and msg_type == "return":
                    # Pattern: A receives X from B
                    from_actor = self._find_actor_id(groups[2], actor_names)
                    to_actor = self._find_actor_id(groups[0], actor_names)
                    message = f"Return {groups[1]}"
                elif len(groups) >= 3:
                    # Pattern: A sends/calls B for X
                    from_actor = self._find_actor_id(groups[0], actor_names)
                    to_actor = self._find_actor_id(groups[1], actor_names)
                    message = groups[2].strip()
                elif len(groups) >= 2:
                    # Pattern: A authenticates (to B)
                    from_actor = self._find_actor_id(groups[0], actor_names)
                    to_actor = self._find_actor_id(groups[1] if groups[1] else "system", actor_names)
                    message = "Authenticate"
                else:
                    continue

                if from_actor and to_actor and from_actor != to_actor:
                    messages.append(SequenceMessage(
                        from_actor=from_actor,
                        to_actor=to_actor,
                        message=message.capitalize(),
                        message_type=msg_type,
                        order=order
                    ))
                    order += 1

        return messages[:15]  # Limit messages for readability

    def _find_actor_id(self, name: str, actor_names: Dict[str, str]) -> Optional[str]:
        """Find actor ID from name, with fuzzy matching"""
        if not name:
            return None

        name_lower = name.lower().strip()

        # Exact match
        if name_lower in actor_names:
            return actor_names[name_lower]

        # Partial match
        for actor_name, actor_id in actor_names.items():
            if name_lower in actor_name or actor_name in name_lower:
                return actor_id

        return None

    def _extract_title(self, description: str) -> str:
        """Extract or generate title from description"""
        # Look for explicit titles
        title_patterns = [
            r'(?:title|sequence|process):\s*(.+?)(?:\n|$)',
            r'^(.+?)\s+(?:sequence|process|workflow|flow)',
            r'(?:the\s+)?(.+?)\s+process'
        ]

        for pattern in title_patterns:
            match = re.search(pattern, description, re.IGNORECASE)
            if match:
                return match.group(1).strip().title()

        # Generate from first sentence
        first_sentence = description.split('.')[0]
        if len(first_sentence) < 50:
            return first_sentence.strip().title()

        return "Sequence Diagram"

    def generate(self, spec: DiagramSpec, output_format: DiagramFormat) -> str:
        """Generate sequence diagram in specified format"""

        if output_format == DiagramFormat.MERMAID:
            return self._generate_mermaid(spec)
        elif output_format == DiagramFormat.PLANTUML:
            return self._generate_plantuml(spec)
        elif output_format == DiagramFormat.PYTHON_DIAGRAMS:
            return self._generate_python_diagrams(spec)
        else:
            raise ValueError(f"Unsupported format: {output_format}")

    def _generate_mermaid(self, spec: DiagramSpec) -> str:
        """Generate Mermaid sequence diagram"""
        lines = [
            "sequenceDiagram",
            f"    title {spec.title}",
            ""
        ]

        # Define participants
        for element in spec.elements:
            if element.element_type == "actor":
                participant_type = "participant"
                if element.properties.get("actor_type") == "person":
                    participant_type = "actor"

                lines.append(f"    {participant_type} {element.id} as {element.label}")

        lines.append("")

        # Add messages in order
        sorted_connections = sorted(spec.connections, key=lambda x: x.properties.get("order", 0))

        for conn in sorted_connections:
            arrow = "->>+" if conn.properties.get("activation") else "->>"
            if conn.connection_type == "async":
                arrow = "-))"
            elif conn.connection_type == "return":
                arrow = "-->"

            # Use sanitized labels for Mermaid sequence diagrams
            label = sanitize_mermaid_label(conn.label) if conn.label else ""
            lines.append(f"    {conn.from_element}{arrow}{conn.to_element}: {label}")

        return "\n".join(lines)

    def _generate_plantuml(self, spec: DiagramSpec) -> str:
        """Generate PlantUML sequence diagram"""
        lines = [
            "@startuml",
            f"title {spec.title}",
            ""
        ]

        # Define actors/participants
        for element in spec.elements:
            if element.element_type == "actor":
                if element.properties.get("actor_type") == "person":
                    lines.append(f"actor {element.label} as {element.id}")
                elif element.properties.get("actor_type") == "database":
                    lines.append(f"database {element.label} as {element.id}")
                else:
                    lines.append(f"participant {element.label} as {element.id}")

        lines.append("")

        # Add interactions
        sorted_connections = sorted(spec.connections, key=lambda x: x.properties.get("order", 0))

        for conn in sorted_connections:
            arrow = "->"
            if conn.connection_type == "async":
                arrow = "->>"
            elif conn.connection_type == "return":
                arrow = "-->"
            elif conn.connection_type == "create":
                arrow = "->*"

            activation = ""
            if conn.properties.get("activation"):
                activation = "\nactivate " + conn.to_element

            lines.append(f"{conn.from_element} {arrow} {conn.to_element}: {conn.label}{activation}")

        lines.extend(["", "@enduml"])
        return "\n".join(lines)

    def _generate_python_diagrams(self, spec: DiagramSpec) -> str:
        """Generate Python diagrams code for sequence-like diagram"""
        # Note: Python diagrams doesn't natively support sequence diagrams
        # This creates a flow-like representation
        lines = [
            "from diagrams import Diagram, Edge",
            "from diagrams.generic.blank import Blank",
            "from diagrams.programming.flowchart import StartEnd, Decision",
            "",
            f'with Diagram("{spec.title}", show=False, direction="TB"):',
        ]

        # Create nodes for actors
        actor_vars = {}
        for element in spec.elements:
            if element.element_type == "actor":
                var_name = element.id.replace("actor_", "")
                lines.append(f'    {var_name} = Blank("{element.label}")')
                actor_vars[element.id] = var_name

        lines.append("")

        # Create message flows
        sorted_connections = sorted(spec.connections, key=lambda x: x.properties.get("order", 0))

        for conn in sorted_connections:
            from_var = actor_vars.get(conn.from_element)
            to_var = actor_vars.get(conn.to_element)

            if from_var and to_var:
                edge_style = 'Edge(label="' + conn.label + '")'
                lines.append(f'    {from_var} >> {edge_style} >> {to_var}')

        return "\n".join(lines)

    def get_supported_formats(self) -> List[DiagramFormat]:
        """Get supported output formats for sequence diagrams"""
        return [
            DiagramFormat.MERMAID,
            DiagramFormat.PLANTUML,
            DiagramFormat.PYTHON_DIAGRAMS
        ]

# ===== FLOWCHART GENERATOR =====

@dataclass
class FlowNode:
    """Node in flowchart"""
    id: str
    label: str
    node_type: str  # start, end, process, decision, data, connector
    properties: Dict[str, Any] = field(default_factory=dict)

class FlowchartGenerator(DiagramGenerator):
    """Generator for process flowcharts"""

    def parse_natural_language(self, description: str) -> DiagramSpec:
        """Parse natural language into flowchart spec"""

        # Extract process steps
        steps = self._extract_process_steps(description)

        # Extract decisions/conditions
        decisions = self._extract_decisions(description)

        # Create flowchart elements
        elements = []
        connections = []

        # Start node
        start_id = "start"
        elements.append(DiagramElement(
            id=start_id,
            label="Start",
            element_type="start"
        ))

        # Process steps
        prev_id = start_id
        for i, step in enumerate(steps):
            step_id = f"step_{i+1}"
            elements.append(DiagramElement(
                id=step_id,
                label=step,
                element_type="process"
            ))

            # Connect to previous
            connections.append(DiagramConnection(
                from_element=prev_id,
                to_element=step_id
            ))
            prev_id = step_id

        # Add decisions
        for i, decision in enumerate(decisions):
            decision_id = f"decision_{i+1}"
            elements.append(DiagramElement(
                id=decision_id,
                label=decision['question'],
                element_type="decision"
            ))

            # Connect decision to flow (simplified)
            if prev_id:
                connections.append(DiagramConnection(
                    from_element=prev_id,
                    to_element=decision_id
                ))

        # End node
        end_id = "end"
        elements.append(DiagramElement(
            id=end_id,
            label="End",
            element_type="end"
        ))

        if prev_id:
            connections.append(DiagramConnection(
                from_element=prev_id,
                to_element=end_id
            ))

        return DiagramSpec(
            diagram_type=DiagramType.FLOWCHART,
            title=self._extract_process_title(description),
            description=description,
            elements=elements,
            connections=connections
        )

    def _extract_process_steps(self, description: str) -> List[str]:
        """Extract process steps from description"""
        steps = []

        # Look for numbered steps
        numbered_pattern = r'(\d+)[\.\)]\s*(.+?)(?=\n|\d+[\.\)]|$)'
        matches = re.finditer(numbered_pattern, description, re.MULTILINE)
        for match in matches:
            steps.append(match.group(2).strip())

        if steps:
            return steps

        # Look for step indicators
        step_patterns = [
            r'(?:first|1st),?\s*(.+?)(?=\n|second|then|next|$)',
            r'(?:second|2nd|then|next),?\s*(.+?)(?=\n|third|then|next|finally|$)',
            r'(?:third|3rd|then|next),?\s*(.+?)(?=\n|fourth|then|next|finally|$)',
            r'(?:finally|lastly|last),?\s*(.+?)(?=\n|$)'
        ]

        for pattern in step_patterns:
            matches = re.finditer(pattern, description, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                step = match.group(1).strip()
                if len(step) > 3:
                    steps.append(step)

        # Look for verb-based steps
        if not steps:
            verb_pattern = r'(?:^|\n)\s*(?:the\s+)?(?:user|system|process|we)\s+([a-z]+(?:s|es|ed|ing)?(?:\s+\w+)*?)(?=\n|$)'
            matches = re.finditer(verb_pattern, description, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                step = match.group(1).strip()
                if len(step) > 5 and len(step) < 100:
                    steps.append(step.capitalize())

        return steps[:10]  # Limit to 10 steps

    def _extract_decisions(self, description: str) -> List[Dict[str, str]]:
        """Extract decision points from description"""
        decisions = []

        decision_patterns = [
            r'if\s+(.+?)\s*(?:then|,)',
            r'(?:check|verify|determine)\s+(?:if|whether)\s+(.+?)(?=\n|$)',
            r'(.+?)\s*\?\s*(?:yes|no|true|false)',
            r'(?:when|while)\s+(.+?)(?=\n|$)'
        ]

        for pattern in decision_patterns:
            matches = re.finditer(pattern, description, re.IGNORECASE)
            for match in matches:
                question = match.group(1).strip()
                if len(question) > 5 and len(question) < 80:
                    decisions.append({
                        'question': question,
                        'type': 'condition'
                    })

        return decisions[:3]  # Limit to 3 decisions

    def _extract_process_title(self, description: str) -> str:
        """Extract process title"""
        title_patterns = [
            r'(?:process|workflow|procedure):\s*(.+?)(?:\n|$)',
            r'^(.+?)\s+(?:process|workflow|procedure)',
            r'(?:how to|steps to)\s+(.+?)(?:\n|$)'
        ]

        for pattern in title_patterns:
            match = re.search(pattern, description, re.IGNORECASE)
            if match:
                return match.group(1).strip().title()

        return "Process Flow"

    def generate(self, spec: DiagramSpec, output_format: DiagramFormat) -> str:
        """Generate flowchart in specified format"""

        if output_format == DiagramFormat.MERMAID:
            return self._generate_mermaid_flowchart(spec)
        elif output_format == DiagramFormat.PYTHON_DIAGRAMS:
            return self._generate_python_flowchart(spec)
        else:
            raise ValueError(f"Unsupported format: {output_format}")

    def _generate_mermaid_flowchart(self, spec: DiagramSpec) -> str:
        """Generate Mermaid flowchart"""
        lines = [
            "flowchart TD",
            f"    title[{spec.title}]",
            ""
        ]

        # Define nodes
        for element in spec.elements:
            shape = self._get_mermaid_shape(element.element_type)
            # Use sanitized labels for Mermaid flowchart nodes
            label = sanitize_mermaid_label(element.label) if element.label else ""
            lines.append(f"    {element.id}{shape[0]}{label}{shape[1]}")

        lines.append("")

        # Define connections
        for conn in spec.connections:
            arrow = "-->"
            # Use sanitized labels for Mermaid flowchart connections
            label = f"|{sanitize_mermaid_label(conn.label, is_pipe_wrapped=True)}|" if conn.label else ""
            lines.append(f"    {conn.from_element} {arrow}{label} {conn.to_element}")

        return "\n".join(lines)

    def _get_mermaid_shape(self, element_type: str) -> Tuple[str, str]:
        """Get Mermaid shape notation for element type"""
        shapes = {
            "start": ("([", "])"),
            "end": ("([", "])"),
            "process": ("[", "]"),
            "decision": ("{", "}"),
            "data": ("[(", ")]"),
            "connector": ("((", "))")
        }
        return shapes.get(element_type, ("[", "]"))

    def _generate_python_flowchart(self, spec: DiagramSpec) -> str:
        """Generate Python diagrams flowchart"""
        lines = [
            "from diagrams import Diagram",
            "from diagrams.programming.flowchart import StartEnd, Decision, Action",
            "",
            f'with Diagram("{spec.title}", show=False, direction="TD"):'
        ]

        # Create variables for nodes
        node_vars = {}
        for element in spec.elements:
            var_name = element.id

            if element.element_type in ["start", "end"]:
                class_name = "StartEnd"
            elif element.element_type == "decision":
                class_name = "Decision"
            else:
                class_name = "Action"

            lines.append(f'    {var_name} = {class_name}("{element.label}")')
            node_vars[element.id] = var_name

        lines.append("")

        # Create connections
        for conn in spec.connections:
            from_var = node_vars.get(conn.from_element)
            to_var = node_vars.get(conn.to_element)

            if from_var and to_var:
                lines.append(f"    {from_var} >> {to_var}")

        return "\n".join(lines)

    def get_supported_formats(self) -> List[DiagramFormat]:
        """Get supported formats for flowcharts"""
        return [
            DiagramFormat.MERMAID,
            DiagramFormat.PYTHON_DIAGRAMS
        ]

# ===== CLASS DIAGRAM GENERATOR =====

@dataclass
class ClassDefinition:
    """Class definition for class diagrams"""
    name: str
    attributes: List[str] = field(default_factory=list)
    methods: List[str] = field(default_factory=list)
    stereotypes: List[str] = field(default_factory=list)
    visibility: str = "public"  # public, private, protected

@dataclass
class ClassRelationship:
    """Relationship between classes"""
    from_class: str
    to_class: str
    relationship_type: str  # inheritance, composition, aggregation, association, dependency
    multiplicity: Optional[str] = None
    label: Optional[str] = None

class ClassDiagramGenerator(DiagramGenerator):
    """Generator for class/entity relationship diagrams"""

    def parse_natural_language(self, description: str) -> DiagramSpec:
        """Parse natural language into class diagram spec"""

        # Extract classes from description
        classes = self._extract_classes(description)

        # Extract relationships
        relationships = self._extract_relationships(description, classes)

        # Create diagram elements
        elements = []
        for cls in classes:
            elements.append(DiagramElement(
                id=f"class_{cls.name.lower()}",
                label=cls.name,
                element_type="class",
                properties={
                    "attributes": cls.attributes,
                    "methods": cls.methods,
                    "stereotypes": cls.stereotypes
                }
            ))

        # Create connections from relationships
        connections = []
        for rel in relationships:
            connections.append(DiagramConnection(
                from_element=f"class_{rel.from_class.lower()}",
                to_element=f"class_{rel.to_class.lower()}",
                label=rel.label,
                connection_type=rel.relationship_type,
                properties={"multiplicity": rel.multiplicity}
            ))

        return DiagramSpec(
            diagram_type=DiagramType.CLASS,
            title=self._extract_class_diagram_title(description),
            description=description,
            elements=elements,
            connections=connections
        )

    def _extract_classes(self, description: str) -> List[ClassDefinition]:
        """Extract class definitions from description"""
        classes = []

        # Pattern for class definitions
        class_patterns = [
            r'class\s+(\w+)',
            r'entity\s+(\w+)',
            r'model\s+(\w+)',
            r'(?:a|an)\s+(\w+)\s+(?:class|entity|object)',
            r'(\w+)\s+(?:has|contains|includes|manages)'
        ]

        found_classes = set()

        for pattern in class_patterns:
            matches = re.finditer(pattern, description, re.IGNORECASE)
            for match in matches:
                class_name = match.group(1).strip()
                if len(class_name) > 2 and class_name.lower() not in found_classes:
                    # Extract attributes and methods for this class
                    attributes = self._extract_class_attributes(class_name, description)
                    methods = self._extract_class_methods(class_name, description)

                    classes.append(ClassDefinition(
                        name=class_name.capitalize(),
                        attributes=attributes,
                        methods=methods
                    ))
                    found_classes.add(class_name.lower())

        # If no explicit classes found, infer from domain entities
        if not classes:
            domain_entities = self._extract_domain_entities(description)
            for entity in domain_entities:
                classes.append(ClassDefinition(name=entity.capitalize()))

        return classes[:8]  # Limit to 8 classes

    def _extract_class_attributes(self, class_name: str, description: str) -> List[str]:
        """Extract attributes for a specific class"""
        attributes = []

        # Look for property patterns
        attribute_patterns = [
            fr'{class_name}\s+has\s+(?:a\s+)?(\w+(?:\s+\w+)*)',
            fr'{class_name}\s+contains\s+(\w+(?:\s+\w+)*)',
            fr'{class_name}.*?(?:with|having)\s+(\w+(?:\s+\w+)*)',
            fr'(\w+)\s+(?:of|in)\s+{class_name}'
        ]

        for pattern in attribute_patterns:
            matches = re.finditer(pattern, description, re.IGNORECASE)
            for match in matches:
                attr = match.group(1).strip()
                if len(attr) < 30 and attr.lower() != class_name.lower():
                    attributes.append(attr.lower().replace(' ', '_'))

        # Common attributes based on class type
        class_lower = class_name.lower()
        if 'user' in class_lower:
            attributes.extend(['id', 'name', 'email', 'created_at'])
        elif 'product' in class_lower:
            attributes.extend(['id', 'name', 'price', 'description'])
        elif 'order' in class_lower:
            attributes.extend(['id', 'status', 'total', 'created_at'])

        return list(set(attributes))[:6]  # Remove duplicates, limit to 6

    def _extract_class_methods(self, class_name: str, description: str) -> List[str]:
        """Extract methods for a specific class"""
        methods = []

        # Look for action patterns
        method_patterns = [
            fr'{class_name}\s+(?:can|should|will|must)\s+(\w+(?:\s+\w+)*)',
            fr'(\w+(?:\s+\w+)*)\s+(?:the\s+)?{class_name}',
            fr'{class_name}.*?(?:to|for)\s+(\w+(?:\s+\w+)*)'
        ]

        for pattern in method_patterns:
            matches = re.finditer(pattern, description, re.IGNORECASE)
            for match in matches:
                method = match.group(1).strip()
                if len(method) < 30:
                    # Convert to method name format
                    method_name = method.lower().replace(' ', '_')
                    if not method_name.startswith(('get_', 'set_', 'is_', 'has_')):
                        if any(verb in method_name for verb in ['create', 'add', 'insert']):
                            method_name = 'create_' + method_name.split('_')[-1]
                        elif any(verb in method_name for verb in ['update', 'modify', 'change']):
                            method_name = 'update_' + method_name.split('_')[-1]
                        elif any(verb in method_name for verb in ['delete', 'remove']):
                            method_name = 'delete_' + method_name.split('_')[-1]
                        elif any(verb in method_name for verb in ['find', 'search', 'get']):
                            method_name = 'get_' + method_name.split('_')[-1]

                    methods.append(method_name + '()')

        return list(set(methods))[:6]  # Remove duplicates, limit to 6

    def _extract_domain_entities(self, description: str) -> List[str]:
        """Extract domain entities when no explicit classes mentioned"""
        entities = []

        # Look for noun phrases that could be entities
        noun_patterns = [
            r'\b([A-Z]\w+)\b',  # Capitalized words
            r'\b(user|customer|product|order|payment|account|service|item|record)\b'
        ]

        found_entities = set()
        for pattern in noun_patterns:
            matches = re.finditer(pattern, description, re.IGNORECASE)
            for match in matches:
                entity = match.group(1).lower()
                if (len(entity) > 2 and entity not in found_entities and
                    entity not in ['the', 'and', 'for', 'with', 'this', 'that']):
                    entities.append(entity)
                    found_entities.add(entity)

        return entities[:5]

    def _extract_relationships(self, description: str, classes: List[ClassDefinition]) -> List[ClassRelationship]:
        """Extract relationships between classes"""
        relationships = []
        class_names = [cls.name.lower() for cls in classes]

        # Relationship patterns
        relationship_patterns = [
            (r'(\w+)\s+(?:inherits from|extends|is a)\s+(\w+)', 'inheritance'),
            (r'(\w+)\s+(?:has|contains|owns)\s+(?:a|an|many)?\s*(\w+)', 'composition'),
            (r'(\w+)\s+(?:uses|depends on|relies on)\s+(\w+)', 'dependency'),
            (r'(\w+)\s+(?:is associated with|relates to)\s+(\w+)', 'association'),
            (r'(\w+)\s+(?:aggregates|includes)\s+(\w+)', 'aggregation')
        ]

        for pattern, rel_type in relationship_patterns:
            matches = re.finditer(pattern, description, re.IGNORECASE)
            for match in matches:
                from_class = match.group(1).lower()
                to_class = match.group(2).lower()

                # Only include if both classes exist
                if from_class in class_names and to_class in class_names:
                    relationships.append(ClassRelationship(
                        from_class=from_class,
                        to_class=to_class,
                        relationship_type=rel_type,
                        label=rel_type.replace('_', ' ').title()
                    ))

        return relationships[:10]  # Limit to 10 relationships

    def _extract_class_diagram_title(self, description: str) -> str:
        """Extract title for class diagram"""
        title_patterns = [
            r'(?:class diagram|domain model|entity model):\s*(.+?)(?:\n|$)',
            r'^(.+?)\s+(?:class diagram|domain model|entity model)',
            r'(?:model|classes) for\s+(.+?)(?:\n|$)'
        ]

        for pattern in title_patterns:
            match = re.search(pattern, description, re.IGNORECASE)
            if match:
                return match.group(1).strip().title()

        return "Class Diagram"

    def generate(self, spec: DiagramSpec, output_format: DiagramFormat) -> str:
        """Generate class diagram in specified format"""

        if output_format == DiagramFormat.MERMAID:
            return self._generate_mermaid_class(spec)
        elif output_format == DiagramFormat.PLANTUML:
            return self._generate_plantuml_class(spec)
        elif output_format == DiagramFormat.PYTHON_DIAGRAMS:
            return self._generate_python_class(spec)
        else:
            raise ValueError(f"Unsupported format: {output_format}")

    def _generate_mermaid_class(self, spec: DiagramSpec) -> str:
        """Generate Mermaid class diagram"""
        lines = [
            "classDiagram",
            f"    title {spec.title}",
            ""
        ]

        # Define classes
        for element in spec.elements:
            if element.element_type == "class":
                class_name = element.label
                lines.append(f"    class {class_name} {{")

                # Add attributes
                for attr in element.properties.get('attributes', []):
                    lines.append(f"        +{attr}")

                # Add methods
                for method in element.properties.get('methods', []):
                    lines.append(f"        +{method}")

                lines.append("    }")
                lines.append("")

        # Define relationships
        for conn in spec.connections:
            from_class = conn.from_element.replace('class_', '').title()
            to_class = conn.to_element.replace('class_', '').title()

            # Map relationship types to Mermaid notation
            rel_notation = {
                'inheritance': '<|--',
                'composition': '*--',
                'aggregation': 'o--',
                'association': '--',
                'dependency': '..>'
            }

            notation = rel_notation.get(conn.connection_type, '--')
            lines.append(f"    {to_class} {notation} {from_class}")

        return "\n".join(lines)

    def _generate_plantuml_class(self, spec: DiagramSpec) -> str:
        """Generate PlantUML class diagram"""
        lines = [
            "@startuml",
            f"title {spec.title}",
            ""
        ]

        # Define classes
        for element in spec.elements:
            if element.element_type == "class":
                class_name = element.label
                lines.append(f"class {class_name} {{")

                # Add attributes
                for attr in element.properties.get('attributes', []):
                    lines.append(f"  +{attr}")

                lines.append("  --")

                # Add methods
                for method in element.properties.get('methods', []):
                    lines.append(f"  +{method}")

                lines.append("}")
                lines.append("")

        # Define relationships
        for conn in spec.connections:
            from_class = conn.from_element.replace('class_', '').title()
            to_class = conn.to_element.replace('class_', '').title()

            # Map relationship types to PlantUML notation
            rel_notation = {
                'inheritance': '<|--',
                'composition': '*--',
                'aggregation': 'o--',
                'association': '--',
                'dependency': '..>'
            }

            notation = rel_notation.get(conn.connection_type, '--')
            lines.append(f"{to_class} {notation} {from_class}")

        lines.extend(["", "@enduml"])
        return "\n".join(lines)

    def _generate_python_class(self, spec: DiagramSpec) -> str:
        """Generate Python diagrams for class-like diagram"""
        # Python diagrams doesn't have native class diagram support
        # This creates a component-like representation
        lines = [
            "from diagrams import Diagram, Cluster, Edge",
            "from diagrams.generic.blank import Blank",
            "",
            f'with Diagram("{spec.title}", show=False, direction="TB"):'
        ]

        # Group related classes in clusters
        class_vars = {}
        for element in spec.elements:
            if element.element_type == "class":
                var_name = element.id.replace('class_', '')
                class_name = element.label

                # Create a simple representation
                lines.append(f'    {var_name} = Blank("{class_name}")')
                class_vars[element.id] = var_name

        lines.append("")

        # Create relationships
        for conn in spec.connections:
            from_var = class_vars.get(conn.from_element)
            to_var = class_vars.get(conn.to_element)

            if from_var and to_var:
                edge_style = f'Edge(label="{conn.connection_type}")'
                lines.append(f"    {from_var} >> {edge_style} >> {to_var}")

        return "\n".join(lines)

    def get_supported_formats(self) -> List[DiagramFormat]:
        """Get supported formats for class diagrams"""
        return [
            DiagramFormat.MERMAID,
            DiagramFormat.PLANTUML,
            DiagramFormat.PYTHON_DIAGRAMS
        ]

# ===== UNIFIED DIAGRAM FACTORY =====

class DiagramGeneratorFactory:
    """Factory for creating diagram generators"""

    @staticmethod
    def create_generator(diagram_type: DiagramType) -> DiagramGenerator:
        """Create appropriate generator for diagram type"""
        generators = {
            DiagramType.SEQUENCE: SequenceDiagramGenerator(),
            DiagramType.FLOWCHART: FlowchartGenerator(),
            DiagramType.CLASS: ClassDiagramGenerator(),
            # Add more generators as implemented
        }

        generator = generators.get(diagram_type)
        if not generator:
            raise ValueError(f"Unsupported diagram type: {diagram_type}")

        return generator

# ===== MCP INTEGRATION =====

class MultiDiagramService:
    """Service for generating multiple diagram types"""

    def __init__(self):
        self.factory = DiagramGeneratorFactory()

    def generate_diagram(
        self,
        description: str,
        diagram_type: str,
        output_format: str = "mermaid",
        title: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate diagram from natural language description.

        Args:
            description: Natural language description of the diagram
            diagram_type: Type of diagram (sequence, flowchart, class, etc.)
            output_format: Output format (mermaid, plantuml, python_diagrams)
            title: Optional custom title

        Returns:
            Dictionary with generated diagram code and metadata
        """
        try:
            # Parse diagram type and format
            diagram_type_enum = DiagramType(diagram_type.lower())
            format_enum = DiagramFormat(output_format.lower())

            # Get appropriate generator
            generator = self.factory.create_generator(diagram_type_enum)

            # Check if format is supported
            if format_enum not in generator.get_supported_formats():
                return {
                    "error": f"Format '{output_format}' not supported for {diagram_type} diagrams",
                    "supported_formats": [f.value for f in generator.get_supported_formats()]
                }

            # Parse description into diagram spec
            spec = generator.parse_natural_language(description)

            # Override title if provided
            if title:
                spec.title = title

            # Generate diagram code
            diagram_code = generator.generate(spec, format_enum)

            return {
                "success": True,
                "diagram_type": diagram_type,
                "output_format": output_format,
                "title": spec.title,
                "diagram_code": diagram_code,
                "metadata": {
                    "elements_count": len(spec.elements),
                    "connections_count": len(spec.connections),
                    "parsed_from": "natural_language"
                },
                "spec": {
                    "elements": len(spec.elements),
                    "connections": len(spec.connections),
                    "diagram_metadata": spec.metadata
                }
            }

        except ValueError as e:
            return {
                "error": str(e),
                "supported_diagram_types": [dt.value for dt in DiagramType],
                "supported_formats": [df.value for df in DiagramFormat]
            }
        except Exception as e:
            logger.error(f"Error generating diagram: {e}")
            return {
                "error": f"Failed to generate diagram: {str(e)}"
            }

    def get_supported_types_and_formats(self) -> Dict[str, List[str]]:
        """Get supported diagram types and their formats"""
        supported = {}

        for diagram_type in [DiagramType.SEQUENCE, DiagramType.FLOWCHART, DiagramType.CLASS]:
            try:
                generator = self.factory.create_generator(diagram_type)
                supported[diagram_type.value] = [f.value for f in generator.get_supported_formats()]
            except ValueError:
                # Generator not implemented yet
                continue

        return supported
