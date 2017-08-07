import time

import serial

import octoprint.plugin
from octoprint.events import Events


class OsminogPlugin(
    octoprint.plugin.StartupPlugin,
    octoprint.plugin.EventHandlerPlugin,
    octoprint.plugin.TemplatePlugin,
    octoprint.plugin.SettingsPlugin,
):
    CHECK_INTERVAL = 10

    def initialize(self):
        self._last_filament_check = 0
        self._printer_paused = False

        port = self._settings.get(["port"])
        self._osminog_port = None
        if port:
            try:
                self._osminog_port = serial.Serial(self._settings.get(["port"]))
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

        self._osminog_port.write(command.encode('utf8'))
        return self._osminog_port.readline().strip()

    def on_event(self, event, payload):
        if event == Events.PRINT_STARTED:
            self.send_command('POWERON')
        if event in (
            Events.PRINT_STOPPED,
            Events.PRINT_FAILED,
            Events.PRINT_CANCELLED,
        ):
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


__plugin_name__ = 'Osminog'
__plugin_implementation__ = OsminogPlugin()