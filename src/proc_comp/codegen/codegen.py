from ..common.types import *
from ..common import csh
from ..common.cfgbuilder import ControlFlowGraph


class CodeGen:
    cfg = ControlFlowGraph()
    procedures: dict[str, list[csh.CSH_Command]]
    main: list[csh.CSH_Command]
    
    procs: int = 0
    params: dict[type, int] = {}
    
    def __init__(self) -> None:
        self.main = []
        self.procedures = {}
    
    def _next_proc_id(self):
        self.procs += 1
        return f"proc${self.procs}"

    def _next_param_id(self, type_: type):
        if type_ not in self.params:
            self.params[type_] = 0
        
        self.params[type_] += 1
        return f"param${type_.type_name}${self.params[type_]}"
    
    def _next_param(self, type_: type):
        return csh.ParamGeneralRegister(type_, self._next_param_id(type_))
    
    def _sub_proc(self, exps: list[Expression]):
        body = []
        for x in exps:
            self._code_gen(x, body)
        
        id = self._next_proc_id()
        self.procedures[id] = body
        
        return id

    def _code_gen(self, exp: Expression, procedure: list[csh.CSH_Command]):
        match exp:
            case SeqExp():
                for x in exp.exps:
                    self._code_gen(x, procedure)
            
            case RepeatExp():
                body = []
                for x in exp.exps:
                    self._code_gen(x, body)
                
                proc_body_id = self._next_proc_id()
                self.procedures[proc_body_id] = body
                
                counter = self._next_param(UInt32)
                limit = self._next_param(UInt32)
                
                loop_id = self._next_proc_id()
                loop = [
                    csh.ProcSet(counter, UInt32(0)),
                    csh.ProcSet(limit, exp.count),
                    
                    csh.ProcCall(proc_body_id), 
                    csh.ProcUnop(counter, IncrOp(), counter),
                    
                    csh.ProcIfElse(counter, LtOp(), limit),
                        csh.ProcCall(loop_id),
                        csh.ProcNoop(),
                ]
                
                self.procedures[loop_id] = loop
                
                procedure.append(csh.ProcCall(loop_id))
                
                
                
                
                
                

            case IfElseExp():
                procedure.append(csh.ProcIfElse(exp.a, exp.op, exp.b))
                
                def handle_seq(then_or_else):
                    if isinstance(then_or_else, SeqExp):
                        id = self._sub_proc(then_or_else.exps)
                        procedure.append(csh.ProcCall(id))
                    else:
                        self._code_gen(then_or_else, procedure)
                
                handle_seq(exp.then)
                handle_seq(exp.else_)
            
            case WaitTimeExp():
                # Copy current time to a param
                # Add specified time to the param
                # Block until current time is greater than the param
                
                tmp = self._next_param(UInt32)
                
                for p in [
                    csh.ProcUnop(csh.ParamRef("time"), IdentLocalOp(), tmp),
                    csh.ProcBinop(tmp, AddOp(), exp.time, tmp),
                    csh.ProcBlock(csh.ParamRef("time"), GteOp(), tmp)
                ]:
                    procedure.append(p)
                
            case ProcSetExp():
                tmp = self._next_param(type(exp.value))
                procedure.append(csh.ProcSet(csh.ParamRef(exp.name), exp.value))
            
            case _:
                raise NotImplementedError
            
    
    def code_gen(self, exp: Expression):
        main_prefix = [
            csh.ProcNew(),
        ]
        
        main_suffix = [
            csh.ProcDel(10),
            csh.ProcPush(10),
            csh.ProcRun(10),
        ]
        
        self._code_gen(exp, self.main)
        
        print("Procedures:")
        for k,v in self.procedures.items():
            print(k)
            for x in v:
                print(f"\t{x}")
        
        print("Main:")
        for x in self.main:
            print(f"\t{x}")
