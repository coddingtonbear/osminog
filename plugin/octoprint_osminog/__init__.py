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
    MAX_ATTEMPTS = 5

    BUZZER_BEEPS = 5
    BUZZER_DELAY = 0.3

    def initialize(self):
        self._last_filament_check = 0
        self.port = self._settings.get(["port"])
        self._osminog_port = None
        self.connect()

    def connect(self, close_existing=False):
        if not self.port:
            self._logger.info(
                "Cannot connect; no port specified.",
            )
            return False

        if self._osminog_port and close_existing:
            try:
                self._osminog_port.close()
            except Exception as e:
                self._logger.error(
                    "Unable to close existing connection: %s",
                    str(e)
                )
        elif self._osminog_port:
            self._logger.debug(
                "Already connected; leaving existing connection as-is."
            )
            return True

        try:
            self._osminog_port = serial.Serial(
                self._settings.get(["port"]),
                timeout=2
            )
            return True
        except Exception as e:
            self._logger.error(
                "Unable to connect to port %s: %s",
                self._settings.get(["port"]),
                str(e),
            )

    def send_command(self, command):
        attempt_count = 0
        while True:
            attempt_count += 1
            if attempt_count > self.MAX_ATTEMPTS:
                logger.error(
                    "Exceeded max attempts at sending command %s: aborting.",
                    command,
                )
                return

            try:
                if not self.connect():
                    continue
                return self._send_command(command)
            except serial.serialutil.SerialException as e:
                self._logger.error(
                    "Serial connection lost: %s; reconnecting...",
                    str(e)
                )
                time.sleep(1)

    def _send_command(self, command):
        self._osminog_port.reset_input_buffer()
        self._osminog_port.write(command.encode('utf8') + b'\r\n')
        response = self._osminog_port.readline().strip()
        self._logger.debug(
            "Osminog Command: %s -> %s",
            command,
            response,
        )
        return response

    def on_event(self, event, payload):
        if event == Events.POWER_ON:
            self._logger.info(
                "%s event detected; powering on.",
                event,
            )
            self.send_command('POWERON')
        if event == Events.POWER_OFF:
            self._logger.info(
                "%s event detected; powering off.",
                event,
            )
            self.send_command('POWEROFF')
        if event in (
            Events.PRINT_PAUSED,
            Events.PRINT_DONE,
        ):
            self._logger.info(
                "%s event detected; buzzing buzzer.",
                event,
            )
            for _ in xrange(self.BUZZER_BEEPS):
                self.send_command("BUZZER")
                time.sleep(self.BUZZER_DELAY)

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

        if not available:
            # Double-check:
            available = int(self.send_command('FILAMENT'))
            if not available:
                self._logger.warning(
                    "Filament outage detected; pausing print.",
                )
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
        }

    def on_settings_save(self, data):
        octoprint.plugin.SettingsPlugin.on_settings_save(self, data)
        self.connect(close_existing=True)


__plugin_name__ = 'Osminog'
__plugin_implementation__ = OsminogPlugin()
