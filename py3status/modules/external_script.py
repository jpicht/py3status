"""
Display output of a given shell command.

Display output of the shell command set by `script_path`. By default
(`input_format` = 'text') only the first two lines of output will be used. The
first line is used as the displayed text. If the output has two or more lines,
the second line is set as the text color (and should hence be a valid hex color
code such as #FF0000 for red).

If `input_format` is set to 'i3bar' the input is parsed as a single 'i3bar'
protocol item. In this mode `format`, `localize`, `strip_output`,
`convert_numbers`, and `button_show_notification` are ignored.

Configuration parameters:
    button_show_notification: button to show notification with full output
        (default None)
    cache_timeout: how often we refresh this module in seconds
        (default 15)
    convert_numbers: convert decimal numbers to a numeric type
        (default True)
    format: see placeholders below (default '{output}')
    input_format: specify input format, either 'text' or 'i3bar'
        (default 'text')
    localize: should script output be localized (if available)
        (default True)
    script_path: script you want to show output of (compulsory)
        (default None)
    strip_output: shall we strip leading and trailing spaces from output
        (default False)

Format placeholders:
    {lines} number of lines in the output
    {output} output of script given by "script_path"

Examples:
```
external_script {
    format = "my name is {output}"
    script_path = "/usr/bin/whoami"
}

external_script {
    script_path = "/home/user/go/bin/k8s_status_i3bar"
    input_format = "i3bar"
}
```

@author frimdo ztracenastopa@centrum.cz

SAMPLE OUTPUT
{'full_text': 'script output'}

example
{'full_text': 'It is now: Wed Feb 22 22:24:13'}
"""

import json
from os import chmod, unlink
import re

STRING_ERROR_MISSING_PATH = "missing script_path"
STRING_ERROR_INPUT_FORMAT = "invalid input format"

STRING_TEST_SCRIPT = """
#!/bin/bash

echo '{testdata}'

"""

class Py3status:
    """
    """

    # available configuration parameters
    button_show_notification = None
    cache_timeout = 15
    convert_numbers = True
    format = "{output}"
    input_format = "text"
    localize = True
    script_path = None
    strip_output = False

    def post_config_hook(self):
        if not self.script_path:
            raise Exception(STRING_ERROR_MISSING_PATH)

        if self.input_format not in ("text", "i3bar"):
            raise Exception(STRING_ERROR_INPUT_FORMAT)

    def external_script(self):
        try:
            self.output = self.py3.command_output(
                self.script_path, shell=True, localized=self.localize
            )
        except self.py3.CommandError as e:
            # something went wrong show error to user
            output = e.output or e.error
            self.py3.error(output)

        if self.input_format == "i3bar":
            return json.loads(self.output)

        response = {}
        response["cached_until"] = self.py3.time_in(self.cache_timeout)
        output_lines = self.output.splitlines()
        if len(output_lines) > 1:
            output_color = output_lines[1]
            if re.search(r"^#[0-9a-fA-F]{6}$", output_color):
                response["color"] = output_color

        if output_lines:
            output = output_lines[0]
            if self.strip_output:
                output = output.strip()
            # If we get something that looks numeric then we convert it
            # to a numeric type because this can be helpful. for example:
            #
            # external_script {
            #     format = "file is [\?if=output>10 big|small]"
            #     script_path = "cat /tmp/my_file | wc -l"
            # }
            if self.convert_numbers is True:
                try:
                    output = int(output)
                except ValueError:
                    try:
                        output = float(output)
                    except ValueError:
                        pass
        else:
            output = ""

        response["full_text"] = self.py3.safe_format(
            self.format, {"output": output, "lines": len(output_lines)}
        )
        return response

    def on_click(self, event):
        button = event["button"]
        if button == self.button_show_notification:
            self.py3.notify_user(self.output)
            self.py3.prevent_refresh()


if __name__ == "__main__":
    """
    Run module in test mode.
    """
    from py3status.module_test import module_test

    module_test(Py3status)
