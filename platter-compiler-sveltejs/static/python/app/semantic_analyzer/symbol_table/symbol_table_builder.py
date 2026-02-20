"""
Symbol Table Builder for Platter Language
Handles scoping and symbol collection - traverses AST to build symbol table structure
NOTE: This version does NOT perform semantic checking - it only collects symbols
"""

from app.semantic_analyzer.ast.ast_nodes import *
from typing import Optional, Dict, List
from enum import Enum


class SymbolKind(Enum):
    """Types of symbols in the symbol table"""
    VARIABLE = "variable"
    PARAMETER = "parameter"
    FUNCTION = "function"
    TABLE_TYPE = "table_type"
    FIELD = "field"


class TypeInfo:
    """Represents type information including arrays and nested structures"""
    
    def __init__(self, base_type: str, dimensions: int = 0, table_fields: Optional[Dict[str, 'TypeInfo']] = None):
        self.base_type = base_type
        self.dimensions = dimensions if dimensions is not None else 0
        self.table_fields = table_fields or {}
        self.is_table = table_fields is not None
    
    def __repr__(self):
        dims = f"{'[]' * self.dimensions}" if self.dimensions > 0 else ""
        if self.is_table:
            return f"Table({self.base_type}){dims}"
        return f"{self.base_type}{dims}"
    
    def __eq__(self, other):
        if not isinstance(other, TypeInfo):
            return False
        return (self.base_type == other.base_type and 
                self.dimensions == other.dimensions and
                self.is_table == other.is_table)
    
    def is_compatible_with(self, other: 'TypeInfo') -> bool:
        """Check if this type is compatible with another"""
        if self == other:
            return True
        if self.dimensions != other.dimensions:
            return False
        if self.base_type != other.base_type:
            if {self.base_type, other.base_type} == {"piece", "sip"}:
                return True
            return False
        if self.is_table and other.is_table:
            if set(self.table_fields.keys()) != set(other.table_fields.keys()):
                return False
            for field_name in self.table_fields:
                if not self.table_fields[field_name].is_compatible_with(other.table_fields[field_name]):
                    return False
        return True
    
    def get_element_type(self) -> Optional['TypeInfo']:
        """Get the type of array elements"""
        if self.dimensions == 0:
            return None
        return TypeInfo(self.base_type, self.dimensions - 1, self.table_fields if self.is_table else None)
    
    def get_field_type(self, field_name: str) -> Optional['TypeInfo']:
        """Get the type of a table field"""
        if not self.is_table:
            return None
        return self.table_fields.get(field_name)


class Symbol:
    """Represents a symbol in the symbol table"""
    
    def __init__(self, name: str, kind: SymbolKind, type_info: TypeInfo, 
                 scope_level: int, declaration_node: ASTNode = None, declared_scope: 'Scope' = None):
        self.name = name
        self.kind = kind
        self.type_info = type_info
        self.scope_level = scope_level
        self.declaration_node = declaration_node
        self.declared_scope = declared_scope  # Store the scope where declared
        self.is_initialized = False
        self.usages = []  # List of scope names where this symbol is accessed
        self.accessed_in_scopes = []  # Track unique scope names where accessed
    
    def add_usage(self, scope_name: str, declared_scope_name: str):
        """Record that this symbol was accessed in a given scope (only if different from declaration scope)"""
        # Only record if accessed in a different scope than where it was declared
        if scope_name != declared_scope_name and scope_name not in self.accessed_in_scopes:
            self.accessed_in_scopes.append(scope_name)
    
    def __repr__(self):
        return f"Symbol({self.name}: {self.type_info}, kind={self.kind.value}, level={self.scope_level})"


class Scope:
    """Represents a lexical scope"""
    
    def __init__(self, name: str, level: int, parent: Optional['Scope'] = None):
        self.name = name
        self.level = level
        self.parent = parent
        self.symbols: Dict[str, Symbol] = {}
        self.children: List['Scope'] = []
        self.declaring_scope = None  # The scope where this scope's symbols are declared
    
    def define(self, symbol: Symbol) -> bool:
        """Define a symbol in this scope"""
        if symbol.name in self.symbols:
            return False
        self.symbols[symbol.name] = symbol
        return True
    
    def lookup_local(self, name: str) -> Optional[Symbol]:
        """Look up symbol in this scope only"""
        return self.symbols.get(name)
    
    def lookup(self, name: str) -> Optional[Symbol]:
        """Look up symbol in this scope and parent scopes"""
        if name in self.symbols:
            return self.symbols[name]
        if self.parent:
            return self.parent.lookup(name)
        return None
    
    def get_all_symbols(self) -> Dict[str, Symbol]:
        """Get all symbols visible in this scope"""
        all_symbols = {}
        if self.parent:
            all_symbols = self.parent.get_all_symbols()
        all_symbols.update(self.symbols)
        return all_symbols
    
    def __repr__(self):
        return f"Scope({self.name}, level={self.level}, symbols={len(self.symbols)})"


class SemanticError:
    """Represents a semantic error"""
    
    def __init__(self, message: str, node: ASTNode = None, severity: str = "error"):
        self.message = message
        self.node = node
        self.severity = severity
    
    def __repr__(self):
        return f"[{self.severity.upper()}] {self.message}"


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
        self.errors: List[SemanticError] = []
        self.table_types: Dict[str, TypeInfo] = {}
        self.current_function: Optional[Symbol] = None
        self.in_loop = 0
    
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
    
    def define_symbol(self, name: str, kind: SymbolKind, type_info: TypeInfo, 
                     declaration_node: ASTNode = None) -> bool:
        """Define a symbol in current scope"""
        symbol = Symbol(name, kind, type_info, self.current_scope.level, declaration_node, self.current_scope)
        
        if not self.current_scope.define(symbol):
            self.add_error(f"Symbol '{name}' already defined in scope '{self.current_scope.name}'", declaration_node)
            return False
        
        if kind == SymbolKind.TABLE_TYPE:
            self.table_types[name] = type_info
        
        return True
    
    def lookup_symbol(self, name: str) -> Optional[Symbol]:
        """Look up symbol"""
        return self.current_scope.lookup(name)
    
    def lookup_table_type(self, name: str) -> Optional[TypeInfo]:
        """Look up a table type definition"""
        return self.table_types.get(name)
    
    def is_type_defined(self, type_name: str) -> bool:
        """Check if a type is defined"""
        builtin_types = {"piece", "sip", "flag", "chars", "void"}
        return type_name in builtin_types or type_name in self.table_types
    
    def add_error(self, message: str, node: ASTNode = None, severity: str = "error"):
        """Add a semantic error"""
        self.errors.append(SemanticError(message, node, severity))
    
    def add_warning(self, message: str, node: ASTNode = None):
        """Add a semantic warning"""
        self.add_error(message, node, "warning")
    
    def has_errors(self) -> bool:
        """Check if there are any errors"""
        return any(e.severity == "error" for e in self.errors)
    
    def get_errors_str(self) -> str:
        """Get formatted error string"""
        if not self.errors:
            return "No errors"
        return "\n".join(str(e) for e in self.errors)
    
    def print_scope_tree(self, scope: Scope = None, indent: int = 0):
        """Print the scope tree"""
        if scope is None:
            scope = self.global_scope
        
        print("  " * indent + str(scope))
        for name, symbol in scope.symbols.items():
            print("  " * (indent + 1) + f"├─ {symbol}")
        
        for child in scope.children:
            self.print_scope_tree(child, indent + 1)


class SymbolTableBuilder:
    """Builds symbol table by traversing the AST - NO semantic checking!"""
    
    def __init__(self):
        self.symbol_table = SymbolTable()
        self.built = False
    
    def build(self, ast_root: Program) -> SymbolTable:
        """Build symbol table from AST"""
        if not isinstance(ast_root, Program):
            self.symbol_table.add_error("Root must be a Program node")
            return self.symbol_table
        
        self._gather_type_definitions(ast_root)
        self._process_global_declarations(ast_root)
        self._process_function_declarations(ast_root)
        
        if ast_root.start_platter:
            self.symbol_table.enter_scope("start_platter")
            self._process_platter(ast_root.start_platter)
            self.symbol_table.exit_scope()
        
        self.built = True
        return self.symbol_table
    
    def _gather_type_definitions(self, program: Program):
        """Gather all table type definitions"""
        for decl in program.global_decl:
            if isinstance(decl, TablePrototype):
                self._process_table_prototype(decl)
    
    def _process_table_prototype(self, node: TablePrototype):
        """Process a table type definition"""
        field_types = {}
        for field in node.fields:
            dims = field.dimensions if field.dimensions is not None else 0
            field_type_info = self._create_type_info(field.data_type, dims)
            field_types[field.identifier] = field_type_info
        
        table_type_info = TypeInfo(node.name, 0, field_types)
        
        self.symbol_table.define_symbol(
            node.name,
            SymbolKind.TABLE_TYPE,
            table_type_info,
            node
        )
    
    def _process_global_declarations(self, program: Program):
        """Process global variable declarations"""
        for decl in program.global_decl:
            if isinstance(decl, VarDecl):
                self._process_var_decl(decl)
            elif isinstance(decl, ArrayDecl):
                self._process_array_decl(decl)
            elif isinstance(decl, TableDecl):
                self._process_table_decl(decl)
    
    def _process_function_declarations(self, program: Program):
        """Process function declarations"""
        for recipe in program.recipe_decl:
            self._process_recipe_decl(recipe)
    
    def _process_recipe_decl(self, node: RecipeDecl):
        """Process a function declaration"""
        dims = node.return_dims if node.return_dims is not None else 0
        return_type = self._create_type_info(node.return_type, dims)
        
        func_symbol = Symbol(
            node.name,
            SymbolKind.FUNCTION,
            return_type,
            0,
            node,
            self.symbol_table.current_scope
        )
        
        if not self.symbol_table.current_scope.define(func_symbol):
            self.symbol_table.add_error(f"Recipe '{node.name}' already defined", node)
            return
        
        self.symbol_table.enter_scope(f"recipe_{node.name}")
        self.symbol_table.current_function = func_symbol
        
        for param in node.params:
            self._process_param_decl(param)
        
        if node.body:
            self._process_platter(node.body)
        
        self.symbol_table.current_function = None
        self.symbol_table.exit_scope()
    
    def _process_param_decl(self, node: ParamDecl):
        """Process a function parameter"""
        dims = node.dimensions if node.dimensions is not None else 0
        type_info = self._create_type_info(node.data_type, dims)
        
        self.symbol_table.define_symbol(
            node.identifier,
            SymbolKind.PARAMETER,
            type_info,
            node
        )
    
    def _process_var_decl(self, node: VarDecl):
        """Process a variable declaration"""
        type_info = self._create_type_info(node.data_type, 0)
        
        self.symbol_table.define_symbol(
            node.identifier,
            SymbolKind.VARIABLE,
            type_info,
            node
        )
        
        # Track usage in initial value if present
        if node.init_value:
            self._track_expression_usage(node.init_value)
    
    def _process_array_decl(self, node: ArrayDecl):
        """Process an array declaration"""
        dims = node.dimensions if node.dimensions is not None else 0
        type_info = self._create_type_info(node.data_type, dims)
        
        self.symbol_table.define_symbol(
            node.identifier,
            SymbolKind.VARIABLE,
            type_info,
            node
        )
        
        # Track usage in initial value if present
        if node.init_value:
            self._track_expression_usage(node.init_value)
    
    def _process_table_decl(self, node: TableDecl):
        """Process a table instance declaration"""
        table_type = self.symbol_table.lookup_table_type(node.table_type)
        
        dims = node.dimensions if node.dimensions is not None else 0
        
        if table_type:
            type_info = TypeInfo(
                node.table_type,
                dims,
                table_type.table_fields if dims == 0 else None
            )
            
            if dims > 0:
                type_info.is_table = True
                type_info.table_fields = table_type.table_fields
        else:
            type_info = TypeInfo(node.table_type, dims)
        
        self.symbol_table.define_symbol(
            node.identifier,
            SymbolKind.VARIABLE,
            type_info,
            node
        )
        
        # Track usage in initial value if present
        if node.init_value:
            self._track_expression_usage(node.init_value)
    
    def _process_platter(self, node: Platter):
        """Process a block/compound statement"""
        for decl in node.local_decls:
            if isinstance(decl, VarDecl):
                self._process_var_decl(decl)
            elif isinstance(decl, ArrayDecl):
                self._process_array_decl(decl)
            elif isinstance(decl, TableDecl):
                self._process_table_decl(decl)
        
        for stmt in node.statements:
            self._process_statement(stmt)
    
    def _process_statement(self, node: ASTNode):
        """Process a statement"""
        if isinstance(node, IfStatement):
            self._process_if_statement(node)
        elif isinstance(node, SwitchStatement):
            self._process_switch_statement(node)
        elif isinstance(node, WhileLoop):
            self._process_while_loop(node)
        elif isinstance(node, DoWhileLoop):
            self._process_do_while_loop(node)
        elif isinstance(node, ForLoop):
            self._process_for_loop(node)
        elif isinstance(node, Platter):
            self.symbol_table.enter_scope("block")
            self._process_platter(node)
            self.symbol_table.exit_scope()
        elif isinstance(node, Assignment):
            self._track_expression_usage(node.target)
            self._track_expression_usage(node.value)
        elif isinstance(node, ReturnStatement):
            if node.value:
                self._track_expression_usage(node.value)
        elif isinstance(node, ExpressionStatement):
            self._track_expression_usage(node.expr)
    
    def _process_if_statement(self, node: IfStatement):
        """Process if statement - use Platter syntax: check/alt/instead"""
        # Track condition expression usage
        self._track_expression_usage(node.condition)
        
        self.symbol_table.enter_scope("check")
        self._process_platter(node.then_block)
        self.symbol_table.exit_scope()
        
        for i, (elif_cond, elif_block) in enumerate(node.elif_clauses):
            self._track_expression_usage(elif_cond)
            self.symbol_table.enter_scope("alt")
            self._process_platter(elif_block)
            self.symbol_table.exit_scope()
        
        if node.else_block:
            self.symbol_table.enter_scope("instead")
            self._process_platter(node.else_block)
            self.symbol_table.exit_scope()
    
    def _process_switch_statement(self, node: SwitchStatement):
        """Process switch statement - use Platter syntax: menu/choice"""
        # Track switch expression usage
        self._track_expression_usage(node.expr)
        
        for i, case in enumerate(node.cases):
            self.symbol_table.enter_scope("choice")
            for stmt in case.statements:
                self._process_statement(stmt)
            self.symbol_table.exit_scope()
        
        if node.default:
            self.symbol_table.enter_scope("default")
            for stmt in node.default:
                self._process_statement(stmt)
            self.symbol_table.exit_scope()
    
    def _process_while_loop(self, node: WhileLoop):
        """Process while loop - use Platter syntax: repeat"""
        self.symbol_table.in_loop += 1
        # Track condition expression usage
        self._track_expression_usage(node.condition)
        
        self.symbol_table.enter_scope("repeat")
        self._process_platter(node.body)
        self.symbol_table.exit_scope()
        self.symbol_table.in_loop -= 1
    
    def _process_do_while_loop(self, node: DoWhileLoop):
        """Process do-while loop - use Platter syntax: order_repeat"""
        self.symbol_table.in_loop += 1
        self.symbol_table.enter_scope("order_repeat")
        self._process_platter(node.body)
        self.symbol_table.exit_scope()
        # Track condition expression usage
        self._track_expression_usage(node.condition)
        self.symbol_table.in_loop -= 1
    
    def _process_for_loop(self, node: ForLoop):
        """Process for loop - use Platter syntax: pass"""
        self.symbol_table.in_loop += 1
        
        # Track init, condition, and update expressions
        if node.init:
            if isinstance(node.init, Assignment):
                self._track_expression_usage(node.init.target)
                self._track_expression_usage(node.init.value)
        if node.condition:
            self._track_expression_usage(node.condition)
        if node.update:
            if isinstance(node.update, Assignment):
                self._track_expression_usage(node.update.target)
                self._track_expression_usage(node.update.value)
        
        self.symbol_table.enter_scope("pass")
        self._process_platter(node.body)
        self.symbol_table.exit_scope()
        self.symbol_table.in_loop -= 1
    
    def _create_type_info(self, base_type: str, dimensions: int = 0) -> TypeInfo:
        """Create TypeInfo"""
        dims = dimensions if dimensions is not None else 0
        
        table_type = self.symbol_table.lookup_table_type(base_type)
        if table_type:
            return TypeInfo(base_type, dims, table_type.table_fields)
        
        return TypeInfo(base_type, dims)
    
    def _track_expression_usage(self, expr: ASTNode):
        """Track symbol usage in expressions"""
        if expr is None:
            return
        
        if isinstance(expr, Identifier):
            # Look up the symbol and record usage
            symbol = self.symbol_table.lookup_symbol(expr.name)
            if symbol:  # Find the scope where this symbol is declared
                declared_scope = self._find_declaring_scope(symbol.name)
                if declared_scope:
                    # Record usage with both current scope and declaring scope
                    symbol.add_usage(self.symbol_table.current_scope.name, declared_scope.name)
        
        elif isinstance(expr, BinaryOp):
            self._track_expression_usage(expr.left)
            self._track_expression_usage(expr.right)
        
        elif isinstance(expr, UnaryOp):
            self._track_expression_usage(expr.operand)
        
        elif isinstance(expr, ArrayAccess):
            self._track_expression_usage(expr.array)
            self._track_expression_usage(expr.index)
        
        elif isinstance(expr, TableAccess):
            self._track_expression_usage(expr.table)
        
        elif isinstance(expr, FunctionCall):
            # Track function name usage
            symbol = self.symbol_table.lookup_symbol(expr.name)
            if symbol:
                declared_scope = self._find_declaring_scope(symbol.name)
                if declared_scope:
                    symbol.add_usage(self.symbol_table.current_scope.name, declared_scope.name)
            # Track arguments
            for arg in expr.args:
                self._track_expression_usage(arg)
        
        elif isinstance(expr, CastExpr):
            self._track_expression_usage(expr.expr)
        
        elif isinstance(expr, ArrayLiteral):
            for elem in expr.elements:
                self._track_expression_usage(elem)
        
        elif isinstance(expr, TableLiteral):
            for field_name, value in expr.field_inits:
                self._track_expression_usage(value)
    
    def _find_declaring_scope(self, symbol_name: str) -> Optional[Scope]:
        """Find the scope where a symbol is declared"""
        scope = self.symbol_table.current_scope
        while scope:
            if symbol_name in scope.symbols:
                return scope
            scope = scope.parent
        return None


# Helper Functions
def build_symbol_table(ast_root: Program) -> SymbolTable:
    """Build symbol table from AST"""
    builder = SymbolTableBuilder()
    return builder.build(ast_root)


def print_symbol_table(symbol_table: SymbolTable):
    """Print symbol table in formatted table layout"""
    from app.semantic_analyzer.symbol_table.symbol_table_output import format_symbol_table_compact
    
    print("\n")
    print("╔" + "═" * 78 + "╗")
    print("║" + " " * 25 + "SYMBOL TABLE ANALYSIS" + " " * 32 + "║")
    print("╚" + "═" * 78 + "╝")
    print()
    
    formatted_output = format_symbol_table_compact(symbol_table)
    print(formatted_output)
