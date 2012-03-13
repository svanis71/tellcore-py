# Copyright (c) 2012 Erik Johansson <erik@ejohansson.se>
# 
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307
# USA

from .constants import *
from .library import *


class TelldusCore(object):
    def __init__(self):
        object.__init__(self)
        self.lib = Library()

    def devices(self):
        devices = []
        count = self.lib.tdGetNumberOfDevices()
        for i in range(0, count):
            id_ = self.lib.tdGetDeviceId(i)
            devices.append(Device(id_))
        return devices

    def sensors(self):
        sensors = []
        try:
            sensor = self.lib.tdSensor()
            sensor['id_'] = sensor['id']
            del sensor['id']
            sensors.append(Sensor(**sensor))
        except TelldusError as e:
            if e.error == TELLSTICK_ERROR_DEVICE_NOT_FOUND:
                pass
            raise
        return sensors

    def controllers(self):
        controllers = []
        try:
            controller = self.lib.tdController()
            controller['id_'] = controller['id']
            controller['type_'] = controller['type']
            del controller['id'], controller['type']
            controllers.append(Controller(**controller))
        except TelldusError as e:
            if e.error == TELLSTICK_ERROR_NOT_FOUND:
                pass
            raise
        return controllers

    def add_device(self, name, protocol, model=None, **parameters):
        device = Device(self.lib.tdAddDevice())
        device.name = name
        device.protocol = protocol
        if model is not None:
            device.model = model
        for key, value in parameters.items():
            device.set_parameter(key, value)
        return device

    def send_raw_command(self, command, reserved=0):
        return self.lib.tdSendRawCommand(command, reserved)

    def connect_controller(self, vid, pid, serial):
        self.lib.tdConnectTellStickController(vid, pid, serial)

    def disconnect_controller(self, vid, pid, serial):
        self.lib.tdDisconnectTellStickController(vid, pid, serial)

class Device(object):
    def __init__(self, id_):
        object.__init__(self)
        object.__setattr__(self, 'id', id_)
        object.__setattr__(self, 'lib', Library())

    def remove(self):
        return self.lib.tdRemoveDevice(self.id)

    def __getattr__(self, name):
        if name == 'name':
            func = self.lib.tdGetName
        elif name == 'protocol':
            func = self.lib.tdGetProtocol
        elif name == 'model':
            func = self.lib.tdGetModel
        elif name == 'type':
            func = self.lib.tdGetDeviceType
        else:
            raise AttributeError(name)
        return func(self.id)

    def __setattr__(self, name, value):
        if name == 'name':
            func = self.lib.tdSetName
        elif name == 'protocol':
            func = self.lib.tdSetProtocol
        elif name == 'model':
            func = self.lib.tdSetModel
        else:
            raise AttributeError(name)
        return func(self.id, value)

    def __str__(self):
        desc = '/'.join([self.name, self.protocol, self.model])
        return "device-%d [%s]" % (self.id, desc)

    def get_parameter(self, name, default_value):
        return self.lib.tdGetDeviceParameter(self.id, name, default_value)

    def set_parameter(self, name, value):
        return self.lib.tdSetDeviceParameter(self.id, name, value)

    def turn_on(self):
        self.lib.tdTurnOn(self.id)

    def turn_off(self):
        self.lib.tdTurnOff(self.id)

    def bell(self):
        self.lib.tdBell(self.id)

    def dim(self, level):
        self.lib.tdDim(self.id, level)

    def execute(self):
        self.lib.tdExecute(self.id)

    def up(self):
        self.lib.tdUp(self.id)

    def down(self):
        self.lib.tdDown(self.id)

    def stop(self):
        self.lib.tdStop(self.id)

    def learn(self):
        self.lib.tdLearn(self.id)

    def methods(self, methods_supported):
        return self.lib.tdMethods(self.id, methods_supported)

    def last_sent_command(self, methods_supported):
        return self.lib.tdLastSentCommand(self.id, methods_supported)

    def last_sent_value(self):
        return self.lib.tdLastSentValue(self.id)

class Sensor(object):
    def __init__(self, protocol, model, id_, datatypes):
        object.__init__(self)
        self.protocol = protocol
        self.model = model
        self.id = id_
        self.datatypes = datatypes
        self.lib = Library()

    def value(self, datatype):
        return self.lib.tdSensorValue(self.protocol, self.model, self.id,
                                      datatype)

class Controller(object):
    def __init__(self, id_, type_, name, available):
        object.__init__(self)
        object.__setattr__(self, 'id', id_)
        object.__setattr__(self, 'type', type_)
        object.__setattr__(self, 'name', name)
        object.__setattr__(self, 'available', available)
        object.__setattr__(self, 'lib', Library())
    
    def __getattr__(self, name):
        try:
            return self.lib.tdControllerValue(self.id, name)
        except TelldusError as e:
            if e.error == TELLSTICK_ERROR_METHOD_NOT_SUPPORTED:
                raise AttributeError(name)
            raise

    def __setattr__(self, name, value):
        try:
            self.lib.tdSetControllerValue(self.id, name, value)
        except TelldusError as e:
            if e.error == TELLSTICK_ERROR_SYNTAX:
                raise AttributeError(name)
            raise
