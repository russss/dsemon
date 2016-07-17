from __future__ import division, absolute_import, print_function, unicode_literals
from time import sleep
import logging
from enum import Enum
import minimalmodbus
from minimalmodbus import SlaveDeviceBusyError

from sentinel import sentinel_16u, sentinel_16s, sentinel_32u, sentinel_32s, SENTINEL_PAGES

def extract_bit(value, bit):
    return (value >> bit & 1) == 1

class GenCommError(Exception):
    pass


class GenCommClient(object):
    def __init__(self, port, address=10):
        self.log = logging.getLogger(__name__)
        self.port = port
        self.address = address
        self.connect()

    def connect(self):
        self.instrument = minimalmodbus.Instrument(self.port, self.address)
        #self.instrument.debug = True
        self.instrument.serial.stopbits = 2

    def test(self):
        return self.read_register(1, 0) == self.address

    def read_register(self, page, address, scale=1, bits=16, signed=False):
        self.log.debug("Reading page: %s, address: %s", page, address)
        sleep(0.1)
        try:
            self._read_register(page, address, scale, bits, signed)
        except SlaveDeviceBusyError:
            self.log.debug("Slave busy, sleeping")
            sleep(0.1)
        except (ValueError, IOError) as e:
            self.log.debug("Error in read: %s", e)

        retry_count = 5
        while retry_count > 0:
            try:
                result = self._read_register(page, address, scale, bits, signed)
                self.log.debug("Result: %r", result)
                return result
            except SlaveDeviceBusyError:
                self.log.debug("Slave busy.")
            except (ValueError, IOError) as e:
                self.log.debug("Error in read: %s", e)
            retry_count -= 1
            sleep((5 - retry_count) * 0.1)
        raise GenCommError("Read failed.")

    def _read_register(self, page, address, scale, bits, signed):
        coil = (page * 256) + address
        if bits == 16:
            value = self.instrument.read_register(coil, signed=signed)
            if page in SENTINEL_PAGES:
                if not signed and value in sentinel_16u:
                    return sentinel_16u[value]
                elif signed and value in sentinel_16s:
                    return sentinel_16s[value]
        elif bits == 32:
            value = self.instrument.read_long(coil, signed=signed)
            if page in SENTINEL_PAGES:
                if not signed and value in sentinel_32u:
                    return sentinel_32u[value]
                elif signed and value in sentinel_32s:
                    return sentinel_32s[value]

        return value * scale

    def get_status(self):
        return {'manufacturer_id': self.read_register(3, 0),
                'model_id': self.read_register(3, 1),
                'serial_number': self.read_register(3, 2, bits=32),
                'control_mode': self.read_register(3, 4)}

    def get_alarm(self):
        value = self.read_register(3, 6)
        return {'control_unit_not_configured': extract_bit(value, 16),
                'control_unit_failure': extract_bit(value, 14),
                'shutdown_alarm': extract_bit(value, 13),
                'electrical_trip_alarm': extract_bit(value, 12),
                'warning_alarm': extract_bit(value, 11),
                'telemetry_alarm': extract_bit(value, 10),
                'satellite_telemetry_alarm': extract_bit(value, 9),
                'no_font_file': extract_bit(value, 8)}

    def get_basic_instrumentation(self):
        return {'oil_pressure': self.read_register(4, 0),
                'coolant_temperature': self.read_register(4, 1, signed=True),
                'fuel_level': self.read_register(4, 3),
                'alternator_voltage': self.read_register(4, 4, scale=0.1),
                'battery_voltage': self.read_register(4, 5, scale=0.1),
                'engine_speed': self.read_register(4, 6),
                'frequency': self.read_register(4, 7, scale=0.1),
                'l_n_voltage': (self.read_register(4, 8, bits=32, scale=0.1),
                                self.read_register(4, 10, bits=32, scale=0.1),
                                self.read_register(4, 12, bits=32, scale=0.1)),
                'l_l_voltage': (self.read_register(4, 14, bits=32, scale=0.1),
                                self.read_register(4, 16, bits=32, scale=0.1),
                                self.read_register(4, 18, bits=32, scale=0.1)),
                'l_current':   (self.read_register(4, 20, bits=32, scale=0.1),
                                self.read_register(4, 22, bits=32, scale=0.1),
                                self.read_register(4, 24, bits=32, scale=0.1)),
                'earth_current': self.read_register(4, 26, bits=32, scale=0.1),
                'l_power':     (self.read_register(4, 28, bits=32, signed=True),
                                self.read_register(4, 30, bits=32, signed=True),
                                self.read_register(4, 32, bits=32, signed=True)),
                'current_theta': self.read_register(4, 34, signed=True)
               }

    def get_derived_instrumentation(self):
        return {'true_power': self.read_register(5, 0, bits=32, signed=True),
                'l_apparent_power': (self.read_register(5, 2, bits=32),
                                   self.read_register(5, 4, bits=32),
                                   self.read_register(5, 6, bits=32)),
                'apparent_power': self.read_register(5, 8, bits=32),
                'l_reactive_power': (self.read_register(5, 10, bits=32),
                                   self.read_register(5, 12, bits=32),
                                   self.read_register(5, 14, bits=32)),
                'reactive_power': self.read_register(5, 16, bits=32),
                'l_power_factor': (self.read_register(5, 18, scale=0.01, signed=True),
                                   self.read_register(5, 19, scale=0.01, signed=True),
                                   self.read_register(5, 20, scale=0.01, signed=True)),
                'power_factor': self.read_register(5, 21, signed=True),
                'true_power_capacity': self.read_register(5, 22, scale=0.1, signed=True),
                'reactive_power_capacity': self.read_register(5, 23, scale=0.1, signed=True)
               }

    def get_diagnostic_general(self):
        return {'software_version': self.read_register(11, 0, scale=0.01),
                'cpu_usage': self.read_register(11, 1),
                'last_button_pressed': self.read_register(11, 2),
                'backup_supply_voltage': self.read_register(11, 3)
        }

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    c = GenCommClient('/dev/ttyAMA0')
    #print(c.get_status())
    print(c.get_basic_instrumentation())
    print(c.get_derived_instrumentation())
