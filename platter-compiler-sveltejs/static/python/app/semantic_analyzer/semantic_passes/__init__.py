"""
Semantic Analysis Passes for Platter Language
"""

from .error_handler import (
    SemanticError,
    SemanticErrorHandler,
    ErrorSeverity,
    ErrorCodes
)

from .type_checker import TypeChecker
from .scope_checker import ScopeChecker
from .control_flow_checker import ControlFlowChecker
from .function_checker import FunctionChecker

__all__ = [
    'SemanticError',
    'SemanticErrorHandler',
    'ErrorSeverity',
    'ErrorCodes',
    'TypeChecker',
    'ScopeChecker',
    'ControlFlowChecker',
    'FunctionChecker'
]
