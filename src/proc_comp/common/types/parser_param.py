from .param import ParamType

class ParserParam:
    name: str
    idx: int|None
    type: ParamType
    is_variable: bool

    def __init__(self, type:ParamType, name:str, idx:int|None=None, is_variable:bool=False):
        self.type = type
        self.name = name
        self.idx = idx
        self.is_variable = is_variable


