class Expression:
    def __repr__(self):
        return self.__str__()
    
    def __str__(self):
        return "Expression()"

    def __pprint__(self, depth=0):
        return [(depth, self.__str__())]
    
    def pprint(self, depth=0, indent=2):
        lines = []
        for d, s in self.__pprint__(depth):
            lines.append(" " * indent * d + s)

        return "\n".join(lines)



class ValExp(Expression):
    def __init__(self, val):
        self.val = val
    
    def __str__(self):
        return f"ValExp({self.val})"


class NoopExp(Expression):
    def __str__(self):
        return "NoopExp()"


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
    def __init__(self, cond, then, else_):
        self.cond = cond
        self.then = then
        self.else_ = else_
    
    def __str__(self):
        return f"IfElseExp({self.cond}, {self.then}, {self.else_})"

    def __pprint__(self, depth=0):
        return [
            (depth, f"IfElseExp({self.cond}"),
            self.then.__pprint__(depth+1),
            self.else_.__pprint__(depth+1),
            (depth, ")")
        ]

class WaitTimeExp(Expression):
    def __init__(self, time):
        self.time = time
    
    def __str__(self):
        return f"WaitTimeExp({self.time})"

class RepeatExp(Expression):
    def __init__(self, count, exps):
        self.count = count
        self.exps = exps
    
    def __str__(self):
        return f"RepeatExp({self.count}, {self.exps})"

    def __pprint__(self, depth=0):
        lines = [(depth, f"RepeatExp({self.count}, [")]
        for x in self.exps:
            lines += x.__pprint__(depth+1)
        lines.append((depth, "])"))

        return lines


class ProcSetExp(Expression):
    def __init__(self, name, value):
        self.name = name
        self.value = value
    
    def __str__(self):
        return f"ProcSetExp({self.name}, {self.value})"