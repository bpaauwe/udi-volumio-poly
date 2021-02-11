#!/usr/bin/env python3
"""
Polyglot v2 node server Volumio Media Server control.
Copyright (C) 2021 Robert Paauwe
"""
import polyinterface
import sys
import time
import json
import requests
from socketIO_client import SocketIO, LoggingNamespace
import node_funcs

LOGGER = polyinterface.LOGGER

@node_funcs.add_functions_as_methods(node_funcs.functions)
class Controller(polyinterface.Controller):
    id = 'Volumio'
    def __init__(self, polyglot):
        super(Controller, self).__init__(polyglot)
        self.name = 'Volumio'
        self.address = 'vctl'
        self.primary = self.address
        self.roku_list = {}
        self.in_config = False
        self.configured = False

        self.params = node_funcs.NSParameters([{
            'name': 'IP Address',
            'default': 'set volumio IP address',
            'isRequired': True,
            'notice': 'IP address/name must be set'
            } ])

        self.poly.onConfig(self.process_config)

    # Process changes to customParameters
    def process_config(self, config):
        (valid, changed) = self.params.update_from_polyglot(config)
        if changed and not valid:
            self.removeNoticesAll()
            self.params.send_notices(self)
        elif changed and valid:
            self.removeNoticesAll()
            self.configured = True
        elif valid:
            LOGGER.debug('CFG: configuration is valid')

    def start(self):
        LOGGER.info('Starting node server')

        self.set_logging_level()
        self.check_params()
        #self.discover()

        while not self.configured:
            time.sleep(5)

        self.start_client(self.params.get('IP Address'))

        LOGGER.info('Node server started')

    def longPoll(self):
        pass

    def shortPoll(self):
        pass

    def query(self):
        for node in self.nodes:
            self.nodes[node].reportDrivers()

    # TODO: is there anything we need to discover?
    def discover(self, *args, **kwargs):
        pass

    # Delete the node server from Polyglot
    def delete(self):
        sio.disconnect()
        LOGGER.info('Removing node server')

    def stop(self):
        sio.disconnect()
        LOGGER.info('Stopping node server')

    def update_profile(self, command):
        st = self.poly.installprofile()
        return st

    def check_params(self):
        self.removeNoticesAll()
        if self.params.get_from_polyglot(self):
            self.configured = True
        else:
            self.params.send_notices(self)

    def remove_notices_all(self, command):
        self.removeNoticesAll()

    def set_logging_level(self, level=None):
        if level is None:
            try:
                level = self.get_saved_log_level()
            except:
                LOGGER.error('unable to get saved log level.')
        if level is None:
            level = 30
        else:
            level = int(level['value'])

        LOGGER.info('Setting log level to %d' % level)
        LOGGER.setLevel(level)
        self.setDriver('GV0', level)

    def start_client(self, ip):
        self.sio = SocketIO(ip, 3000)
        self.sio.on('connect', self.on_connect)
        self.sio.on('disconnect', self.on_disconnect)
        self.sio.on('pushState', self.on_pushState)
        self.sio.on('pushState', self.on_pushState)
        self.sio.on('pushBrowseSources', self.on_pushState)

        # gets the current state
        self.sio.emit('getState', '')
        self.sio.wait(seconds=10)

        # gets the list of sources
        self.sio.emit('getBrowseSources', '')
        self.sio.wait(seconds=10)

    def on_connect(self):
        LOGGER.error('Connected to websocket interface')

    def on_disconnect(self):
        LOGGER.error('Connection to websocket interfaced dropped.')

    def on_pushState(self, data):
        LOGGER.error('Got message: {}'.format(data))

    commands = {
            'DISCOVER': discover,
            'REMOVE_NOTICES_ALL': remove_notices_all,
            'UPDATE_PROFILE': update_profile,
            'DEBUG': set_logging_level,
            }

    drivers = [
            {'driver': 'ST', 'value': 1, 'uom': 2},   # node server status
            {'driver': 'GV0', 'value': 0, 'uom': 25}, # Log Level
            ]

    
