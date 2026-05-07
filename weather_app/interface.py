"""interface.py -- The View of the Weather Dashboard.

Everything visual lives here:

* the light-blue / gray colour theme (see IDLE_THEME),
* the search bar + Search button at the top,
* the huge centred temperature label, the emoji icon, and the
  humidity / wind-speed card,
* DYNAMIC re-theming: every weather condition maps to its own emoji and
  background colour scheme (EMOJI_BY_CONDITION / THEME_BY_CONDITION).

How it connects to the engine:
    When the user presses Search (or hits Enter inside the entry box),
    we call ``get_weather(city, api_key)`` from weather_app.api_client
    and render the returned dictionary. Any network/API problem arrives
    as an exception, which we translate into a friendly on-screen message.
"""

import tkinter as tk
from tkinter import messagebox

from weather_app.api_client import (
    MissingAPIKeyError,
    WeatherAPIError,
    get_weather,
)

# --------------------------------------------------------------------------- #
#  Fonts & static colours
# --------------------------------------------------------------------------- #
FONT_FAMILY = "Segoe UI"
ICON_FONT = ("Segoe UI Emoji", 72)
TEXT_DARK = "#2C3E50"
TEXT_GRAY = "#7F8C8D"
ENTRY_BG = "#FFFFFF"
STATUS_ERROR = "#C0392B"
WATERMARK_COLOR = "#A6ACAF"

IDLE_EMOJI = "\U0001F30D"  # globe shown before the first search

IDLE_THEME = {"background": "#EAF2F8", "card": "#FFFFFF", "accent": "#2874A6"}

# --------------------------------------------------------------------------- #
#  Dynamic theming: condition group -> emoji / colours
# --------------------------------------------------------------------------- #
EMOJI_BY_CONDITION = {
    "thunderstorm": "\u26A1",
    "drizzle": "\U0001F326\uFE0F",
    "rain": "\U0001F327\uFE0F",
    "snow": "\u2744\uFE0F",
    "atmosphere": "\U0001F32B\uFE0F",
    "clear": "\u2600\uFE0F",
    "clouds": "\u2601\uFE0F",
}

THEME_BY_CONDITION = {
    "thunderstorm": {"background": "#D5DBDB", "card": "#E5E8E8", "accent": "#34495E"},
    "drizzle": {"background": "#D4E6F1", "card": "#EBF5FB", "accent": "#2E86C1"},
    "rain": {"background": "#CFE3F0", "card": "#EBF5FB", "accent": "#21618C"},
    "snow": {"background": "#EAF4FA", "card": "#FBFDFF", "accent": "#5DADE2"},
    "atmosphere": {"background": "#E5E8E8", "card": "#F4F6F6", "accent": "#707B7C"},
    "clear": {"background": "#FDF3D7", "card": "#FEF9E7", "accent": "#D68910"},
    "clouds": {"background": "#EAECEE", "card": "#F8F9F9", "accent": "#5D6D7E"},
}

# The first digit of an OWM condition id decides the family:
#   2xx thunderstorm | 3xx drizzle | 5xx rain | 6xx snow | 7xx atmosphere
#   800 clear sky | 80x clouds
_GROUP_BY_FIRST_DIGIT = {
    2: "thunderstorm",
    3: "drizzle",
    5: "rain",
    6: "snow",
    7: "atmosphere",
}


def condition_group(condition_id: int) -> str:
    """Translate an OpenWeatherMap condition id into a theme group name."""
    family = condition_id // 100
    if family == 8:
        return "clear" if condition_id == 800 else "clouds"
    return _GROUP_BY_FIRST_DIGIT.get(family, "clouds")


# --------------------------------------------------------------------------- #
#  Main window
# --------------------------------------------------------------------------- #
class WeatherDashboard(tk.Tk):
    """Main application window (the entire GUI)."""

    def __init__(self, api_key: str) -> None:
        super().__init__()
        self._api_key = api_key  # handed over from main.py

        self.title("Weather Dashboard")
        self.geometry("430x650")
        self.resizable(False, False)

        self._build_widgets()
        self._apply_theme(IDLE_THEME)

        # Pressing Enter in the search box triggers the same action
        # as clicking the Search button.
        self.city_entry.bind("<Return>", lambda _event: self._on_search())
        self.city_entry.focus_set()

    # ------------------------------------------------------------------ #
    #  Widget construction
    # ------------------------------------------------------------------ #
    def _build_widgets(self) -> None:
        # ---- App heading -------------------------------------------------
        self.title_label = tk.Label(
            self, text="Weather Dashboard", font=(FONT_FAMILY, 18, "bold")
        )
        self.title_label.pack(pady=(20, 8))

        # ---- Search row ----------------------------------------------------
        self.search_frame = tk.Frame(self)
        self.search_frame.pack()

        self.city_entry = tk.Entry(
            self.search_frame,
            font=(FONT_FAMILY, 13),
            width=22,
            justify="center",
            relief="flat",
            highlightthickness=1,
            highlightbackground="#BDC3C7",
            highlightcolor="#5DADE2",
        )
        self.city_entry.pack(side="left", ipady=8, padx=(0, 10))

        self.search_button = tk.Button(
            self.search_frame,
            text="Search",
            font=(FONT_FAMILY, 11, "bold"),
            relief="flat",
            cursor="hand2",
            padx=18,
            command=self._on_search,  # button click -> engine query below
        )
        self.search_button.pack(side="left", ipady=6)

        # ---- Big, centred weather display ----------------------------------
        self.icon_label = tk.Label(self, text=IDLE_EMOJI, font=ICON_FONT)
        self.icon_label.pack(pady=(30, 2))

        self.location_label = tk.Label(
            self, text="Type a city to begin", font=(FONT_FAMILY, 15)
        )
        self.location_label.pack()

        self.temp_label = tk.Label(self, text="--\u00B0", font=(FONT_FAMILY, 62, "bold"))
        self.temp_label.pack()

        self.description_label = tk.Label(
            self, text="", font=(FONT_FAMILY, 13, "italic")
        )
        self.description_label.pack(pady=(0, 4))

        # ---- Humidity / wind card -------------------------------------------
        self.details_card = tk.Frame(self, padx=12, pady=14)
        self.details_card.pack(fill="x", padx=48, pady=(18, 0))

        self.details_card.columnconfigure(0, weight=1)
        self.details_card.columnconfigure(1, weight=1)

        self.humidity_value = tk.Label(
            self.details_card, text="-- %", font=(FONT_FAMILY, 19, "bold")
        )
        self.humidity_value.grid(row=0, column=0)

        self.humidity_caption = tk.Label(
            self.details_card, text="Humidity", font=(FONT_FAMILY, 11)
        )
        self.humidity_caption.grid(row=1, column=0, pady=(3, 0))

        self.wind_value = tk.Label(
            self.details_card, text="-- m/s", font=(FONT_FAMILY, 19, "bold")
        )
        self.wind_value.grid(row=0, column=1)

        self.wind_caption = tk.Label(
            self.details_card, text="Wind Speed", font=(FONT_FAMILY, 11)
        )
        self.wind_caption.grid(row=1, column=1, pady=(3, 0))

        # ---- Bottom watermark -------------------------------------------------
        # Packed BEFORE the status label so it ends up at the very bottom edge.
        self.watermark_label = tk.Label(
            self,
            text="made by zencps",
            font=(FONT_FAMILY, 9),
            fg=WATERMARK_COLOR,
        )
        self.watermark_label.pack(side="bottom", pady=(0, 6))

        # ---- Status / error line ---------------------------------------------
        self.status_label = tk.Label(
            self, text="", font=(FONT_FAMILY, 10), wraplength=380
        )
        self.status_label.pack(side="bottom", fill="x", pady=(12, 0))

    # ------------------------------------------------------------------ #
    #  Dynamic re-theming
    # ------------------------------------------------------------------ #
    def _apply_theme(self, theme: dict) -> None:
        """Repaint every widget so the window matches *theme*.

        Called with IDLE_THEME at startup and then again with one of the
        THEME_BY_CONDITION entries after every successful search -- that is
        what makes the background colour change with the weather.
        """
        bg, card, accent = theme["background"], theme["card"], theme["accent"]

        self.configure(bg=bg)
        self.title_label.configure(bg=bg, fg=TEXT_DARK)

        self.search_frame.configure(bg=bg)
        self.city_entry.configure(
            bg=ENTRY_BG,
            fg=TEXT_DARK,
            insertbackground=TEXT_DARK,
            highlightbackground="#BDC3C7",
            highlightcolor=accent,
        )
        self.search_button.configure(
            bg=accent,
            fg="white",
            activebackground=accent,
            activeforeground="white",
        )

        self.icon_label.configure(bg=bg, fg=TEXT_DARK)
        self.location_label.configure(bg=bg, fg=accent)
        self.temp_label.configure(bg=bg, fg=TEXT_DARK)
        self.description_label.configure(bg=bg, fg=TEXT_GRAY)

        self.details_card.configure(bg=card)
        for widget in (self.humidity_value, self.wind_value):
            widget.configure(bg=card, fg=TEXT_DARK)
        for widget in (self.humidity_caption, self.wind_caption):
            widget.configure(bg=card, fg=TEXT_GRAY)

        self.status_label.configure(bg=bg)
        self.watermark_label.configure(bg=bg, fg=WATERMARK_COLOR)

    # ------------------------------------------------------------------ #
    #  Event handlers (search flow: View -> Engine -> View)
    # ------------------------------------------------------------------ #
    def _on_search(self) -> None:
        city = self.city_entry.get().strip()
        if not city:
            self._set_status("Please type a city name first.", error=True)
            return

        self._set_status(f'Fetching weather for "{city}" ...')
        self.update_idletasks()  # let the status paint before the blocking request

        try:
            # <-- THE CONNECTION POINT: the view asks the engine for data.
            weather = get_weather(city, self._api_key)
        except MissingAPIKeyError as exc:
            self._set_status("Missing API key.", error=True)
            messagebox.showerror("API key missing", str(exc))
            return
        except WeatherAPIError as exc:
            # Friendly message such as "City not found ..." shown on screen.
            self._set_status(str(exc), error=True)
            return

        self._render(weather)

    def _render(self, weather: dict) -> None:
        """Paint the returned engine data onto all labels + apply the theme."""
        group = condition_group(weather["condition_id"])
        self._apply_theme(THEME_BY_CONDITION[group])

        self.icon_label.configure(text=EMOJI_BY_CONDITION[group])
        self.location_label.configure(text=f"{weather['city']}, {weather['country']}")
        self.temp_label.configure(text=f"{weather['temperature']}\u00B0C")
        self.description_label.configure(text=weather["description"])
        self.humidity_value.configure(text=f"{weather['humidity']}%")
        self.wind_value.configure(text=f"{weather['wind_speed']} m/s")

        self._set_status(f"Feels like {weather['feels_like']}\u00B0C | Updated just now.")

    def _set_status(self, message: str, *, error: bool = False) -> None:
        self.status_label.configure(
            text=message, fg=STATUS_ERROR if error else TEXT_GRAY
        )
