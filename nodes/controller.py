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
import threading
from socketIO_client import SocketIO, LoggingNamespace
import dns.resolver
import node_funcs
import write_nls
from nodes import myserver

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
        self.server = None
        self.sources = []
        self.ip_address = ''

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

        while not self.configured:
            LOGGER.debug('Waiting for configuration')
            time.sleep(5)

        if self.params.get('IP Address').endswith('local'):
            myres = dns.resolver.Resolver()
            myres.nameservers = ['224.0.0.251']
            myres.port = 5353
            try:
                ip = myres.resolve(self.params.get('IP Address'), 'A')
                self.ip_address = 'http://' + ip[0].to_text()
            except:
                self.ip_address = 'http://' + self.params.get('IP Address')
        else:
            self.ip_address = 'http://' + self.params.get('IP Address')

        LOGGER.info('Start client now with {}'.format(self.ip_address))
        self.start_client(self.ip_address)

        LOGGER.info('Node server started')

    def longPoll(self):
        pass

    def shortPoll(self):
        pass

    def query(self):
        for node in self.nodes:
            self.nodes[node].reportDrivers()

    """
    TODO:

    Discover sources.  Browse the root and pull out the components we
    want to use as source.  I think this will result in favorites,
    spotify and pandora.  The get the list of playlist and add those
    to the sources list.

    Once we have the list of sources, use that to generate the NLS entries.

    Ideally, only do this if either the list doesn't exist or the user runs
    the discover command manually.

    Thus, we should save the list in CustomData so we should check that before
    running discover from start.

    Do we want to allow custom sources?  we could have the user enter the uri
    value in the custom params for custom sources and add those to the list.
    """
    def discover(self, *args, **kwargs):
        src_cnt = 0
        self.sources = []
        root = self.send_command('browse')
        for src in root['navigation']['lists']:
            LOGGER.error('Found {}'.format(src['uri']))
            if src['uri'] == 'favourites':
                self.sources.append({'name': 'Favourites', 'uri': 'favourites'})
            elif src['uri'] == '/pandora':
                #TODO: Look up pandora stations
                stations = self.send_command('browse', 'uri=/pandora')
                sl = stations['navigation']['lists'][0]['items']
                for s in sl:
                    LOGGER.debug('found: {} {}'.format(s['name'], s['uri']))
                    self.sources.append({'name': s['name'], 'uri': s['uri']})
            elif src['uri'] == '/spotify':
                self.sources.append({'name': 'Spotify', 'uri': '/spotify'})

        playlists = self.send_command('listplaylists')
        for play in playlists:
            LOGGER.error('Found {}'.format(play))
            self.sources.append({'name': play, 'uri': 'playplaylist'})

        #TODO: Create and write out NLS with this source list
        write_nls.write_nls(LOGGER, self.sources)
        self.poly.installprofile()

        #Save source list to customData
        if 'customData' in self.polyConfig:
            customdata = self.polyConfig['customData']
        else:
            customdata = {}
        customdata['sourceList'] = self.sources
        self.poly.saveCustomData(customdata)

    # Delete the node server from Polyglot
    def delete(self):
        LOGGER.info('Removing node server')

    def stop(self):
        self.server.Stop = True
        self.server.socket.close()
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
        return
        if level is None:
            try:
                level = self.get_saved_log_level()
            except:
                LOGGER.error('unable to get saved log level.')
        if level is None:
            level = 30
        else:
            level = int(level['value'])

        level = 10
        LOGGER.info('Setting log level to %d' % level)
        LOGGER.setLevel(level)
        self.setDriver('GV0', level)


    def send_command(self, command, value=None):
        cmds = ['play', 'toggle', 'stop', 'pause', 'prev', 'next', 'clearQueue']
        cmdv = ['playplaylist', 'repeat', 'random', 'volume']

        url = self.ip_address + '/api/v1/'
        if command in cmds:
            url += 'commands?cmd=' + command
        elif command in cmdv:
            url += 'commands?cmd=' + command + '&' + value
        else:
            if value is not None:
                url += command + '?' + value
            else:
                url += command

        LOGGER.debug('sending: {}'.format(url))
        c = requests.get(url)
        LOGGER.debug('send_command retuned: {}'.format(c.text))
        try:
            jdata = c.json()
        except Exception as e:
            LOGGER.error('GET {} failed: {}'.format(url, c.text))
            jdata = ''
        c.close()

        return jdata

    def post_request(self, command, body):
        url = self.ip_address + '/api/v1/' + command

        c = requests.post(url, json=body)

        try:
            jdata = c.json()
        except Exception as e:
            LOGGER.error('GET {} failed: {}'.format(url, c.text))
            jdata = ''
        c.close()

        return jdata

    """
      Use replaceAndPlay to add items to the queue or replace what's
      currently playing with something new.

      This will probably be used to select things like Pandora or a
      playlist or is it just used to add individual tracks?
    """
    def replaceAndPlay(self):
        pass

    def status(self, info, force=False):
        LOGGER.debug('Setting initial status')
        self.setDriver('SVOL', int(info['volume']), True, force)
        self.setDriver('DUR', int(info['duration']), True, force)
        if info['status'].lower() == 'stop':
            self.setDriver('MODE', 0, True, force)
        elif info['status'].lower() == 'play':
            self.setDriver('MODE', 2, True, force)
        else:
            self.setDriver('MODE', 1, True, force)

        if info['random']:
            self.setDriver('GV4', 1, True, force)
        else:
            self.setDriver('GV4', 0, True, force)

        if info['repeat']:
            self.setDriver('GV5', 1, True, force)
        else:
            self.setDriver('GV5', 0, True, force)


    def web_server(self):
        """
        Notifications:
          Send a post to pushNotificationsUrls?url=<our server process>
        """
        try:
            self.server = myserver.Server(('', 8383), myserver.VHandler)
            self.server.serve_forever(self)
        except Exception as e:
            LOGGER.error('web server failed: {}'.format(e))

    def start_client(self, ip):
        LOGGER.error('Status: {}'.format(self.send_command('getState')))

        if 'customData' in self.polyConfig:
            if 'sourceList' in self.polyConfig['customData']:
                self.sources = self.polyConfig['customData']['sourceList']
                for src in self.sources:
                    LOGGER.debug('Restoring source: {}'.format(src))

        if len(self.sources) == 0:
            LOGGER.error('Calling discover')
            self.discover()

        LOGGER.error('Starting notification server')
        self.notification_thread = threading.Thread(target = self.web_server)
        self.notification_thread.daemon = True
        self.notification_thread.start()

        LOGGER.error('network = {}'.format(self.poly.network_interface))
        address = self.poly.network_interface['addr']
        url = 'http://' + address + ':8383/volumiostatus'
        self.post_request('pushNotificationUrls', {"url": url})

        LOGGER.error('{}'.format(self.send_command('pushNotificationUrls')))

        # Get current status
        info = self.send_command('getState')
        self.status(info, True)



    def process_cmd(self, cmd=None):
        LOGGER.error('ISY sent: {}'.format(cmd))
        if cmd is not None:
            if cmd['cmd'] == 'PLAY':
                self.send_command('play')
            elif cmd['cmd'] == 'PAUSE':
                self.send_command('pause')
            elif cmd['cmd'] == 'NEXT':
                self.send_command('next')
            elif cmd['cmd'] == 'PREV':
                self.send_command('prev')
            elif cmd['cmd'] == 'STOP':
                self.send_command('stop')
            elif cmd['cmd'] == 'VOLUME':
                self.send_command('volume', 'volume=' + cmd['value'])
            elif cmd['cmd'] == 'SHUFFLE':
                if cmd['value'] == 0:
                    value = 'false'
                else:
                    value = 'true'
                self.send_command('random', 'value=' + value)
            elif cmd['cmd'] == 'REPEAT':
                if cmd['value'] == 0:
                    value = 'false'
                else:
                    value = 'true'
                self.send_command('repeat', 'value=' + value)
            elif cmd['cmd'] == 'SOURCE':
                LOGGER.debug('selected source now = {}'.format(cmd['value']))
                idx = int(cmd['value'])
                try:
                    src = self.sources[idx]
                    LOGGER.debug('Found source entry {}'.format(src))
                    # what are the different playback mechinims. 
                    #   pandora or spotify
                    #   favorites
                    #   playlists
                    self.send_command('stop')
                    self.send_command('clearQueue')
                    if 'pandora' in src['uri']:
                        self.send_command('browse', 'uri=' + src['uri'])
                        self.send_command('repeat', 'value=false')
                        self.send_command('random', 'value=false')
                        self.send_command('next')
                        self.send_command('play')
                    elif 'spotify' in src['uri']:
                        self.send_command('browse', 'uri=' + src['uri'])
                        self.send_command('repeat', 'value=false')
                        self.send_command('random', 'value=false')
                        self.send_command('next')
                        self.send_command('play')
                    elif src['name'] == 'Favourites':
                        self.send_command('browse', 'uri=' + src['uri'])
                        self.send_command('repeat', 'value=false')
                        self.send_command('random', 'value=true')
                        self.send_command('play')
                    else: # playlist
                        self.send_command('playplaylist', 'name=' + src['name'])
                        self.send_command('repeat', 'value=false')
                        self.send_command('random', 'value=true')
                        self.send_command('next')
                        self.send_command('play')

                    self.setDriver('GV1', idx, True)
                except:
                    LOGGER.debug('Index {} not found in {}'.format(idx, self.sources))

    commands = {
            'DISCOVER': discover,
            'REMOVE_NOTICES_ALL': remove_notices_all,
            'UPDATE_PROFILE': update_profile,
            'DEBUG': set_logging_level,
            'VOLUME': process_cmd,
            'SOURCE': process_cmd,
            'PLAY': process_cmd,
            'PAUSE': process_cmd,
            'SHUFFLE': process_cmd,
            'REPEAT': process_cmd,
            'PREV': process_cmd,
            'NEXT': process_cmd,
            }

    drivers = [
            {'driver': 'ST', 'value': 1, 'uom': 2},       # node server status
            {'driver': 'GV0', 'value': 0, 'uom': 25},     # Log Level
            {'driver': 'GV1', 'value': 0, 'uom': 25},     # Source
            {'driver': 'SVOL', 'value': 0, 'uom': 12},    # Volume
            {'driver': 'DUR', 'value': 0, 'uom': 58},     # duration
            {'driver': 'TIMEREM', 'value': 0, 'uom': 58}, # remaining
            {'driver': 'GV4', 'value': 0, 'uom': 25},     # shuffle
            {'driver': 'GV5', 'value': 0, 'uom': 25},     # repeat
            {'driver': 'MODE', 'value': 0, 'uom': 25},    # play/pause
            ]

    
