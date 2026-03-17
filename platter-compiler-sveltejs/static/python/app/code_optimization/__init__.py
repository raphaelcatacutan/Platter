"""
Code Optimization Package for Platter Language

This package provides optimization passes for intermediate representation (IR)
including constant folding, propagation, dead code elimination,
algebraic simplification, and strength reduction.

Modules:
- optimizer: Base optimization infrastructure (OptimizationPass, BasicBlock, CFG)
- constant_folding: Constant folding optimization pass
- propagation: Constant and copy propagation passes
- dead_code_elimination: Dead code elimination passes
- algebraic_simplification: Algebraic simplification and strength reduction
- optimizer_manager: Manages and coordinates optimization passes
"""

from .optimizer import OptimizationPass, BasicBlock, ControlFlowGraph
from .constant_folding import ConstantFoldingPass
from .propagation import ConstantPropagationPass, CopyPropagationPass
from .dead_code_elimination import DeadCodeEliminationPass, UnreachableCodeEliminationPass
from .algebraic_simplification import AlgebraicSimplificationPass, StrengthReductionPass
from .optimizer_manager import OptimizerManager, OptimizationLevel, optimize_ir

__all__ = [
    # Optimization Base
    'OptimizationPass',
    'BasicBlock',
    'ControlFlowGraph',
    
    # Optimization Passes
    'ConstantFoldingPass',
    'ConstantPropagationPass',
    'CopyPropagationPass',
    'DeadCodeEliminationPass',
    'UnreachableCodeEliminationPass',
    'AlgebraicSimplificationPass',
    'StrengthReductionPass',
    
    # Optimizer Manager
    'OptimizerManager',
    'OptimizationLevel',
    'optimize_ir',
]

__version__ = '1.0.0'
