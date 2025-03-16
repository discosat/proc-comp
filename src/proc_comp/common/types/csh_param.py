from .param import ParamType

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
    
    def __eq__(self, value):
        if type(self) is not type(value):
            return False

        return self.name == value.name and self.array_idx == value.array_idx
    
    def __hash__(self):
        return hash((self.name, self.array_idx))

class ParamGeneralRegister(ParamRef):
    type_: ParamType
    def __init__(self, type_: ParamType, name: str):
        if not issubclass(type_, ParamType):
            raise ValueError(f"Expected a subclass of ParamType, got {type_}")
        self.type_ = type_
        super().__init__(name)

    def __str__(self):
        return f"({self.type_.__name__}) {self.name}"
    
    def __eq__(self, value):
        return super().__eq__(value) and self.type_ == value.type_
    
    def __hash__(self):
        return hash((super().__hash__(), self.type_))
