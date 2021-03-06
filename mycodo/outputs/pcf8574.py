# coding=utf-8
#
# pcf8574.py - Output for PCF8574
#
from flask_babel import lazy_gettext

from mycodo.databases.models import OutputChannel
from mycodo.outputs.base_output import AbstractOutput
from mycodo.utils.database import db_retrieve_table_daemon


def constraints_pass_positive_value(mod_dev, value):
    """
    Check if the user input is acceptable
    :param mod_input: SQL object with user-saved Input options
    :param value: float or int
    :return: tuple: (bool, list of strings)
    """
    errors = []
    all_passed = True
    # Ensure value is positive
    if value <= 0:
        all_passed = False
        errors.append("Must be a positive value")
    return all_passed, errors, mod_dev


# Measurements
measurements_dict = {
    0: {
        'measurement': 'duration_time',
        'unit': 's',
    },
    1: {
        'measurement': 'duration_time',
        'unit': 's',
    },
    2: {
        'measurement': 'duration_time',
        'unit': 's',
    },
    3: {
        'measurement': 'duration_time',
        'unit': 's',
    },
    4: {
        'measurement': 'duration_time',
        'unit': 's',
    },
    5: {
        'measurement': 'duration_time',
        'unit': 's',
    },
    6: {
        'measurement': 'duration_time',
        'unit': 's',
    },
    7: {
        'measurement': 'duration_time',
        'unit': 's',
    }
}

channels_dict = {
    0: {
        'name': 'Channel 1',
        'types': ['on_off'],
        'measurements': [0]
    },
    1: {
        'name': 'Channel 2',
        'types': ['on_off'],
        'measurements': [1]
    },
    2: {
        'name': 'Channel 3',
        'types': ['on_off'],
        'measurements': [2]
    },
    3: {
        'name': 'Channel 4',
        'types': ['on_off'],
        'measurements': [3]
    },
    4: {
        'name': 'Channel 5',
        'types': ['on_off'],
        'measurements': [4]
    },
    5: {
        'name': 'Channel 6',
        'types': ['on_off'],
        'measurements': [5]
    },
    6: {
        'name': 'Channel 7',
        'types': ['on_off'],
        'measurements': [6]
    },
    7: {
        'name': 'Channel 8',
        'types': ['on_off'],
        'measurements': [7]
    }
}

# Output information
OUTPUT_INFORMATION = {
    'output_name_unique': 'PCF8574',
    'output_name': "{} PCF8574 (8 Channels)".format(lazy_gettext('On/Off')),
    'output_library': 'smbus2',
    'measurements_dict': measurements_dict,
    'channels_dict': channels_dict,
    'output_types': ['on_off'],

    'url_manufacturer': 'https://www.ti.com/product/PCF8574',
    'url_datasheet': 'https://www.ti.com/lit/ds/symlink/pcf8574.pdf',
    'url_product_purchase': 'https://www.amazon.com/gp/product/B07JGSNWFF',

    'message': 'Controls the 8 channels of the PCF8574.',

    'options_enabled': [
        'i2c_location',
        'button_on',
        'button_send_duration'
    ],
    'options_disabled': ['interface'],

    'dependencies_module': [
        ('pip-pypi', 'smbus2', 'smbus2')
    ],

    'interfaces': ['I2C'],
    'i2c_location': [
        '0x20', '0x21', '0x22', '0x23', '0x24', '0x25', '0x26', '0x27',
        '0x38', '0x39', '0x3a', '0x3b', '0x3c', '0x3d', '0x3e', '0x3f'
    ],
    'i2c_address_editable': False,
    'i2c_address_default': '0x20',

    'custom_channel_options': [
        {
            'id': 'name',
            'type': 'text',
            'default_value': '',
            'required': False,
            'name': lazy_gettext('Name'),
            'phrase': lazy_gettext('A name for this channel')
        },
        {
            'id': 'state_startup',
            'type': 'select',
            'default_value': 0,
            'options_select': [
                (0, 'Off'),
                (1, 'On')
            ],
            'name': lazy_gettext('Startup State'),
            'phrase': lazy_gettext('Set the state of the GPIO when Mycodo starts')
        },
        {
            'id': 'state_shutdown',
            'type': 'select',
            'default_value': 0,
            'options_select': [
                (0, 'Off'),
                (1, 'On')
            ],
            'name': lazy_gettext('Shutdown State'),
            'phrase': lazy_gettext('Set the state of the GPIO when Mycodo shuts down')
        },
        {
            'id': 'on_state',
            'type': 'select',
            'default_value': 1,
            'options_select': [
                (1, 'HIGH'),
                (0, 'LOW')
            ],
            'name': lazy_gettext('On State'),
            'phrase': lazy_gettext('The state of the GPIO that corresponds to an On state')
        },
        {
            'id': 'trigger_functions_startup',
            'type': 'bool',
            'default_value': False,
            'name': lazy_gettext('Trigger Functions at Startup'),
            'phrase': lazy_gettext('Whether to trigger functions when the output switches at startup')
        },
        {
            'id': 'amps',
            'type': 'float',
            'default_value': 0.0,
            'required': True,
            'name': lazy_gettext('Current (Amps)'),
            'phrase': lazy_gettext('The current draw of the device being controlled')
        }
    ]
}


class OutputModule(AbstractOutput):
    """ An output support class that operates an output """
    def __init__(self, output, testing=False):
        super(OutputModule, self).__init__(output, testing=testing, name=__name__)

        self.sensor = None

        output_channels = db_retrieve_table_daemon(
            OutputChannel).filter(OutputChannel.output_id == output.unique_id).all()
        self.options_channels = self.setup_custom_channel_options_json(
            OUTPUT_INFORMATION['custom_channel_options'], output_channels)

    def setup_output(self):
        import smbus2

        self.setup_on_off_output(OUTPUT_INFORMATION)

        if self.output.i2c_location:
            self.sensor = PCF8574(smbus2, self.output.i2c_bus, int(str(self.output.i2c_location), 16))
            self.output_setup = True

        for channel in channels_dict:
            if self.options_channels['state_startup'][channel] == '1':
                self.output_switch('on', output_channel=channel)
            elif self.options_channels['state_startup'][channel] == '0':
                self.output_switch('off', output_channel=channel)
            else:
                continue
            if self.options_channels['trigger_functions_startup'][channel]:
                self.check_triggers(self.unique_id, output_channel=channel)

    def output_switch(self,
                      state,
                      output_type=None,
                      amount=None,
                      duty_cycle=None,
                      output_channel=None):
        if output_channel is None:
            self.logger.error("Output channel needs to be specified")
            return

        try:
            list_states = []
            for channel in channels_dict:
                if output_channel == channel:
                    if state == 'on':
                        list_states.append(self.options_channels['on_state'][channel])
                    elif state == 'off':
                        list_states.append(not self.options_channels['on_state'][channel])
                else:
                    list_states.append(self.output_states[channel])
            self.sensor.port = list_states
            self.output_states[output_channel] = list_states[output_channel]
            msg = "success"
        except Exception as e:
            msg = "CH{} state change error: {}".format(output_channel, e)
            self.logger.error(msg)
        return msg

    def is_on(self, output_channel=None):
        if self.is_setup():
            if output_channel is not None and output_channel in self.output_states:
                return self.output_states[output_channel]
            else:
                return self.output_states

    def is_setup(self):
        return self.output_setup

    def stop_output(self):
        """ Called when Output is stopped """
        for channel in channels_dict:
            if self.options_channels['state_shutdown'][channel] == '1':
                self.output_switch('on', output_channel=channel)
            elif self.options_channels['state_shutdown'][channel] == '0':
                self.output_switch('off', output_channel=channel)
        self.running = False


class IOPort(list):
    """ Represents the PCF8574 IO port as a list of boolean values """
    def __init__(self, pcf8574, *args, **kwargs):
        super(IOPort, self).__init__(*args, **kwargs)
        self.pcf8574 = pcf8574

    def __setitem__(self, key, value):
        """ Set an individual output pin """
        self.pcf8574.set_output(key, value)

    def __repr__(self):
        """ Represent port as a list of booleans """
        state = self.pcf8574.bus.read_byte(self.pcf8574.address)
        ret = []
        for i in range(8):
            ret.append(bool(state & 1 << i))
        return repr(ret)

    def __len__(self):
        return 8

    def __iter__(self):
        for i in range(8):
            yield self[i]

    def __reversed__(self):
        for i in range(8):
            yield self[7-i]


class PCF8574(object):
    """ A software representation of a single PCF8574 IO expander chip """
    def __init__(self, smbus, i2c_bus, i2c_address):
        self.bus_no = i2c_bus
        self.bus = smbus.SMBus(i2c_bus)
        self.address = i2c_address

    def __repr__(self):
        return "PCF8574(i2c_bus_no=%r, address=0x%02x)" % (self.bus_no, self.address)

    @property
    def port(self):
        """ Represent IO port as a list of boolean values """
        return IOPort(self)

    @port.setter
    def port(self, value):
        """ Set the whole port using a list """
        assert isinstance(value, list)
        assert len(value) == 8
        new_state = 0
        for i, val in enumerate(value):
            if val:
                new_state |= 1 << i
        self.bus.write_byte(self.address, new_state)

    def set_output(self, output_number, value):
        """ Set a specific output high (True) or low (False) """
        assert output_number in range(8), "Output number must be an integer between 0 and 7"
        current_state = self.bus.read_byte(self.address)
        bit = 1 << output_number
        new_state = current_state | bit if value else current_state & (~bit & 0xff)
        self.bus.write_byte(self.address, new_state)
