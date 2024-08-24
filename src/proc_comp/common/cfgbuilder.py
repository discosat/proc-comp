class Instruction:
    sets: set
    uses: set
    
    def __init__(self, sets, uses) -> None:
        self.sets = sets
        self.uses = uses

class Block:
    name: str
    
    live_in: set
    live_out: set
    
    instructions: set
    predecessors: set
    successors: set
    
    def __init__(self, name) -> None:
        self.name = name
    
    def add_instruction(self, instruction):
        self.instructions.append(instruction)


class ControlFlowGraph:
    blocks: list[Block]
    current_block: Block
    
    def block_start(self, name):
        if self.current_block:
            raise Exception("Block not terminated")
        self.current_block = Block(name)

    def block_end(self):
        if not self.current_block:
            raise Exception("No block to end")
        self.blocks.append(self.current_block)
        self.current_block = None
    
    def add_instruction(self, instruction):
        if not self.current_block:
            raise Exception("No block to add instruction to")
        self.current_block.add_instruction(instruction)

    def calc_liveness(self):
        pass