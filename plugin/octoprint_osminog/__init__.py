import collections
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
        self._filament_checks = collections.deque([])
        self._last_available = None

        self.port = self._settings.get(["port"])
        try:
            self.check_count = int(self._settings.get(["check_count"]))
        except (ValueError, TypeError):
            self.check_count = 2

        self._osminog_port = None
        self.connect()

    def connect(self):
        if not self.port:
            self._logger.info(
                "Cannot connect; no port specified.",
            )
            return

        if self._osminog_port:
            self._osminog_port.close()

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

        while True:
            try:
                return self._send_command(command)
            except serial.serialutil.SerialException as e:
                self._logger.error(
                    "Serial connection lost: %s; reconnecting...",
                    str(e)
                )
                self.connect()
                time.sleep(1)

    def _send_command(self, command):
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
        if event == Events.PRINT_PAUSED:
            self.send_command("BUZZER")
            time.sleep(0.5)
            self.send_command("BUZZER")
            time.sleep(0.5)
            self.send_command("BUZZER")

        if (
            time.time() >
            (self._last_filament_check + self.CHECK_INTERVAL)
        ):
            try:
                self._do_filament_check()
                self._last_filament_check = time.time()
            except (ValueError, TypeError):
                pass

    def _do_filament_check(self):
        available = int(self.send_command('FILAMENT'))

        self._filament_checks.append(available)
        while(len(self._filament_checks) > self.check_count):
            self._filament_checks.popleft()

        if all(not check for check in self._filament_checks):
            self._printer.pause_print()

    def get_template_configs(self):
        return [
            {
                'type': 'settings',
                'custom_bindings': False,
            }
        ]

    def get_settings_defaults(self):
        return {
            'port': '',
            'check_count': '2',
        }

    def on_settings_save(self, data):
        octoprint.plugin.SettingsPlugin.on_settings_save(self, data)
        self.connect()


__plugin_name__ = 'Osminog'
__plugin_implementation__ = OsminogPlugin()
