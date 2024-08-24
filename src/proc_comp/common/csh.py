from .types import *


class CSH_Command:
    def __repr__(self):
        return self.__str__()
    
    def __str__(self):
        return f"{type(self).__name__}"

    def __node_str__(self):
        return f" [{self.node}]" if self.node else ""

class ParamRef:
    name: str
    array_idx: int|None
    
    def __init__(self, name: str, array_idx: int|None = None):
        self.name = name
        self.array_idx = array_idx
    
    def __repr__(self):
        return self.__str__()
    
    def __str__(self):
        return f"{self.name}" + (f"[{self.array_idx}]" if self.array_idx is not None else "")

class ParamGeneralRegister(ParamRef):
    type_: ParamType
    def __init__(self, type_: type, name: str):
        if not issubclass(type_, ParamType):
            raise ValueError(f"Expected a subclass of ParamType, got {type_}")
        self.type_ = type_
        super().__init__(name)

    def __str__(self):
        return f"({self.type_.__name__}) {self.name}"



# Proc Procedure Management Commands

class ProcNew(CSH_Command):
    pass


class ProcDel(CSH_Command):
    def __init__(self, slot, node=0):
        self.slot = slot
        self.node = node
    
    def __str__(self):
        return super().__str__() + f" {self.slot}" + self.__node_str__()

class ProcPull(CSH_Command):
    def __init__(self, slot, node=0):
        self.slot = slot
        self.node = node
    
    def __str__(self):
        return super().__str__() + f" {self.slot}" + self.__node_str__()

class ProcPush(CSH_Command):
    def __init__(self, slot, node=0):
        self.slot = slot
        self.node = node
    
    def __str__(self):
        return super().__str__() + f" {self.slot}" + self.__node_str__()

class ProcRun(CSH_Command):
    def __init__(self, slot, node=0):
        self.slot = slot
        self.node = node
    
    def __str__(self):
        return super().__str__() + f" {self.slot}" + self.__node_str__()

## Mostly for manual control 
class ProcPop(CSH_Command):
    def __init__(self, instruction_index=None):
        self.idx = instruction_index

class ProcSize(CSH_Command):
    pass

class ProcList(CSH_Command):
    pass

class ProcSlots(CSH_Command):
    def __init__(self, node=0):
        self.node = node
    
    def __str__(self):
        return super().__str__() + self.__node_str__()


# Proc Control-Flow and Arithmetic Operations
"""


    proc block <param a> <op> <param b> [node]: Blocks execution of the procedure until the specified condition is met. <op> can be one of: ==, !=, <, >, <=, >=.

    proc ifelse <param a> <op> <param b> [node]: Skips the next instruction if the condition is not met, and the following instruction if it is met. This command cannot be nested in the default runtime - i.e. it cannot be used again within the following 2 instructions.

    proc noop: Performs no operation. Useful in combination with ifelse instructions.

    proc set <param> <value> [node]: Sets the value of a parameter. The type of value is always inferred from the libparam type of the parameter.

    proc unop <param> <op> <result> [node]: Applies a unary operator to a parameter and stores the result. <op> can be one of: ++, --, !, -, idt, rmt. idt and rmt are both identity operators.

    proc binop <param a> <op> <param b> <result> [node]: Applies a binary operator to parameters <param a> and <param b> and stores the result. <op> can be one of: +, -, *, /, %, <<, >>, &, |, ^.

    proc call <procedure slot> [node]: Inserts an instruction to run the procedure in the specified slot.

"""

class ProcBlock(CSH_Command):
    __match_args__ = ('a', 'op', 'b', 'node')
    def __init__(self, a, op:ComparisonOp, b, node=0):
        self.a = a
        self.op = op
        self.b = b
        self.node = node
    
    def __str__(self):
        return super().__str__() + f" {self.a} {self.op} {self.b}" + self.__node_str__()

class ProcIfElse(CSH_Command):
    __match_args__ = ('a', 'op', 'b', 'node')
    def __init__(self, a, op:ComparisonOp , b, node=0):
        self.a = a
        self.op = op
        self.b = b
        self.node = node
    
    def __str__(self):
        return super().__str__() + f" {self.a} {self.op} {self.b}" + self.__node_str__()

class ProcNoop(CSH_Command):
    pass

class ProcSet(CSH_Command):
    __match_args__ = ('param', 'value', 'node')
    def __init__(self, param:ParamRef, value, node=0):
        self.param = param
        self.value = value
        self.node = node
    
    def __str__(self):
        return super().__str__() + f" {self.param} {self.value}" + self.__node_str__()

class ProcUnop(CSH_Command):
    __match_args__ = ('param', 'op', 'result', 'node')
    def __init__(self, param:ParamRef, op:UnaryOp, result:ParamRef, node=0):
        self.param = param
        self.op = op
        self.result = result
        self.node = node
    
    def __str__(self):
        return super().__str__() + f" {self.param} {self.op} {self.result}" + self.__node_str__()

class ProcBinop(CSH_Command):
    __match_args__ = ('a', 'op', 'b', 'result', 'node')
    def __init__(self, a:ParamRef, op:BinaryOp, b:ParamRef, result:ParamRef, node=0):
        self.a = a
        self.op = op
        self.b = b
        self.result = result
        self.node = node
    
    def __str__(self):
        return super().__str__() + f" {self.a} {self.op} {self.b} {self.result}" + self.__node_str__()

class ProcCall(CSH_Command):
    __match_args__ = ('slot', 'node')
    def __init__(self, slot, node=0):
        self.slot = slot
        self.node = node
    
    def __str__(self):
        return super().__str__() + f" {self.slot}" + self.__node_str__()