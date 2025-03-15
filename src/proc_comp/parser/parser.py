from dataclasses import dataclass, field
from typing import Callable, Any
from ..common.types import *

@dataclass
class ExpAttr:
    name: str
    type: str
    default: Any | None = None
    required: bool = True
    attributes: dict = field(default_factory=dict)
    description: str | None = None


@dataclass
class ExpressionMapItem:
    attributes: list[ExpAttr]
    expression: Callable[[Callable, dict], Expression]
    description: str | None = None


types = {
    'expression': {
        'name': 'string'
    },
    'conditional': {
        'left': 'parameter',
        'operator': 'comparator',
        'right': 'parameter'
    },
    'parameter': [
        'node_param',
        'variable_param'
    ],
    'variable_param': {
        'name': 'string',
        'type': 'csh_param_type'
    },
    'csh_param_type': [
        'Int8', 'Int16', 'Int32', 'Int64',
        'UInt8', 'UInt16', 'UInt32', 'UInt64',
        'Float32', 'Double64',
        'String'
    ],
    'comparator': [
        'Eq', 'Neq', 'Lt', 'Lte', 'Gt', 'Gte',
    ],
    'unop': [
        'Increment', 'Decrement', 'Negation', 'Not', 'IdentLocal', 'IdentRemote'
    ],
    'binop': [
        'Add', 'Sub', 'Mul', 'Div', 'Mod', 'LShift', 'RShift', 'BitAnd', 'BitOr', 'BitXOr'
    ]
}


expression_map: dict[str, ExpressionMapItem] = {
    # General CSH/Proc expressions
    'commands': ExpressionMapItem(
        [ ExpAttr('body', '[expression]') ],
        lambda parse,obj: SeqExp([parse(x) for x in obj.get('body',[])]),
        description='A list of expressions to be executed sequentially'
    ),

    #TODO: Wrong input is passed to IfElseExp. Needs to be (param_a,comparison_operator,param_b,then,else)
    'if': ExpressionMapItem(
        [ ExpAttr('cond', 'conditional')
        , ExpAttr('then', 'expression')
        ],
        lambda parse, obj: IfElseExp(parse(obj['cond']), parse(obj['then']), NoopExp()),
        description='Do something only if the condition is true'
    ),
    'ifelse': ExpressionMapItem(
        [ ExpAttr('cond', 'conditional')
        , ExpAttr('then', 'expression')
        , ExpAttr('else', 'expression')
        ],
        lambda parse, obj: IfElseExp(parse(obj['cond']), parse(obj['then']), parse(obj['else'])),
        description='Do one thing if the condition evaluates as true, and another if it is false'
    ),
    'wait-sec': ExpressionMapItem(
        [ ExpAttr('duration', 'uint') ],
        lambda _,obj: WaitTimeExp(UInt32(obj['duration'])),
        description='Pause execution of the flight plan for a given duration, in seconds'
    ),
    'repeat-n': ExpressionMapItem(
        [ ExpAttr('count', 'uint')
        , ExpAttr('body', 'expression')
        ],
        lambda parse,obj: RepeatExp(UInt32(obj['count']), parse(obj['body'])),
        description='Repeat the expression a given number of times'
    ),
    'raw': ExpressionMapItem(
        [ ExpAttr('body', '[string]') ],
        lambda _,obj: RawCSH(obj.get('commands', [])),
        description='Manually write CSH commands to be executed. Only use if you know what you are doing.\n\nWith great power comes great responsibility!'
    ),

    # DISCO-2 specific
    'capture_image': ExpressionMapItem(
        [ ExpAttr('cameraID', 'string')
        , ExpAttr('cameraType', 'string')
        , ExpAttr('exposure', 'uint', required=False)
        , ExpAttr('iso', 'uint', required=False)
        , ExpAttr('numOfImages', 'uint', 1, False)
        , ExpAttr('interval', 'uint', 10, False)
        ],
        lambda _,obj: ProcCaptureImages(
                    String(obj['cameraID']),
                    String(obj['cameraType']),
                    Int64(obj['exposure']),
                    Double64(obj['iso']),
                    Int64(obj['numOfImages']),
                    Int64(obj['interval'])
                )
    ),

    # Raspberry Pi test expressions
    'gpio-write': ExpressionMapItem(
        [ ExpAttr('pin', 'uint', attributes={'min':0, 'max':31})
        , ExpAttr('value', 'uint', attributes={'min': 0, 'max': 1})
        ],
        lambda _, obj: SeqExp([
                ProcSetExp(f"gpio_mode[{obj['pin']}]", UInt8(1)),
                ProcSetExp(f"gpio_value[{obj['pin']}]", UInt8(obj['value']))
            ])
    )
}


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