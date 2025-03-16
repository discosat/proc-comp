from .types import ParamType

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
    def __init__(self, type_: ParamType, name: str):
        if not issubclass(type_, ParamType):
            raise ValueError(f"Expected a subclass of ParamType, got {type_}")
        self.type_ = type_
        super().__init__(name)

    def __str__(self):
        return f"({self.type_.__name__}) {self.name}"