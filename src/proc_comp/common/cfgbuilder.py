class Instruction:
    sets: set
    uses: set
    live_in: set
    live_out: set
    
    def __init__(self, sets=None, uses=None) -> None:
        if not sets:
            sets = set()
        if not uses:
            uses = set()
        self.sets = sets
        self.uses = uses
        self.live_in = set()
        self.live_out = set()
    
    def __str__(self) -> str:
        return f"Instruction(sets {self.sets}, uses {self.uses})"

    def __repr__(self) -> str:
        return self.__str__()

class Block:
    name: str
    
    live_in: set
    live_out: set
    
    instructions: list[Instruction]
    predecessors: set
    successors: set
    
    def __init__(self, name) -> None:
        self.name = name
        self.instructions = []
        self.predecessors = set()
        self.successors = set()
        self.live_in = set()
        self.live_out = set()
    
    def __str__(self) -> str:
        return f"Block({self.name}, {self.instructions})"

    def __repr__(self) -> str:
        return self.__str__()

    
    def add_instruction(self, instruction):
        self.instructions.append(instruction)


class ControlFlowGraph:
    blocks: list[Block]
    current_block: Block

    block_id: int

    def __init__(self):
        self.blocks = []
        self.current_block = None
        self.block_id = 0
    
    def __str__(self) -> str:
        return (
            "ControlFlowGraph(\n\t"
            + "\n\t".join([str(x) for x in self.blocks])
            + "\n)"
        )

    def __repr__(self) -> str:
        return self.__str__()
    
    def block_start(self, name, succeeds:Block|list[Block]=None):
        if self.current_block:
            raise Exception("Block not terminated")
        
        self.current_block = Block(name + "#" + str(self.block_id))
        self.block_id += 1
        if succeeds:
            if isinstance(succeeds, list):
                for s in succeeds:
                    self.current_block.predecessors.add(s)
                    s.successors.add(self.current_block)
            else:
                self.current_block.predecessors.add(succeeds)
                succeeds.successors.add(self.current_block)
        return self.current_block

    def block_end(self):
        if not self.current_block:
            raise Exception("No block to end. Current blocks: " + str(self.blocks))
        self.blocks.append(self.current_block)
        self.current_block = None
    
    def add_instruction(self, instruction: Instruction):
        if not self.current_block:
            raise Exception("No block to add instruction to")
        self.current_block.add_instruction(instruction)

    def calc_liveness(self):
        '''
        live_in = use(n) U (live_out - def(n))
        live_out = U (for all s in succ(n)) live_in(s)
        '''
        i = 0
        while True:
            print("Calculating liveness...", i)
            i += 1
            changed = False
            for block in reversed(self.blocks):
                print(f"Calculating liveness for block {block.name}")
                print(f"Old live_in: {block.live_in}")
                print(f"Old live_out: {block.live_out}")

                old_live_out = block.live_out.copy()
                old_live_in = block.live_in.copy()
                block.live_out = set()
                for s in block.successors:
                    block.live_out |= s.live_in
                
                block.live_in = block.live_out.copy()
                for instruction in reversed(block.instructions):
                    print(instruction)
                    block.live_in |= instruction.uses
                    block.live_in -= instruction.sets
                
                print(f"New live_in: {block.live_in}")
                print(f"New live_out: {block.live_out}\n")

                if block.live_out != old_live_out or block.live_in != old_live_in:
                    changed = True
            if not changed:
                break
    
    def pprint(self):
        print('Control Flow Graph')
        for block in self.blocks:
            print(f"Block: {block.name}")
            print(f"\tInstructions:")
            for i in block.instructions:
                print(f"\t\t{i}")
            print(f"\tPredecessors: {[b.name for b in block.predecessors]}")
            print(f"\tSuccessors: {[b.name for b in block.successors]}")
            print(f"\tLive In: {block.live_in}")
            print(f"\tLive Out: {block.live_out}")
            print()