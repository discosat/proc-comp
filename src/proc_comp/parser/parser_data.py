from dataclasses import dataclass, field
from typing import Any, Callable

from ..common.types.expression import *
from ..common.types.param import *
from .parser_aux import *


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
    'node_param': {
        'name': 'string',
        'array_idx': 'uint',
    },
    'variable_param': {
        'variable_name': 'string',
        'type': 'csh_param_type'
    },
    'csh_param_type': [
        list(type_map.keys())
    ],
    'comparator': [
        list(comparator_map.keys())
    ],
    'unop': [
        list(unop_map.keys())
    ],
    'binop': [
        list(binop_map.keys())
    ]
}


expression_map: dict[str, ExpressionMapItem] = {
    # General CSH/Proc expressions
    'commands': ExpressionMapItem(
        [ ExpAttr('body', '[expression]') ],
        lambda parse,obj: SeqExp([parse(x) for x in obj.get('body',[])]),
        description='A list of expressions to be executed sequentially'
    ),

    'if': ExpressionMapItem(
        [ ExpAttr('cond', 'conditional')
        , ExpAttr('then', 'expression')
        ],
        lambda parse, obj: IfElseExp(*parse_conditional(obj['cond']), parse(obj['then']), NoopExp()),
        description='Do something only if the condition is true'
    ),
    'ifelse': ExpressionMapItem(
        [ ExpAttr('cond', 'conditional')
        , ExpAttr('then', 'expression')
        , ExpAttr('else', 'expression')
        ],
        lambda parse, obj: IfElseExp(*parse_conditional(obj['cond']), parse(obj['then']), parse(obj['else'])),
        description='Do one thing if the condition evaluates as true, and another if it is false'
    ),
    'set-param': ExpressionMapItem(
        [ ExpAttr('param', 'parameter')
        , ExpAttr('type', 'csh_param_type')
        , ExpAttr('value', '@type')
        ],
        lambda _, obj: ProcSetExp(parse_param(obj.get('param')), type_map.get(obj.get('type'))(value=obj.get('value')))
    ),
    'binop': ExpressionMapItem(
        [ ExpAttr('left', 'parameter')
        , ExpAttr('operator', 'binop')
        , ExpAttr('right', 'parameter')
        , ExpAttr('result', 'parameter')
        ],
        lambda _, obj: ProcBinopExp(parse_param(obj.get('left')), parse_param(obj.get('right')), parse_param(obj.get('result')), binop_map.get(obj.get('operator'))()),
        description='Do a binary operation on the "left" and "right" parameters. The result of the operation is stored in the "result" parameter.'
    ),
    'unop': ExpressionMapItem(
        [ ExpAttr('value', 'parameter')
        , ExpAttr('operator', 'binop')
        , ExpAttr('result', 'parameter')
        ],
        lambda _, obj: ProcUnopExp(parse_param(obj.get('value')), parse_param(obj.get('result')), unop_map.get(obj.get('operator'))()),
        description='Do a unary operation on the "value" parameter. The result of the operation is stored in the "result" parameter.'

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
                ProcSetExp(ParamRef("gpio_mode",obj['pin']), UInt8(1)),
                ProcSetExp(ParamRef("gpio_value",obj['pin']), UInt8(obj['value']))
            ])
    )
}

