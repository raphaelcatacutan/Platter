"""
AST Reader and Pretty Printer
Provides utilities to traverse and display the AST structure
"""

from app.semantic_analyzer.ast.ast_nodes import *
import json


class ASTReader:
    """Read and traverse the AST"""
    
    def __init__(self, ast_root):
        self.root = ast_root
    
    def to_dict(self, node, depth=0, max_depth=50):
        """Convert AST node to dictionary representation"""
        if depth > max_depth:
            return {"type": "MAX_DEPTH_EXCEEDED"}
        
        if node is None:
            return None
        
        if isinstance(node, list):
            return [self.to_dict(item, depth + 1, max_depth) for item in node]
        
        if isinstance(node, tuple):
            return tuple(self.to_dict(item, depth + 1, max_depth) for item in node)
        
        if isinstance(node, (str, int, float, bool)):
            return node
        
        if not isinstance(node, ASTNode):
            return str(node)
        
        result = {
            "node_type": node.node_type,
            "class": node.__class__.__name__
        }
        
        # Add all attributes except node_type
        for attr, value in node.__dict__.items():
            if attr != "node_type":
                result[attr] = self.to_dict(value, depth + 1, max_depth)
        
        return result
    
    def to_json(self, indent=2):
        """Convert AST to JSON string"""
        ast_dict = self.to_dict(self.root)
        return json.dumps(ast_dict, indent=indent, ensure_ascii=False)
    
    def pretty_print(self, node=None, indent=0, prefix=""):
        """Pretty print the AST to console"""
        if node is None:
            node = self.root
        
        if node is None:
            print(f"{' ' * indent}{prefix}None")
            return
        
        if isinstance(node, list):
            if not node:
                print(f"{' ' * indent}{prefix}[]")
                return
            print(f"{' ' * indent}{prefix}[")
            for i, item in enumerate(node):
                is_last = (i == len(node) - 1)
                item_prefix = "  └─ " if is_last else "  ├─ "
                self.pretty_print(item, indent + 2, item_prefix)
            print(f"{' ' * indent}]")
            return
        
        if isinstance(node, tuple):
            print(f"{' ' * indent}{prefix}(")
            for i, item in enumerate(node):
                is_last = (i == len(node) - 1)
                item_prefix = "  └─ " if is_last else "  ├─ "
                self.pretty_print(item, indent + 2, item_prefix)
            print(f"{' ' * indent})")
            return
        
        if isinstance(node, (str, int, float, bool)):
            print(f"{' ' * indent}{prefix}{repr(node)}")
            return
        
        if not isinstance(node, ASTNode):
            print(f"{' ' * indent}{prefix}{str(node)}")
            return
        
        # Print node type
        print(f"{' ' * indent}{prefix}{node.__class__.__name__}")
        
        # Print attributes
        attrs = [(k, v) for k, v in node.__dict__.items() if k != "node_type"]
        for i, (attr, value) in enumerate(attrs):
            is_last = (i == len(attrs) - 1)
            attr_prefix = "  └─ " if is_last else "  ├─ "
            
            if isinstance(value, (list, tuple)) and value:
                print(f"{' ' * (indent + 2)}{attr_prefix}{attr}: ", end="")
                self.pretty_print(value, indent + 2, "")
            elif isinstance(value, ASTNode):
                print(f"{' ' * (indent + 2)}{attr_prefix}{attr}:")
                sub_prefix = "    "
                self.pretty_print(value, indent + 4, sub_prefix)
            else:
                print(f"{' ' * (indent + 2)}{attr_prefix}{attr}: {repr(value)}")


def print_ast(ast_root, format="pretty"):
    """
    Print the AST in specified format
    
    Args:
        ast_root: Root AST node
        format: "pretty" for tree view, "json" for JSON output
    """
    reader = ASTReader(ast_root)
    
    if format == "json":
        print(reader.to_json())
    else:
        print("\n" + "="*60)
        print("AST Structure:")
        print("="*60)
        reader.pretty_print()
        print("="*60 + "\n")
