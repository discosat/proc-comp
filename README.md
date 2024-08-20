# proc-comp

A compiler targeting [CSH](https://github.com/spaceinventor/csh) scripts with [csp_proc](https://github.com/discosat/csp_proc/) from .json source syntax files.


## Development

Setup a virtual environment and install requirements:

```bash
python3 -m venv .venv
source venv/bin/activate
pip install -r requirements.txt
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