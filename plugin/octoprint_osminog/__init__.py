import time

import serial

import octoprint.plugin
from octoprint.events import Events


class OsminogPlugin(
    octoprint.plugin.StartupPlugin,
    octoprint.plugin.EventHandlerPlugin,
    octoprint.plugin.SettingsPlugin,
    octoprint.plugin.TemplatePlugin,
):
    CHECK_INTERVAL = 10

    def initialize(self):
        self._last_filament_check = 0
        self._printer_paused = False

        self.port = self._settings.get(["port"])
        self._osminog_port = None
        if self.port:
            self.connect()

    def connect(self):
        if self._osminog_port:
            self._osminog_port.close()

        self._osminog_port = None

        try:
            self._osminog_port = serial.Serial(
                self._settings.get(["port"]),
                timeout=2
            )
        except:
            self._logger.error(
                "Unable to connect to port %s",
                self._settings.get(["port"])
            )

    def send_command(self, command):
        if not self._osminog_port:
            self._logger.info(
                "No connection to osminog; not sending %s",
                command,
            )
            return

        self._osminog_port.reset_input_buffer()
        self._osminog_port.write(command.encode('utf8') + b'\r\n')
        self._logger.info(
            "Sending command: %s",
            command,
        )
        response = self._osminog_port.readline().strip()
        self._logger.info(
            "Received response: %s",
            response
        )

        return response

    def on_event(self, event, payload):
        if event == Events.POWER_ON:
            self.send_command('POWERON')
        if event == Events.POWER_OFF:
            self.send_command('POWEROFF')

        if time.time() > self._last_filament_check + self.CHECK_INTERVAL:
            self._do_filament_check()

    def _do_filament_check(self):
        available = self.send_command('FILAMENT')
        if available == '0':
            if not self._printer_paused:
                self._printer.pause_print()
                self._printer_paused = True
            self.send_command("BUZZER")

        self._last_filament_check = time.time()

    def get_template_configs(self):
        return [
            {
                'type': 'sidebar',
                'custom_bindings': False,
            },
            {
                'type': 'settings',
                'custom_bindings': False,
            }
        ]

    def get_settings_defaults(self):
        return {
            'port': '',
        }

    def on_settings_save(self, data):
        octoprint.plugin.SettingsPlugin.on_settings_save(self, data)
        self.connect()


__plugin_name__ = 'Osminog'
__plugin_implementation__ = OsminogPlugin()
