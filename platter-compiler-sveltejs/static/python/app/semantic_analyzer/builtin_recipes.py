"""
Built-in Recipes (Functions) for Platter Language
Defines type signatures and spice (parameter) specifications for all built-in recipes
"""

from app.semantic_analyzer.symbol_table.types import TypeInfo
from typing import List, Tuple


class BuiltinRecipeSignature:
    """Represents a built-in recipe's type signature"""
    
    def __init__(self, name: str, return_type: str, return_dims: int, 
                 spices: List[Tuple[str, int]], description: str = ""):
        """
        Initialize a built-in recipe signature
        
        Args:
            name: Recipe name
            return_type: Return type (piece, sip, chars, flag, void)
            return_dims: Number of array dimensions for return type
            spices: List of (type, dimensions) tuples for each spice (parameter)
            description: Description of what the recipe does
        """
        self.name = name
        self.return_type = return_type
        self.return_dims = return_dims
        self.spices = spices  # List of (type_name, dimensions) tuples
        self.description = description
    
    def get_return_type_info(self) -> TypeInfo:
        """Get TypeInfo for the return type"""
        return TypeInfo(self.return_type, self.return_dims)
    
    def get_spice_type_info(self, index: int) -> TypeInfo:
        """Get TypeInfo for a specific spice (parameter)"""
        if 0 <= index < len(self.spices):
            type_name, dims = self.spices[index]
            return TypeInfo(type_name, dims)
        return None
    
    def get_spice_count(self) -> int:
        """Get the number of spices (parameters)"""
        return len(self.spices)
    
    def __repr__(self):
        return f"BuiltinRecipe({self.name}: {self.return_type}, {len(self.spices)} spices)"


# Built-in recipe definitions
# Format: (name, return_type, return_dims, [(spice_type, spice_dims), ...], description)
BUILTIN_RECIPES = {
    # Type conversion recipes
    "topiece": BuiltinRecipeSignature(
        "topiece", "piece", 0, 
        [("chars", 0)],  # Accepts chars, sip, or flag (any scalar)
        "Convert to piece (integer)"
    ),
    
    "tosip": BuiltinRecipeSignature(
        "tosip", "sip", 0,
        [("chars", 0)],  # Accepts piece, chars, or flag (any scalar)
        "Convert to sip (float)"
    ),
    
    "tochars": BuiltinRecipeSignature(
        "tochars", "chars", 0,
        [("chars", 0)],  # Accepts any scalar type
        "Convert to chars (string)"
    ),
    
    # Array manipulation recipes
    "append": BuiltinRecipeSignature(
        "append", "void", 0,
        [("chars", 1), ("chars", 0)],  # (array, element) - accepts any array type
        "Append element to end of array"
    ),
    
    "remove": BuiltinRecipeSignature(
        "remove", "chars", 0,  # Returns the removed element
        [("chars", 1), ("piece", 0)],  # (array, index)
        "Remove and return element at index from array"
    ),
    
    "size": BuiltinRecipeSignature(
        "size", "piece", 0,
        [("chars", 1)],  # Accepts any array
        "Get the size (length) of an array"
    ),
    
    "copy": BuiltinRecipeSignature(
        "copy", "chars", 1,
        [("chars", 1)],  # Accepts any array, returns same type
        "Create a copy of an array"
    ),
    
    "reverse": BuiltinRecipeSignature(
        "reverse", "void", 0,
        [("chars", 1)],  # Modifies array in place
        "Reverse an array in place"
    ),
    
    "sort": BuiltinRecipeSignature(
        "sort", "void", 0,
        [("chars", 1)],  # Modifies array in place
        "Sort an array in place"
    ),
    
    "order": BuiltinRecipeSignature(
        "order", "void", 0,
        [("chars", 1)],  # Modifies array in place (alias for sort)
        "Order (sort) an array in place"
    ),
    
    # String manipulation recipes
    "cut": BuiltinRecipeSignature(
        "cut", "chars", 0,
        [("chars", 0), ("piece", 0), ("piece", 0)],  # (string, start, end)
        "Extract substring from start to end index"
    ),
    
    "search": BuiltinRecipeSignature(
        "search", "piece", 0,
        [("chars", 0), ("chars", 0)],  # (haystack, needle)
        "Search for substring, return index or -1"
    ),
    
    "matches": BuiltinRecipeSignature(
        "matches", "flag", 0,
        [("chars", 0), ("chars", 0)],  # (string, pattern)
        "Check if string matches pattern"
    ),
    
    # Math recipes
    "sqrt": BuiltinRecipeSignature(
        "sqrt", "sip", 0,
        [("sip", 0)],  # Accepts piece or sip
        "Calculate square root"
    ),
    
    "pow": BuiltinRecipeSignature(
        "pow", "sip", 0,
        [("sip", 0), ("sip", 0)],  # (base, exponent)
        "Calculate power (base^exponent)"
    ),
    
    "fact": BuiltinRecipeSignature(
        "fact", "piece", 0,
        [("piece", 0)],
        "Calculate factorial (piece only)"
    ),
    
    # Random number generation
    "rand": BuiltinRecipeSignature(
        "rand", "piece", 0,
        [("piece", 0), ("piece", 0)],  # (min, max)
        "Generate random piece (integer) between min and max (inclusive)"
    ),
}


def get_builtin_recipe(name: str) -> BuiltinRecipeSignature:
    """
    Get a built-in recipe signature by name
    
    Args:
        name: Recipe name
    
    Returns:
        BuiltinRecipeSignature if found, None otherwise
    """
    return BUILTIN_RECIPES.get(name)


def is_builtin_recipe(name: str) -> bool:
    """
    Check if a name is a built-in recipe
    
    Args:
        name: Recipe name to check
    
    Returns:
        True if it's a built-in recipe, False otherwise
    """
    return name in BUILTIN_RECIPES


def get_all_builtin_recipe_names() -> List[str]:
    """Get list of all built-in recipe names"""
    return list(BUILTIN_RECIPES.keys())
