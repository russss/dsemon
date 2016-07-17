from __future__ import division, absolute_import, print_function, unicode_literals
from time import sleep
import logging
from gencomm import GenCommClient, GenCommError
from constants import control_modes


class DSEMon(object):
    def __init__(self):
        self.log = logging.getLogger(__name__)
        self.fetch_frequency = 10

    def run(self):
        while True:
            try:
                self.main()
            except GenCommError:
                self.log.exception("Communications error, retrying in 5 seconds...")
            sleep(5)

    def main(self):
        self.log.info("DSEMon starting...")
        self.client = GenCommClient('/dev/ttyAMA0')
        diagnostic_general = self.client.get_diagnostic_general()
        status = self.client.get_status()

        self.log.info("Established communication with manufacturer: %s, model: %s, serial: %s. Controller version: %s",
                      status['manufacturer_id'], status['model_id'], status['serial_number'], diagnostic_general['software_version'])

        while True:
            control_mode = self.client.read_register(3, 4)
            basic = self.client.get_basic_instrumentation()
            derived = self.client.get_derived_instrumentation()
            alarms = self.client.get_alarm()
            self.log.info("Control mode: %s, battery voltage: %sV, generator power capacity: %s%%",
                          control_modes.get(control_mode, 'Unknown'), basic['battery_voltage'], derived['true_power_capacity'])

            alarm_strings = []
            for alarm, state in alarms.items():
                if state:
                    alarm_strings.append(alarm)
            if len(alarm_strings) > 0:
                self.log.info("ACTIVE ALARMS: %s", ", ".join(alarm_strings))
            sleep(5)



if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    DSEMon().run()
