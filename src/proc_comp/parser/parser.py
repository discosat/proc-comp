from ..common.types.expression import Expression
from .parser_data import expression_map


def parse(obj: dict) -> Expression:
    """Parse an object describing a satellite procedure. Is recursive.

    Args:
        obj (dict): A dictionary describing a satellite procedure. 

    Raises:
        ValueError: The given expression is not recognized

    Returns:
        Expression: An abstract representation of the procedure expression
    """
    #print(obj)

    name = obj.get('name')
    if name is None:
        raise Exception(f'Unable to parse "{obj}". Missing "name".')
    
    expr = expression_map.get(name)
    if expr is None:
        raise Exception(f'Unsupported expression block "{name}".')
    
    return expr.expression(parse, obj)


def discover():
    return {
        k: {
            'fields': [
                a.__dict__
                for a in v.attributes
            ],
            'description': v.description
        }
        for k,v in expression_map.items()
    }