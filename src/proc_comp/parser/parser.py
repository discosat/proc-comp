from ..common.types.expression import Expression
from .parser_data import expression_map
from .parser_aux import type_map, comparator_map, binop_map, unop_map


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

    missing_attributes = set()
    for attr in  expr.attributes:
        if attr.name not in obj and attr.required:
            missing_attributes.add(attr.name)
    
    if len(missing_attributes) > 0:
        raise Exception(f'Missing attributes in "{name}": {", ".join(missing_attributes)}')

    
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

def json_schema():
    # Build the $defs dictionary in steps to avoid mixing comprehensions and static entries
    defs = {}

    # Add expression_map definitions
    for k, v in expression_map.items():
        defs[k] = {
            "type": "object",
            "properties": {
                a.name: {"$ref": "#/$defs/" + (a.type if not a.type.startswith("[") and not a.type.endswith("]") else (a.type.removeprefix("[").removesuffix("]") + "array"))}
                for a in v.attributes
            },
            "required": [
                a.name
                for a in v.attributes
                if a.required
            ]
        }

    # Add type_map definitions
    for k, v in type_map.items():
        if k.startswith("Int") or k.startswith("UInt"):
            type_value = "integer"
        elif k == "String":
            type_value = "string"
        else:
            type_value = "number"
        entry = {
            "type": type_value
        }
        if hasattr(v, "min_val"):
            entry["minimum"] = v.min_val
        if hasattr(v, "max_val"):
            entry["maximum"] = v.max_val
        defs[k] = entry

    # Add parameter definitions
    defs["parameter"] = {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "array_idx": {"type": "integer"},
            "_type": {"$ref": "#/$defs/csh_param_type"},
            "variable_name": {"type": "string"}
        },
        "anyOf": [
            {
                "required": ["name", "array_idx"]
            },
            {
                "required": ["variable_name", "_type"]
            }
        ]
    }

    # Add static enum definitions
    defs["csh_param_type"] = {
        "enum": list(type_map.keys())
    }
    defs["unary_operator"] = {
        "enum": list(unop_map.keys())
    }
    defs["binary_operator"] = {
        "enum": list(binop_map.keys())
    }
    defs["comparison_operator"] = {
        "enum": list(comparator_map.keys())
    }

    defs["expression"] = {
        "anyOf": [
            {"$ref": "#/$defs/" + k}
            for k in expression_map.keys()
        ]
    }


    #TODO: Should probaly find some way to make this more generic
    defs["expressionarray"] = {
        "type": "array",
        "items": {
            "$ref": "#/$defs/expression"
        }
    }

    defs["stringarray"] = {
        "type": "array",
        "items": {
            "type": "string"
        }
    }

    defs["conditional"] = {
        "type": "object",
        "properties": {
            "left": {"$ref": "#/$defs/parameter"},
            "operator": {"$ref": "#/$defs/comparison_operator"},
            "right": {"$ref": "#/$defs/parameter"}
        },
        "required": ["left", "operator", "right"]
    }

    defs["@type"] = {
        "type": ["string","number"],
    }

    return {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "$defs": defs,
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "pattern": "^commands"
            },
            "body": {
            "$ref": "#/$defs/expressionarray"
            }
        }

    }

