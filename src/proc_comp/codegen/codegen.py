from ..common.types import *
from ..common import csh
from ..common.cfgbuilder import ControlFlowGraph, Instruction


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
                loop = []

                proc_body_id = self._next_proc_id()
                counter = self._next_param(UInt32)
                limit = self._next_param(UInt32)
                loop_id = self._next_proc_id()


                procedure.append(csh.ProcCall(loop_id))

                cfgprev = self.cfg.current_block
                self.cfg.block_end()

                # CFG Head
                cfghead = self.cfg.block_start("repeat_head", succeeds=cfgprev)

                loop += [
                    csh.ProcSet(counter, UInt32(0)),
                    csh.ProcSet(limit, exp.count),
                    csh.ProcCall(proc_body_id), 
                ]
                self.cfg.add_instruction(Instruction(sets={counter}))
                self.cfg.add_instruction(Instruction(sets={limit}))
                self.cfg.block_end()

                # CFG Body
                cfgbody = self.cfg.block_start("repeat_body", succeeds=cfghead)

                for x in exp.exps:
                    self._code_gen(x, body)
                
                self.procedures[proc_body_id] = body

                self.cfg.block_end()

                
                # CFG Loop check/tail
                cfgtail = self.cfg.block_start("repeat_tail", succeeds=cfgbody)

                loop += [
                    csh.ProcUnop(counter, IncrOp(), counter),
                    csh.ProcIfElse(counter, LtOp(), limit),
                        csh.ProcCall(loop_id),
                        csh.ProcNoop(),
                ]

                self.cfg.add_instruction(Instruction(sets={counter}, uses={counter}))
                self.cfg.block_end()
                cfgtail.successors.add(cfghead)
                cfghead.predecessors.add(cfgtail)

                self.procedures[loop_id] = loop
                
                cfgmerge = self.cfg.block_start("repeat_merge", succeeds=cfgtail)
                
            case IfElseExp():
                cfgprev = self.cfg.current_block
                self.cfg.block_end()

                # Head
                cfghead = self.cfg.block_start("if_head", cfgprev)

                procedure.append(csh.ProcIfElse(exp.a, exp.op, exp.b))
                self.cfg.add_instruction(Instruction(uses={exp.a, exp.b}))
                self.cfg.block_end()
                
                def handle_seq(then_or_else, block_name):
                    cfgblock = self.cfg.block_start(f"if_{block_name}", succeeds=cfghead)
                    if isinstance(then_or_else, SeqExp):
                        id = self._sub_proc(then_or_else.exps)
                        procedure.append(csh.ProcCall(id))
                    else:
                        self._code_gen(then_or_else, procedure)
                    self.cfg.block_end()
                    return cfgblock
                
                cfgthen = handle_seq(exp.then, 'then')
                cfgelse = handle_seq(exp.else_, 'else')

                cfgmerge = self.cfg.block_start("if_merge", succeeds=[cfgthen, cfgelse])
                
            
            case WaitTimeExp():
                # Copy current time to a param
                # Add specified time to the param
                # Block until current time is greater than the param
                
                tmp = self._next_param(UInt32)
                time = csh.ParamRef("time")
                
                # Don't add time to the CFG as it is a hardcoded param name
                procedure.append(csh.ProcUnop(time, IdentLocalOp(), tmp))
                self.cfg.add_instruction(Instruction(sets={tmp}))

                procedure.append(csh.ProcBinop(tmp, AddOp(), exp.time, tmp))
                self.cfg.add_instruction(Instruction(sets={tmp},uses={tmp}))

                procedure.append(csh.ProcBlock(time, GteOp(), tmp))
                self.cfg.add_instruction(Instruction(uses={tmp}))

                
            case ProcSetExp():
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
        
        self.cfg.block_start("main")

        self._code_gen(exp, self.main)

        self.cfg.block_end()
        
        print("Procedures:")
        for k,v in self.procedures.items():
            print(k)
            for x in v:
                print(f"\t{x}")
        
        print("Main:")
        for x in self.main:
            print(f"\t{x}")
