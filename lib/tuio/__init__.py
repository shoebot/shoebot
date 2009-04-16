# -*- coding: utf-8 -*-
"""A Python library that understands the TUIO protocol"""

__author__    = "Jannis Leidel"
__version__   = "0.1"
__copyright__ = "Copyright (c) 2007-2008 Jannis Leidel"
__license__   = "MIT"
__url__       = "http://code.google.com/p/pytuio/"

import os
import sys
import math
import socket
import inspect

import OSC
import profiles

class CallbackError(Exception):
    pass

class Tracking(object):
    def __init__(self, host='127.0.0.1', port=3333):
        self.host = host
        self.port = port
        self.current_frame = 0
        self.last_frame = 0

        self.open_socket()
        self.manager = OSC.CallbackManager()
        self.profiles = self.load_profiles()

    def open_socket(self):
        """
        Opens the socket and binds to the given host and port. Uses
        SO_REUSEADDR to be as robust as possible.
        """
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.setblocking(0)
        self.socket.bind((self.host, self.port))
    start = open_socket

    def close_socket(self):
        """
        Closes the socket connection
        """
        self.socket.close()
    stop = close_socket

    def refreshed(self):
        """
        Returns True if there was a new frame
        """
        return self.current_frame >= self.last_frame
    
    def load_profiles(self):
        """
        Loads all possible TUIO profiles and returns a dictionary with the
        profile addresses as keys and an instance of a profile as the value 
        """
        _profiles = {}
        for name, klass in inspect.getmembers(profiles):
            if inspect.isclass(klass) and name.endswith('Profile') and name != 'TuioProfile':
                # Adding profile to the self.profiles dictionary
                profile = klass()
                _profiles[profile.address] = profile
                # setting convenient variable to access objects of profile
                try:
                    setattr(self, profile.list_label, profile.objs)
                except AttributeError:
                    continue
                # Mapping callback method to every profile
                self.manager.add(self.callback, profile.address)
        return _profiles
    
    def get_profile(self, profile):
        """Returns a specific profile from the profile list and otherwise None"""
        return self.profiles.get(profile, None)
    
    def get_helpers(self):
        """Returns a list of helper functions that provide access to the
        objects of each profile."""
        return list([profile.list_label for profile in self.profiles.values()])

    def update(self):
        """
        Tells the connection manager to receive the next 1024 byte of messages
        to analyze.
        """
        try:
            self.manager.handle(self.socket.recv(1024))
        except socket.error:
            pass

    def callback(self, *incoming):
        """
        Gets called by the CallbackManager if a new message was received 
        """
        message = incoming[0]
        if message:
            address, command = message[0], message[2]
            profile = self.get_profile(address)
            if profile is not None:
                try:
                    getattr(profile, command)(self, message)
                except AttributeError:
                    pass
