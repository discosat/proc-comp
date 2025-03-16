class ParamType:
    value = None
    type_name = None
    register_name = None
    num_registers = 0
    def __init__(self, value) -> None:
        self.value = value
        
    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"({self.type_name}) {self.value}"

class IntParamType(ParamType):
    min_val = None
    max_val = None
    
    def __init__(self, value):
        if self.min_val is not None and value < self.min_val:
            raise ValueError(f"Value {value} is less than minimum value {self.min_val}")
        if self.max_val is not None and value > self.max_val:
            raise ValueError(f"Value {value} is greater than maximum value {self.max_val}")

        super().__init__(value)

class Int8(IntParamType):
    min_val = -128
    max_val =  127
    type_name = "I8"
    register_name = "_p_int8"
    num_registers = 32

class Int16(IntParamType):
    min_val = -32_768
    max_val =  32_767
    type_name = "I16"
    register_name = "_p_int16"
    num_registers = 32

class Int32(IntParamType):
    min_val = -2_147_483_648
    max_val =  2_147_483_647
    type_name = "I32"
    register_name = "_p_int32"
    num_registers = 32

class Int64(IntParamType):
    min_val = -9_223_372_036_854_775_808
    max_val =  9_223_372_036_854_775_807
    type_name = "I64"
    register_name = "_p_int64"
    num_registers = 32

class UInt8(IntParamType):
    min_val = 0
    max_val = 255
    type_name = "U8"
    register_name = "_p_uint8"
    num_registers = 32

class UInt16(IntParamType):
    min_val = 0
    max_val = 65_535
    type_name = "U16"
    register_name = "_p_uint16"
    num_registers = 32

class UInt32(IntParamType):
    min_val = 0
    max_val = 4_294_967_295
    type_name = "U32"
    register_name = "_p_uint32"
    num_registers = 32

class UInt64(IntParamType):
    min_val = 0
    max_val = 18_446_744_073_709_551_615
    type_name = "U64"
    register_name = "_p_uint64"
    num_registers = 32

class Float32(ParamType):
    type_name = "Float"
    register_name = "_p_float"
    num_registers = 32

class Double64(ParamType):
    type_name = "Double"
    register_name = "_p_double"
    num_registers = 16

class String(ParamType):
    type_name = "String"
    register_name = "_p_string"
    num_registers = 32