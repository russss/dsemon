from __future__ import division, absolute_import, print_function, unicode_literals
from time import sleep, time
import logging

from gencomm import GenCommClient, GenCommError
from sentinel import Sentinel
from constants import control_modes


class DSEMon(object):
    def __init__(self):
        self.log = logging.getLogger(__name__)

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
        if not self.client.test():
            self.log.error("Unable to connect to generator.")
            return
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
            self.save_data(control_mode, basic, derived, alarms)
            sleep(5)

    def get_uptime(self):
        with open('/proc/uptime', 'r') as f:
            return f.readline().split(' ')[0]

    def save_data(self, control_mode, basic, derived, alarms):
        gentag = 'generator=test'
        with open('/var/lib/dsemon.log', 'a') as f:
            f.write(self.metric_line('control_mode', control_mode))
            for m in [basic, derived]:
                f.writelines(self.dict_to_metrics(m))

    def dict_to_metrics(self, d):
        for key, value in d.items():
            if isinstance(value, Sentinel):
                continue
            if isinstance(value, (list, tuple)):
                i = 1
                for item in value:
                    yield self.metric_line(key + '_%s' % i, item)
                    i += 1
            else:
                yield self.metric_line(key, value)

    def metric_line(self, name, value):
        return "%s,%s value=%s %s\n" % (name, 'generator=test', value, int(time()))



if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    DSEMon().run()
