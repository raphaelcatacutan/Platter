"""
Interpreter Package for Platter Language

This package provides the TAC interpreter for executing optimized
Three Address Code (TAC) instructions directly in Python.

Modules:
- ir_interpreter: TAC interpreter and convenience runner
"""

from .ir_interpreter import TACInterpreter, run_tac

__all__ = [
    'TACInterpreter',
    'run_tac',
]

__version__ = '1.0.0'
