from ..common.types import *


def parse(obj):
    #print(obj)
    match obj['name']:
        case 'commands':
            return SeqExp([parse(x) for x in obj['body']])
        case 'if':
            return IfElseExp(parse(obj['cond']), parse(obj['then']), NoopExp)
        case 'ifelse':
            return IfElseExp(parse(obj['cond']), parse(obj['then']), parse(obj['else']))
        case 'wait-sec':
            return WaitTimeExp(UInt32(obj['duration']))
        case 'repeat-n':
            return RepeatExp(UInt32(obj['count']), [parse(x) for x in obj['body']])
        case 'gpio-write':
            return SeqExp([
                ProcSetExp(f"gpio_mode[{obj['pin']}]", UInt8(1)),
                ProcSetExp(f"gpio_value[{obj['pin']}]", UInt8(obj['value']))
            ])
        case _:
            raise ValueError(f"Unknown expression: {obj['name']}")
