from tkinter import messagebox, ttk
from typing import List, Optional
import tkinter as tk

from thonny import get_workbench, languages
from thonny.config_ui import (
    ConfigurationPage,
    add_label_and_box_for_list_of_strings,
    add_option_checkbox,
    add_option_combobox,
    add_text_row,
    add_vertical_separator,
)
from thonny.languages import tr
from thonny.misc_utils import running_on_linux
from thonny.ui_utils import ems_to_pixels, get_last_grid_row


class GeneralConfigurationPage(ConfigurationPage):
    def __init__(self, master):
        super().__init__(master)

        add_option_checkbox(
            self, "general.single_instance", tr("Allow only single Thonny instance")
        )
        add_option_checkbox(self, "general.event_logging", tr("Log program usage events"))
        add_option_checkbox(
            self,
            "file.reopen_files",
            tr("Reopen files from previous session"),
        )
        if running_on_linux():
            import shutil

            if shutil.which("zenity"):
                add_option_checkbox(
                    self,
                    "file.use_zenity",
                    tr("Use Zenity file dialogs"),
                )

        add_option_checkbox(
            self,
            "general.disable_notification_sound",
            tr("Disable notification sound"),
        )
        add_option_checkbox(
            self,
            "general.debug_mode",
            tr("Debug mode (provides more detailed diagnostic logs)"),
        )

        add_vertical_separator(self)

        add_option_combobox(
            self,
            "general.language",
            tr("Language"),
            choices={value: key for (key, value) in languages.LANGUAGES_DICT.items()},
            width=20,
        )

        add_option_combobox(
            self, "general.ui_mode", tr("UI mode"), choices=["simple", "regular"], width=10
        )

        current_scaling = get_workbench().get_option("general.scaling")
        if current_scaling in ["default", "auto"]:
            initial_scaling = 1.5
        else:
            initial_scaling = max(0.5, min(16.0, round(float(current_scaling) * 2) / 2))

        scaling_row = self.grid_size()[1]
        ttk.Label(self, text=tr("UI scaling factor")).grid(
            row=scaling_row, column=0, sticky="w", padx=(0, ems_to_pixels(1))
        )
        scaling_value = tk.DoubleVar(self, value=initial_scaling)
        scaling_label = ttk.Label(self)
        scaling_label.grid(row=scaling_row, column=2, sticky="w")

        def update_scaling(value):
            value = round(float(value) * 2) / 2
            value = max(0.5, min(16.0, value))
            get_workbench().set_option("general.scaling", value)
            scaling_label.configure(text=f"{value:.1f}x")

        scaling_slider = tk.Scale(
            self,
            from_=0.5,
            to=16.0,
            orient=tk.HORIZONTAL,
            variable=scaling_value,
            resolution=0.5,
            length=ems_to_pixels(15),
            command=update_scaling,
            showvalue=False,
        )
        scaling_slider.grid(row=scaling_row, column=1, sticky="ew")
        scaling_label.configure(text=f"{initial_scaling:.1f}x")
        self.columnconfigure(1, weight=1)

        add_option_combobox(
            self,
            "general.font_scaling_mode",
            tr("Font scaling mode"),
            choices=["default", "extra", "automatic"],
            width=10,
        )

        add_vertical_separator(self)

        self.env_box = add_label_and_box_for_list_of_strings(
            self,
            tr("Environment variables (one KEY=VALUE per line)"),
            get_workbench().get_option("general.environment"),
        )
        self.rowconfigure(get_last_grid_row(self), weight=1)
        self.columnconfigure(1, weight=1)

        add_vertical_separator(self)

        add_text_row(
            self,
            tr("NB! Restart Thonny after changing these options!"),
            font="BoldTkDefaultFont",
        )

    def apply(self, changed_options: List[str]) -> bool:
        get_workbench().update_debug_mode()

        env = []
        for entry in self.env_box.text.get("1.0", "end").strip("\r\n").splitlines():
            entry = entry.strip("\r\n")
            env.append(entry)

        if any(entry.endswith("'") or entry.endswith('"') for entry in env):
            if not messagebox.askyesno(
                tr("Warning"),
                tr(
                    "If you quote the value of an environment variable, the quotes will"
                    " be part of the value.\nDid you intend this?"
                ),
                parent=self,
            ):
                return False

        get_workbench().set_option("general.environment", env)
        return True


def load_plugin() -> None:
    get_workbench().add_configuration_page("general", tr("General"), GeneralConfigurationPage, 10)
