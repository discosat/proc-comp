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