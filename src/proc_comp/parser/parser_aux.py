from ..common.types.param import *
from ..common.types.csh_param import *
from ..common.types.operator import *


type_map = {
    'Int8': Int8, 
    'Int16': Int16, 
    'Int32': Int32, 
    'Int64': Int64,
    'UInt8': UInt8, 
    'UInt16': UInt16, 
    'UInt32': UInt32, 
    'UInt64': UInt64,
    'Float32': Float32, 
    'Double64': Double64,
    'String': String
}

comparator_map = {
    'Eq': EqOp, 
    'Neq': NeqOp, 
    'Lt': LtOp, 
    'Lte': LteOp, 
    'Gt': GtOp, 
    'Gte': GteOp
}

def parse_param(obj:dict) -> ParamRef:
    if 'name' in obj:
        return ParamRef(obj.get('name'), obj.get('array_idx'))

    elif all([x in obj for x in ['variable_name', 'type']]):
        return ParamGeneralRegister(type_map.get(obj.get('type')), obj.get('variable_name'))

    else:
        raise Exception(f'Could not parse "{obj}" as parameter')

def parse_conditional(obj:dict) -> tuple[ParamRef, ComparisonOp, ParamRef]:
    lhs = obj.get('left')
    op = obj.get('operator')
    rhs = obj.get('right')
    
    if any([x is None for x in [lhs, op, rhs]]):
        raise Exception(f'Incomplete conditional: {obj}')
    
    return (
        parse_param(lhs),
        comparator_map.get(op)(),
        parse_param(rhs)
    )
    