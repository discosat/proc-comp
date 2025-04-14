#!/usr/bin/env python3

import argparse
import logging
import logging.config
import json
from proc_comp.parser import parser as codeParser
from proc_comp.codegen import codegen
import yaml

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="Input file")
    parser.add_argument("--output", "-o", help="Output file", default="out.csh")
    parser.add_argument("--verbose", "-v", help="Enable verbose mode", action="store_true")
    parser.add_argument("--log-file", "-l", help="Set logging to file instead of stdout/stderr")
    parser.add_argument("--yaml", "-y", help="Parse input as YAML instead of JSON", action="store_true")

    args = parser.parse_args()

    logConf = {
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    }

    if args.verbose:
        logConf["level"] = logging.DEBUG
    
    if args.log_file:
        logConf["filename"] = args.log_file
    
    logging.basicConfig(**logConf)

    logger.debug("Input file: %s", args.input)
    logger.debug("Output file: %s", args.output)

    with open(args.input, 'r') as f:
        if args.yaml:
            input_stream = yaml.safe_load(f)
        else:
            input_stream = json.load(f)
    
    ast = codeParser.parse(input_stream)
    logger.debug("Ast: %s", ast)

    csh_generator = codegen.CodeGen()
    csh_script = csh_generator.code_gen(exp=ast)
    code = '\n'.join(csh_script)

    with open(args.output, 'w') as f:
        f.write(code)

    logger.info("CSH script written to %s", args.output)
