"""
Symbol Table Management for Platter Language
Handles scope stack, symbol lookup, and type registration
"""

from app.semantic_analyzer.symbol_table.types import Symbol, Scope, SymbolKind, TypeInfo
from app.semantic_analyzer.ast.ast_nodes import ASTNode
from typing import Optional, Dict, List


class SymbolTable:
    """Manages symbol table with scope stack"""
    
    def __init__(self):
        self.global_scope = Scope("global", 0)
        self.current_scope = self.global_scope
        self.scope_counter = 0
        # Track counters per scope type for incremental naming
        self.scope_type_counters: Dict[str, int] = {
            'check': 0, 'alt': 0, 'instead': 0,
            'pass': 0, 'repeat': 0, 'order_repeat': 0,
            'menu': 0, 'choice': 0, 'default': 0,
            'block': 0, 'start_platter': 0
        }
        self.table_types: Dict[str, TypeInfo] = {}
        self.current_function: Optional[Symbol] = None
        self.in_loop = 0
        # Error handler will be set by the semantic analyzer
        self.error_handler = None
        # Track undeclared symbols that are accessed
        self.undeclared_symbols: Dict[str, Symbol] = {}
    
    def enter_scope(self, name: str) -> Scope:
        """Enter a new scope with incremental counter per scope type"""
        # For recipes, don't add suffix
        if name.startswith('recipe_'):
            scope_name = name.replace('recipe_', '')  # Remove recipe_ prefix
        # For scope types with counters, use incremental numbering
        elif name in self.scope_type_counters:
            self.scope_type_counters[name] += 1
            scope_name = f"{name}_{self.scope_type_counters[name]}"
        else:
            scope_name = name
        
        new_scope = Scope(scope_name, self.current_scope.level + 1, self.current_scope)
        self.current_scope.children.append(new_scope)
        self.current_scope = new_scope
        return new_scope
    
    def exit_scope(self):
        """Exit current scope"""
        if self.current_scope.parent:
            self.current_scope = self.current_scope.parent
    
    def navigate_to_scope(self, scope_name: str) -> bool:
        """Navigate to an existing child scope by name (for semantic passes)"""
        for child in self.current_scope.children:
            if child.name == scope_name:
                self.current_scope = child
                return True
        return False
    
    def define_symbol(self, name: str, kind: SymbolKind, type_info: TypeInfo, 
                     declaration_node: ASTNode = None) -> bool:
        """Define a symbol in current scope"""
        symbol = Symbol(name, kind, type_info, self.current_scope.level, declaration_node, self.current_scope)
        
        if not self.current_scope.define(symbol):
            if self.error_handler:
                self.error_handler.add_error(
                    f"Symbol '{name}' already defined in scope '{self.current_scope.name}'", 
                    declaration_node
                )
            return False
        
        if kind == SymbolKind.TABLE_TYPE:
            self.table_types[name] = type_info
        
        return True
    
    def add_symbol(self, name: str, symbol: Symbol) -> bool:
        """Add a pre-created symbol to current scope"""
        if not self.current_scope.define(symbol):
            if self.error_handler:
                self.error_handler.add_error(
                    f"Symbol '{name}' already defined in scope '{self.current_scope.name}'", 
                    symbol.declaration_node
                )
            return False
        
        if symbol.kind == SymbolKind.TABLE_TYPE:
            self.table_types[name] = symbol.type_info
        
        return True
    
    def lookup_symbol(self, name: str) -> Optional[Symbol]:
        """Look up symbol"""
        return self.current_scope.lookup(name)
    
    def lookup_table_type(self, name: str) -> Optional[TypeInfo]:
        """Look up a table type definition"""
        return self.table_types.get(name)
    
    def is_type_defined(self, type_name: str) -> bool:
        """Check if a type is defined"""
        builtin_types = {"piece", "sip", "flag", "chars"}
        return type_name in builtin_types or type_name in self.table_types
    
    def print_scope_tree(self, scope: Scope = None, indent: int = 0):
        """Print the scope tree"""
        if scope is None:
            scope = self.global_scope
        
        print("  " * indent + str(scope))
        for name, symbol in scope.symbols.items():
            print("  " * (indent + 1) + f"├─ {symbol}")
        
        for child in scope.children:
            self.print_scope_tree(child, indent + 1)
