from proc_comp.common.types.csh_param import ParamRef
from proc_comp.common.types.operator import OperandType
from proc_comp.common.types.param import ParamType, UInt32, Int64, String, Double64

class Expression:
    def __repr__(self):
        return self.__str__()
    
    def __str__(self):
        return f"{type(self).__name__}()"

    def __pprint__(self, depth=0):
        return [(depth, self.__str__())]
    
    def pprint(self, depth=0, indent=2):
        lines = []
        for d, s in self.__pprint__(depth):
            lines.append(" " * indent * d + s)

        return "\n".join(lines)


class ParamExp(Expression):
    def __init__(self, val: ParamType):
        self.val: ParamType = val
    
    def __str__(self):
        return f"ParamExp({self.val})"


class NoopExp(Expression):
    pass


class SeqExp(Expression):
    def __init__(self, exps):
        self.exps = exps

    def __str__(self):
        return f"SeqExp({self.exps})"

    def __pprint__(self, depth=0):
        lines = [(depth, "SeqExp([")]
        for x in self.exps:
            lines += x.__pprint__(depth+1)
        lines.append((depth, "])"))

        return lines

class IfElseExp(Expression):
    def __init__(self, a, op, b, then, else_):
        self.a = a
        self.b = b
        self.op = op
        self.then = then
        self.else_ = else_
        
        self.cond = f"{self.a} {self.op} {self.b}"
    
    def __str__(self):
        return f"IfElseExp({self.cond}, {self.then}, {self.else_})"

    def __pprint__(self, depth=0):
        lines = [(depth, f"IfElseExp({self.cond}")]
        lines += self.then.__pprint__(depth+1)
        lines += self.else_.__pprint__(depth+1)
        lines.append((depth, ")"))
        return lines


class WaitTimeExp(Expression):
    time: UInt32
    def __init__(self, time: UInt32):
        self.time = time
    
    def __str__(self):
        return f"WaitTimeExp({self.time})"

class RepeatExp(Expression):
    count: UInt32
    exp: Expression
    def __init__(self, count: UInt32, exp: Expression):
        self.count = count
        self.exp = exp
    
    def __str__(self):
        return f"RepeatExp({self.count}, {self.exp})"

    def __pprint__(self, depth=0):
        lines = [(depth, f"RepeatExp({self.count}, [")]
        self.exp.pprint(depth+1)
        lines.append((depth, "])"))

        return lines


class ProcSetExp(Expression):
    param: ParamRef
    value: ParamType
    def __init__(self, param, value: ParamType):
        self.param = param
        self.value = value
    
    def __str__(self):
        return f"ProcSetExp({self.param}, {self.value})"

class ProcBinopExp(Expression):
    left: ParamRef
    right: ParamRef
    result: ParamRef
    operator: OperandType

    def __init__(self, left, right, result, operator):
        self.left = left
        self.right = right
        self.result = result
        self.operator = operator
    
    def __str__(self):
        return f"ProcBinopExp({self.result} = {self.left} {self.operator} {self.right})"
class ProcUnopExp(Expression):
    value: ParamRef
    result: ParamRef
    operator: OperandType

    def __init__(self, value, result, operator):
        self.value = value
        self.result = result
        self.operator = operator
    
    def __str__(self):
        return f"ProcUnopExp({self.result} = {self.operator} {self.value})"

class ProcCaptureImages(Expression):
    """
    Args:
        cameraID (String): The model of the camera to capture with.
        cameraType (String): The camera type to capture with.
        exposure (int): Exposure in microseconds.
        iso (float): ISO or gain.
        numOfImages (int): Number of images to capture.
        interval (int): Delay between images in microseconds (excluding exposure).
    """
    cameraID: String
    cameraType: String
    exposure: Int64
    iso: Double64
    numOfImages: Int64
    interval: Int64

    def __init__(self, cameraID: String, cameraType: String, exposure: Int64, iso: Double64, numOfImages: Int64, interval: Int64):
        self.cameraID = cameraID
        self.cameraType = cameraType
        self.exposure = exposure
        self.iso = iso
        self.numOfImages = numOfImages
        self.interval = interval

    def __str__(self):
        return f"ProcCaptureImages({self.cameraID}, {self.cameraType}, {self.exposure}, {self.iso}, {self.numOfImages}, {self.interval})"


class RawCSH(Expression):
    commands: list[str]
    def __init__(self, commands: list[str]):
        self.commands = commands
    
    def __str__(self):
        return f'RawCSH([{"; ".join(self.commands)}])'
    
    def __pprint__(self, depth=0):
        lines = [(depth, "RawCSH([")]
        for x in self.commands:
            lines.append((depth+1, x))
        lines.append((depth, "])"))

        return lines