#! /usr/bin/env python
from optparse import OptionParser
import os
import sys

sys.path.append("./src")

from core import Core

doc=""" 
%omxone [options]
"""

def main():
    parser = OptionParser(version="%omxone 0.1", usage=doc)
    parser.add_option("-c", "--config", dest="config", default="omxone.conf",
                      help="load configuration from FILE", metavar="FILE")
    parser.add_option("-l", "--device-list",
                      action="store_true", dest="list_devices", default=False,
                      help="print a list of available MIDI devices")
    parser.add_option("-d", "--debug",
                      action="store_true", dest="debug", default=False,
                      help="print debug information")
    parser.add_option("-i", "--interactive",
                      action="store_true", dest="interactive", default=False,
                      help="enter interactive mode")
    (options, args) = parser.parse_args()
    
    
    Core.instance().run(options)
       
if __name__ == '__main__':
    main() 
