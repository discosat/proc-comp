# proc-comp

A compiler targeting [CSH](https://github.com/spaceinventor/csh) scripts with [csp_proc](https://github.com/discosat/csp_proc/) from .json source syntax files.


## Development

Setup a virtual environment and install requirements:

```bash
python3 -m venv .venv
source venv/bin/activate
pip install -r requirements.txt
pip install --editable .
```

### Project overview

proc_comp is developed as a Python package. This allows splitting it into multiple modules (files).


Below, the steps done by the compiler is described. Cleanup still needed and function names might not be correct, but this is the main idea:

```
---From frontend--> General language/JSON
---parser--> intermediary representation/abstract syntax 
---codegen.procgen--> CSH command representation split into proc functions. A control flow graph is built alongside
---cfg.calc_liveness--> Analyse the control flow graph for parameter liveness. Calculate a colored graph for reuse of general purpose parameters.
---codegen.assign_params--> Replace placeholder params with general purpose params found with coloring

TODO: 
---codegen.assign_slots--> Analyse which slots are available and update the slot names correspondingly.
---codegen.codegen--> Generate actual CSH script. Use a csh_str() method from common/csh.py (not implemented yet)
```

### Implementing additional translation blocks

To add compiler support for a new type of block, the following modifications should be made:
1. Add a new expression type (can be omitted if the new block reuses existing types)
  - Define attributes and the constructor as necessary 
  - Define `__str__()` to help debugging the parser output
  - Implement `__pprint__()` if additional data or lines should be printed when pretty printing
2. Add an item to the expression map in `parser.py`. Define the expression's attributes and set the expression as a lambda function that takes the parser function and expression block object and returns the Expression.
3. If the expression uses an undefined CSH command, define it in `csh.py`. If the command uses or sets any (general purpose) parameters, set the `self._cfg_instruction` correspondingly -- see e.g. `ProcUnop` for an example. 
4. Lastly, create a new match case in `codegen.py`'s `_code_gen()`, and add the corresponding procedure instructions. If branching control flow is introduced, it is important to keep the control flow graph up to date. Most importantly is ensuring it actually branches properly out and that predecessors and successors are correct. While `cfg.block_next` sets the immediate predecessor automatically others still need to be handled manually. This is done in the `if-else` case as an example. 


## Usage
```
usage: proc_comp.py [-h] [--output OUTPUT] [--verbose] [--log-file LOG_FILE] input

positional arguments:
  input                 Input file

options:
  -h, --help            show this help message and exit
  --output OUTPUT, -o OUTPUT
                        Output file
  --verbose, -v         Enable verbose mode
  --log-file LOG_FILE, -l LOG_FILE
                        Set logging to file instead of stdout/stderr
```


## Functionality to support
- (GPIO) Set GPIO high/low
- (CSH) custom code
- (CSH) get param
- (CSH) set param
- (proc) management
  - `proc new`
  - `proc del`
  - `proc pull`
  - `proc push`
  - `proc size`
  - `proc pop`
  - `proc list`
  - `proc slots`
  - `proc run`
- (proc) Control flow
  - `proc block <param a> <binop> <param b>`
  - `proc ifelse <param a> <binop> <param b>`
  - `proc noop`
  - `proc set <param> <value>`
  - `proc unop <param> <unop> <result>`
  - `proc binop <param a> <binop> <param b> <result>`
  - `proc call <procedure slot>`
- 