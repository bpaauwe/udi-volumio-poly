#!/usr/bin/env python3
"""
Polyglot v2 node server Volumio Media Server control.
Copyright (C) 2021 Robert Paauwe
"""
import polyinterface
import sys
from nodes import controller

LOGGER = polyinterface.LOGGER

if __name__ == "__main__":
    try:
        polyglot = polyinterface.Interface('Volumio')
        polyglot.start()
        control = controller.Controller(polyglot)
        control.runForever()
    except (KeyboardInterrupt, SystemExit):
        sys.exit(0)
        

