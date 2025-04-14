from proc_comp.parser import parser
from proc_comp.codegen.codegen import CodeGen
import yaml
import json

inp_yaml = """\
name: commands
body:
  - name: set-param
    param:
      variable_name: x
      type: Int8
    type: Int8
    value: 8
  - name: binop
    result: 
      variable_name: x
      type: Int8
    left: 
      variable_name: x
      type: Int8
    right: 
      variable_name: y
      type: Int8
    operator: Add
"""

inp_json = """\
{
    "name": "commands",
    "body": [
        {
            "name": "set-param",
            "param": {
                "variable_name": "x",
                "type": "Int8"
            },
            "type": "Int8",
            "value": 8
        },
        {
            "name": "binop",
            "result": {
                "variable_name": "x",
                "type": "Int8"
            },
            "left": {
                "variable_name": "x",
                "type": "Int8"
            },
            "right": {
                "variable_name": "y",
                "type": "Int8"
            },
            "operator": "Add"
        }
    ]
}
"""

obj_yaml = yaml.safe_load(inp_yaml)
obj_json = json.loads(inp_json)

parsed_yaml = parser.parse(obj_yaml)
parsed_json = parser.parse(obj_json)

print('### YAML ###')
print(parsed_yaml.pprint())

print()
G1 = CodeGen()
for l in G1.code_gen(parsed_yaml):
    print(l)

print('\n\n### JSON ###')
print(parsed_json.pprint())

print()
G2 = CodeGen()
for l in G2.code_gen(parsed_json):
    print(l)