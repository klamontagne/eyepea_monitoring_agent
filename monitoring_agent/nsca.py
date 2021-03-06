# -*- coding: utf-8 -*-
'''
NSCA handling
'''

#from pprint import pprint as pp # debug only
import logging
import pynsca
import socket

import configurator

class Nsca(object):
    '''
    Manage NSCA requests
    '''


    def __init__(self, config_file):
        '''
        Read the config file and start NSCA connexions
        '''
        # Setup servers dict from config file
        self.servers = configurator.read(config_file,
                                         configspec='configspecs/nsca.cfg',
                                         server_mode=True)
        # start NSCA connexions
        for server in self.servers:
            self.servers[server]['notifier'] = pynsca.NSCANotifier(self.servers[server]['host'],
                                                                   monitoring_port=int(self.servers[server]['port']),
                                                                   encryption_mode=int(self.servers[server]['encryption_mode']),
                                                                   password=self.servers[server]['password'])


    def send_result(self, return_code, output, service_description=''):
        '''
        Send results
        '''
        for server in self.servers:
            if self.servers[server]['availability']:
                try:
                    self.servers[server]['notifier'].svc_result(self.servers[server]['custom_fqdn'],
                                                                service_description,
                                                                int(return_code),
                                                                str(output))
                    logging.info("[nsca][%s][%s]: Data sent", service_description, self.servers[server]['host'])
                except (socket.gaierror, socket.error), error:
                    self.servers[server]['availability'] = False
                    logging.error("[nsca][%s][%s]: %s", service_description, self.servers[server]['host'], error[1])
            else:
                logging.error("[nsca][%s][%s]: Data not sent, server is unavailable", service_description, self.servers[server]['host'])