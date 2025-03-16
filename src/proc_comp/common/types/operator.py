class OperandType:
    def __repr__(self):
        return self.__str__()
    
    def __str__(self):
        return f"{type(self).__name__}"

class ComparisonOp(OperandType):
    pass

class EqOp(ComparisonOp):
    def __str__(self):
        return "=="

class NeqOp(ComparisonOp):
    def __str__(self):
        return "!="
    
class LtOp(ComparisonOp):
    def __str__(self):
        return "<"

class GtOp(ComparisonOp):
    def __str__(self):
        return ">"

class LteOp(ComparisonOp):
    def __str__(self):
        return "<="

class GteOp(ComparisonOp):
    def __str__(self):
        return ">="

class BinaryOp(OperandType):
    pass

class AddOp(BinaryOp):
    def __str__(self):
        return "+"
    
class SubOp(BinaryOp):
    def __str__(self):
        return "-"

class MulOp(BinaryOp):
    def __str__(self):
        return "*"

class DivOp(BinaryOp):
    def __str__(self):
        return "/"
    
class ModOp(BinaryOp):
    def __str__(self):
        return "%"

class LshiftOp(BinaryOp):
    def __str__(self):
        return "<<"

class RshiftOp(BinaryOp):
    def __str__(self):
        return ">>"

class BitAndOp(BinaryOp):
    def __str__(self):
        return "&"

class BitOrOp(BinaryOp):
    def __str__(self):
        return "|"

class BitXorOp(BinaryOp):
    def __str__(self):
        return "^"

class UnaryOp(OperandType):
    pass

class IncrOp(UnaryOp):
    def __str__(self):
        return "++"

class DecrOp(UnaryOp):
    def __str__(self):
        return "--"

class NegOp(UnaryOp):
    def __str__(self):
        return "-"

class NotOp(UnaryOp):
    def __str__(self):
        return "!"

class IdentLocalOp(UnaryOp):
    def __str__(self):
        return "idt"

class IdentRemoteOp(UnaryOp):
    def __str__(self):
        return "rmt"