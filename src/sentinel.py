from __future__ import division, absolute_import, print_function, unicode_literals
from enum import Enum
class Sentinel(object):
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "[%s]" % self.name

s_unimplemented =    Sentinel('Unimplemented')
s_over_range =       Sentinel('Over measurable range')
s_under_range =      Sentinel('Under measurable range')
s_transducer_fault = Sentinel('Transducer fault')
s_bad_data =         Sentinel('Bad Data')
s_digital_high =     Sentinel('High digital input')
s_digital_low =      Sentinel('Low digital input')
s_reserved =         Sentinel('Reserved')

SENTINEL_VALUES = [s_unimplemented, s_over_range, s_under_range, s_transducer_fault,
                   s_bad_data, s_digital_high, s_digital_low, s_reserved]

sentinel_16u = {
    0xFFFF: s_unimplemented,
    0xFFFE: s_over_range,
    0xFFFD: s_under_range,
    0xFFFC: s_transducer_fault,
    0xFFFB: s_bad_data,
    0xFFFA: s_digital_high,
    0xFFF9: s_digital_low,
    0xFFF8: s_reserved
}

sentinel_16s = {
    0x7FFF: s_unimplemented,
    0x7FFE: s_over_range,
    0x7FFD: s_under_range,
    0x7FFC: s_transducer_fault,
    0x7FFB: s_bad_data,
    0x7FFA: s_digital_high,
    0x7FF9: s_digital_low,
    0x7FF8: s_reserved
}

sentinel_32u = {
    0xFFFFFFFF: s_unimplemented,
    0xFFFFFFFE: s_over_range,
    0xFFFFFFFD: s_under_range,
    0xFFFFFFFC: s_transducer_fault,
    0xFFFFFFFB: s_bad_data,
    0xFFFFFFFA: s_digital_high,
    0xFFFFFFF9: s_digital_low,
    0xFFFFFFF8: s_reserved
}

sentinel_32s = {
    0x7FFFFFFF: s_unimplemented,
    0x7FFFFFFE: s_over_range,
    0x7FFFFFFD: s_under_range,
    0x7FFFFFFC: s_transducer_fault,
    0x7FFFFFFB: s_bad_data,
    0x7FFFFFFA: s_digital_high,
    0x7FFFFFF9: s_digital_low,
    0x7FFFFFF8: s_reserved
}

SENTINEL_PAGES = [4, 6, 7]

