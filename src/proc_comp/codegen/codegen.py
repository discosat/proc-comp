import itertools

from proc_comp.common import types, csh
from proc_comp.common.cfgbuilder import ControlFlowGraph
from proc_comp.common.types.expression import *
from proc_comp.common.types.operator import *
from proc_comp.common.types.param import *
from proc_comp.common.types.csh_param import *


class CodeGen:
    """Class for generating code from an expression tree

    Raises:
        NotImplementedError: _description_
    """
    
    cfg: ControlFlowGraph
    procedures: dict[str, list[csh.CSH_Command]]
    main: list[csh.CSH_Command]
    
    procs: int
    params: dict[type, int]
    
    def __init__(self) -> None:
        self.main = list()
        self.procedures = dict()
        self.procs = 0
        self.params = dict()
        self.cfg = ControlFlowGraph()
    
    def _next_proc_id(self) -> str:
        """Increments the procedure counter and returns the next procedure id. This is used to ensure unique procedure names.

        Returns:
            string: The next procedure id
        """
        self.procs += 1
        return f"proc${self.procs}"

    def _next_param_id(self, type_: type) -> str:
        """Increments the parameter counter for the given type and returns the next parameter id. This is used to ensure unique parameter identifiers.

        Args:
            type_ (type): The type of the parameter. Makes it easier to distinguish between different types of parameters, as the general arrays for those are separate.

        Returns:
            string: The next parameter id
        """
        if type_ not in self.params:
            self.params[type_] = 0
        
        self.params[type_] += 1
        return f"param${type_.type_name}${self.params[type_]}"
    
    def _next_param(self, type_: type) -> csh.ParamGeneralRegister:
        """Increment the parameter counter for the given type and returns a new parameter object.

        Args:
            type_ (type): Given type of the parameter

        Returns:
            csh.ParamGeneralRegister: General (placeholder) parameter object
        """
        return csh.ParamGeneralRegister(type_, self._next_param_id(type_))
    
    def _sub_proc(self, exps: list[Expression]) -> str:
        """Helper function to generate a sub-procedure from a list of expressions

        Args:
            exps (list[Expression]): List of expressions to be converted to a sub-procedure

        Returns:
            str: Proc slot id of the generated procedure
        """
        body = []
        for x in exps:
            self._code_gen_recursive(x, body)
        
        id = self._next_proc_id()
        self.procedures[id] = body
        
        return id
    
    def _add_command(self, command: csh.CSH_Command, procedure: list[csh.CSH_Command]):
        procedure.append(command)
        self.cfg.add_instruction(command.cfg_instruction)
    
    def _add_commands(self, procedure: list[csh.CSH_Command], *commands:csh.CSH_Command):
        for cmd in commands:
            self._add_command(cmd, procedure)

    def _code_gen_recursive(self, exp: Expression, procedure: list[csh.CSH_Command]):
        """Recursive function to generate code from an expression tree.
        Instructions are added to the given procedure list, and the control flow graph is built accordingly, keeping track of how params are used by instructions. 
        
        The function builds on a match statement to pattern match the given expression. This must be updated as new expression types are added.

        Args:
            exp (Expression): _description_
            procedure (list[csh.CSH_Command]): _description_

        Raises:
            NotImplementedError: _description_

        Returns:
            None
        """
        match exp:
            case NoopExp():
                self._add_command(csh.ProcNoop(), procedure)

            case SeqExp():
                for x in exp.exps:
                    self._code_gen_recursive(x, procedure)
            
            case RepeatExp():
                body = []
                loop = []

                proc_body_id = self._next_proc_id()
                counter = self._next_param(UInt32)
                limit = self._next_param(UInt32)
                loop_id = self._next_proc_id()

                # Initialize loop variables before entering the loop. This avoids endlessly looping
                self._add_commands(procedure,
                    csh.ProcSet(counter, UInt32(0)),
                    csh.ProcSet(limit, exp.count),
                    csh.ProcCall(loop_id), 
                )

                # CFG Head
                cfghead = self.cfg.block_next("repeat_head")

                self._add_commands(loop,
                    csh.ProcIfElse(counter, LtOp(), limit),
                        csh.ProcCall(proc_body_id), 
                        csh.ProcNoop(),
                )
                self.procedures[loop_id] = loop

                # CFG Body
                cfgbody = self.cfg.block_next("repeat_body")

                self._code_gen_recursive(exp.exp, body)

                # CFG Loop tail
                cfgtail = self.cfg.block_next("repeat_tail")

                self._add_commands(body,
                    csh.ProcUnop(counter, IncrOp(), counter),
                    csh.ProcCall(loop_id),
                )
                self.procedures[proc_body_id] = body

                self.cfg.block_end()

                cfgtail.successors.add(cfghead)
                cfghead.predecessors.add(cfgtail)
                
                cfgmerge = self.cfg.block_start("repeat_merge", cfghead)
                
            case IfElseExp():
                # Head
                cfghead = self.cfg.block_next("if_head")

                self._add_command(csh.ProcIfElse(exp.a, exp.op, exp.b), procedure)
                self.cfg.block_end()
                
                def handle_seq(then_or_else, block_name):
                    cfgblock = self.cfg.block_start(f"if_{block_name}", succeeds=cfghead)
                    if isinstance(then_or_else, SeqExp):
                        id = self._sub_proc(then_or_else.exps)
                        self._add_command(csh.ProcCall(id), procedure)
                    else:
                        self._code_gen_recursive(then_or_else, procedure)
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
                tmp2 = self._next_param(UInt32)
                time = csh.ParamRef("time")
                
                self._add_commands(procedure,
                    csh.ProcUnop(time, IdentLocalOp(), tmp),
                    csh.ProcSet(tmp2, exp.time),
                    csh.ProcBinop(tmp, AddOp(), tmp2, tmp),
                    csh.ProcBlock(time, GteOp(), tmp),
                )
                
            case ProcSetExp():
                self._add_command(csh.ProcSet(exp.param, exp.value), procedure)
            
            case ProcBinopExp():
                self._add_command(csh.ProcBinop(a=exp.left, b=exp.right, result=exp.result, op=exp.operator), procedure)
            
            case ProcUnopExp():
                self._add_command(csh.ProcUnop(value=exp.value, result=exp.result, op=exp.operator), procedure)

            case ProcCaptureImages():
                value = (
                    f"\"CAMERA_TYPE={exp.cameraType.value};"
                    f"CAMERA_ID={exp.cameraID.value};"
                    f"NUM_IMAGES={exp.numOfImages.value};"
                    f"EXPOSURE={exp.exposure.value};"
                    f"ISO={exp.iso.value};"
                    f"INTERVAL={exp.interval.value};\""
                )

                self._code_gen_recursive(ProcSetExp(ParamRef("capture_params"), String(value)), procedure)

            case RawCSH():
                for cmd in exp.commands:
                    procedure.append(csh.RawCommand(cmd))

            case _:
                raise NotImplementedError(exp)
            
    
    def code_gen(self, exp: Expression) -> list[str]:
        """Main function to generate code from an expression tree. This function is called to start the code generation process and the required sub processes.

        Args:
            exp (Expression): The main expression tree to generate code from
            
        Returns:
            list[str]: The generated code in the form of a list of strings
        """
        
        self.cfg.block_start("main")

        self._code_gen_recursive(exp, self.main)

        self.cfg.block_end()
        
        #print("Procedures:")                 TODO: make toggleable
        #for k,v in self.procedures.items():
        #    print(k)
        #    for x in v:
        #        print(f"\t{x}")
        #
        #print("Main:")
        #for x in self.main:
        #    print(f"\t{x}")
        
        def all_subclasses(cls):
            return set(cls.__subclasses__()).union(
                [s for c in cls.__subclasses__() for s in all_subclasses(c)])
        
        # Register allocation:
        color_maps = self.cfg.calc_liveness()
        
        param_map = dict()
        for reg, color_map in color_maps.items():
            for param, i in color_map.items():
                for typ in all_subclasses(ParamType):
                    if typ.register_name == reg and typ.num_registers <= i:
                        raise Exception("Not enough registers for ", reg, f"({i}/{typ.num_registers})")
                ref = csh.ParamRef(reg, i)
                param_map[param] = ref
        
        # Slot allocation
        MAIN_SLOT_ID = 10
        MIN_SLOT_ID = 11
        MAX_SLOT_ID = 255
        AVAIL_SLOT_IDS = MAX_SLOT_ID - MIN_SLOT_ID

        # get all proc slots
        temp_slots = list(self.procedures.keys()).copy()
        if len(temp_slots) > AVAIL_SLOT_IDS:
            raise Exception('Not enough slots. Too many procedures generated')
        
        slot_map = dict()
        for i, k in enumerate(temp_slots):
            n = i + MIN_SLOT_ID
            slot_map[k] = n
            self.procedures[n] = self.procedures.pop(k)

        # Update all param and slot placeholders in commands with output from colouring/slot allocation
        ## Use itertools to iterate over all commands in main and procedures as if a single list
        for cmd in itertools.chain(self.main, itertools.chain.from_iterable(self.procedures.values())):
            before = str(cmd)
            cmd.update_params(param_map)
            for attr_name,attr in vars(cmd).items():
                if isinstance(attr, ParamGeneralRegister):
                    raise Exception(f'Missing update of param "{attr_name}" in "{cmd}". Is it unused?')
            cmd.update_slots(slot_map)
            after = str(cmd)
            if before != after:
                # print(f'Updated: {before}\n ------> {after}')
                pass
        
        
        #print("POST COLORING:")         TODO: make toggleable
        
        #print("Procedures:")
        #for k,v in self.procedures.items():
        #    print(k)
        #    for x in v:
        #        print(f"\t{x}")
        #
        #print("Main:")
        #for x in self.main:
        #    print(f"\t{x}")
        

        # Generate and output list of resulting CSH script 
        REMOTE_NODE = 12

        instruction_list: list[csh.CSH_Command] = []

        def add_proc(proc_id, instructions):
            instruction_list.append(csh.ProcDel(proc_id, REMOTE_NODE))
            instruction_list.append(csh.ProcNew())
            for instr in instructions:
                instruction_list.append(instr)
            instruction_list.append(csh.ProcPush(proc_id, REMOTE_NODE))

        add_proc(MAIN_SLOT_ID, self.main)
        for proc, instructions in self.procedures.items():
            add_proc(proc, instructions)
        
        instruction_list.append(csh.ProcRun(MAIN_SLOT_ID, REMOTE_NODE))

        commands: list[str] = []

        for instruction in instruction_list:
            commands.append(instruction.command_string())


        return commands
        
