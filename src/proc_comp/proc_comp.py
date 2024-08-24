#!/usr/bin/env python3

import argparse
import logging
import logging.config

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="Input file")
    parser.add_argument("--output", "-o", help="Output file", default="out.csh")
    parser.add_argument("--verbose", "-v", help="Enable verbose mode", action="store_true")
    parser.add_argument("--log-file", "-l", help="Set logging to file instead of stdout/stderr")

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
