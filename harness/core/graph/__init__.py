"""
Graph Engine - Graph definition and execution
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable, Set
from enum import Enum


class NodeType(Enum):
    STANDARD = "standard"
    START = "start"
    END = "end"
    CONDITIONAL = "conditional"
    LOOP = "loop"


@dataclass
class Node:
    """Represents a node in the graph"""
    id: str
    name: str
    node_type: NodeType = NodeType.STANDARD
    execute_func: Optional[Callable] = None
    condition_func: Optional[Callable] = None  # For conditional nodes
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def execute(self, state: Any) -> Any:
        """Execute the node's logic"""
        if self.execute_func:
            return self.execute_func(state)
        return None
    
    def evaluate_condition(self, state: Any) -> str:
        """Evaluate condition for branching (returns next node ID)"""
        if self.condition_func:
            return self.condition_func(state)
        return None


@dataclass
class Edge:
    """Represents an edge between nodes"""
    source: str
    target: str
    condition: Optional[str] = None  # Condition for conditional edges
    metadata: Dict[str, Any] = field(default_factory=dict)


class Graph:
    """Represents a directed graph of nodes"""
    
    def __init__(self, name: str = "default"):
        self.name = name
        self.nodes: Dict[str, Node] = {}
        self.edges: List[Edge] = []
        self.start_node: Optional[str] = None
        self.end_node: Optional[str] = None
        self._adjacency: Dict[str, List[Edge]] = {}
    
    def add_node(self, node: Node):
        """Add a node to the graph"""
        self.nodes[node.id] = node
        self._adjacency[node.id] = []
        
        if node.node_type == NodeType.START:
            self.start_node = node.id
        elif node.node_type == NodeType.END:
            self.end_node = node.id
    
    def add_edge(self, edge: Edge):
        """Add an edge to the graph"""
        self.edges.append(edge)
        # Ensure source node exists in adjacency list
        if edge.source not in self._adjacency:
            self._adjacency[edge.source] = []
        self._adjacency[edge.source].append(edge)
        # Ensure target node exists in adjacency list
        if edge.target not in self._adjacency:
            self._adjacency[edge.target] = []
    
    def get_next_nodes(self, node_id: str, state: Any = None) -> List[str]:
        """Get the next node(s) to execute from current node"""
        if node_id not in self._adjacency:
            return []
        
        next_nodes = []
        for edge in self._adjacency[node_id]:
            if edge.condition:
                # Conditional edge - evaluate condition
                if state and hasattr(state, 'outputs'):
                    # Simple condition evaluation
                    condition_result = state.outputs.get(edge.condition, False)
                    if condition_result:
                        next_nodes.append(edge.target)
                else:
                    # Try to get condition from node's condition_func
                    source_node = self.nodes.get(node_id)
                    if source_node:
                        result = source_node.evaluate_condition(state)
                        if result == edge.target:
                            next_nodes.append(edge.target)
            else:
                next_nodes.append(edge.target)
        
        return next_nodes
    
    def get_node(self, node_id: str) -> Optional[Node]:
        """Get a node by ID"""
        return self.nodes.get(node_id)
    
    def validate(self) -> tuple[bool, List[str]]:
        """Validate the graph structure"""
        errors = []
        
        # Check for start node
        if not self.start_node:
            errors.append("Graph must have a START node")
        
        # Check for end node
        if not self.end_node:
            errors.append("Graph must have an END node")
        
        # Check all nodes are reachable from start
        if self.start_node:
            visited = set()
            self._dfs(self.start_node, visited)
            
            unreachable = set(self.nodes.keys()) - visited
            if unreachable:
                errors.append(f"Unreachable nodes: {unreachable}")
        
        # Check all nodes can reach end (no dead ends except END)
        if self.end_node:
            reverse_adj = self._build_reverse_adjacency()
            visited = set()
            self._dfs_reverse(self.end_node, visited, reverse_adj)
            
            cant_reach_end = set(self.nodes.keys()) - visited
            if cant_reach_end:
                errors.append(f"Nodes that cannot reach END: {cant_reach_end}")
        
        return len(errors) == 0, errors
    
    def _dfs(self, node_id: str, visited: Set[str]):
        """Depth-first search from a node"""
        if node_id in visited:
            return
        visited.add(node_id)
        
        for edge in self._adjacency.get(node_id, []):
            self._dfs(edge.target, visited)
    
    def _build_reverse_adjacency(self) -> Dict[str, List[str]]:
        """Build reverse adjacency list"""
        reverse = {}
        for node_id in self.nodes:
            reverse[node_id] = []
        
        for edge in self.edges:
            if edge.target in reverse:
                reverse[edge.target].append(edge.source)
        
        return reverse
    
    def _dfs_reverse(self, node_id: str, visited: Set[str], reverse_adj: Dict[str, List[str]]):
        """DFS on reverse graph"""
        if node_id in visited:
            return
        visited.add(node_id)
        
        for source in reverse_adj.get(node_id, []):
            self._dfs_reverse(source, visited, reverse_adj)
    
    def get_execution_order(self) -> List[str]:
        """Get topological order of nodes for execution"""
        if not self.start_node:
            return []
        
        order = []
        visited = set()
        stack = [self.start_node]
        
        while stack:
            node_id = stack.pop(0)
            if node_id in visited:
                continue
            visited.add(node_id)
            order.append(node_id)
            
            if node_id == self.end_node:
                continue
            
            for edge in self._adjacency.get(node_id, []):
                if edge.target not in visited:
                    stack.append(edge.target)
        
        return order
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert graph to dictionary representation"""
        return {
            "name": self.name,
            "nodes": {nid: {"id": n.id, "name": n.name, "type": n.node_type.value} 
                     for nid, n in self.nodes.items()},
            "edges": [{"source": e.source, "target": e.target, "condition": e.condition} 
                     for e in self.edges],
            "start": self.start_node,
            "end": self.end_node
        }


class GraphBuilder:
    """Fluent builder for creating graphs"""
    
    def __init__(self, name: str = "default"):
        self.graph = Graph(name)
        self._last_node: Optional[str] = None
    
    def add_start(self) -> 'GraphBuilder':
        """Add START node"""
        node = Node(id="START", name="Start", node_type=NodeType.START)
        self.graph.add_node(node)
        self._last_node = "START"
        return self
    
    def add_end(self) -> 'GraphBuilder':
        """Add END node and connect from last node"""
        node = Node(id="END", name="End", node_type=NodeType.END)
        self.graph.add_node(node)
        
        # Connect from last node to END
        if self._last_node and self._last_node != "END":
            self.graph.add_edge(Edge(source=self._last_node, target="END"))
        
        return self
    
    def add_node(self, node_id: str, name: str, 
                 execute_func: Optional[Callable] = None,
                 node_type: NodeType = NodeType.STANDARD,
                 **metadata) -> 'GraphBuilder':
        """Add a standard node"""
        node = Node(
            id=node_id, 
            name=name, 
            node_type=node_type,
            execute_func=execute_func,
            metadata=metadata
        )
        self.graph.add_node(node)
        
        # Connect from last node to this node
        if self._last_node:
            self.graph.add_edge(Edge(source=self._last_node, target=node_id))
        
        self._last_node = node_id
        return self
    
    def add_conditional_node(self, node_id: str, name: str,
                            condition_func: Callable,
                            **metadata) -> 'GraphBuilder':
        """Add a conditional node"""
        node = Node(
            id=node_id,
            name=name,
            node_type=NodeType.CONDITIONAL,
            condition_func=condition_func,
            metadata=metadata
        )
        self.graph.add_node(node)
        
        if self._last_node:
            self.graph.add_edge(Edge(source=self._last_node, target=node_id))
        
        self._last_node = node_id
        return self
    
    def connect(self, source: str, target: str, condition: Optional[str] = None) -> 'GraphBuilder':
        """Add an edge between nodes"""
        self.graph.add_edge(Edge(source=source, target=target, condition=condition))
        return self
    
    def build(self) -> Graph:
        """Build and return the graph"""
        return self.graph
