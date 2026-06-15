"""
Predictor Profesional de Resultados de Fútbol
App Android - Kivy
"""

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.uix.popup import Popup
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.utils import get_color_from_hex
from dataclasses import dataclass, field
from typing import List, Dict

# ── Colores ──────────────────────────────────────────────────
C_VERDE       = get_color_from_hex("#1a7a1a")
C_VERDE2      = get_color_from_hex("#24a824")
C_AMARILLO    = get_color_from_hex("#f5c518")
C_GRIS_OSC    = get_color_from_hex("#1e1e1e")
C_GRIS        = get_color_from_hex("#2b2b2b")
C_GRIS_CLARO  = get_color_from_hex("#3d3d3d")
C_BLANCO      = get_color_from_hex("#f5f5f5")
C_VERDE_CLARO = get_color_from_hex("#ccffcc")
C_ROJO        = get_color_from_hex("#cc3333")

Window.clearcolor = C_GRIS_OSC

# ── Lógica de predicción ─────────────────────────────────────
@dataclass
class Equipo:
    nombre: str
    goles:    List[float] = field(default_factory=list)
    tarjetas: List[float] = field(default_factory=list)
    corners:  List[float] = field(default_factory=list)

class Predictor:
    N = 20

    @staticmethod
    def promedio(d): return sum(d)/len(d)

    @classmethod
    def varianza(cls, d):
        m = cls.promedio(d)
        return sum((x-m)**2 for x in d)/len(d)

    @classmethod
    def estadisticas(cls, e: Equipo) -> Dict[str, float]:
        return {
            "pg": cls.promedio(e.goles),
            "pt": cls.promedio(e.tarjetas),
            "pc": cls.promedio(e.corners),
            "vg": cls.varianza(e.goles),
            "vt": cls.varianza(e.tarjetas),
            "vc": cls.varianza(e.corners),
        }

    @staticmethod
    def combinados(e1, e2):
        return {
            "pg5":  ((e1["pg"]+e2["pg"])/2)*0.05,
            "pt5":  ((e1["pt"]+e2["pt"])/2)*0.05,
            "pc5":  ((e1["pc"]+e2["pc"])/2)*0.05,
            "vg05": ((e1["vg"]+e2["vg"])/2)*0.005,
            "vt05": ((e1["vt"]+e2["vt"])/2)*0.005,
            "vc05": ((e1["vc"]+e2["vc"])/2)*0.005,
        }

    @staticmethod
    def prediccion(n1, n2, e1, e2):
        return f"{n1}  {round(e1['pg'])}  -  {round(e2['pg'])}  {n2}"


# ── Widgets auxiliares ────────────────────────────────────────
def lbl(text, size=14, bold=False, color=None, halign="left", **kw):
    c = color or C_BLANCO
    l = Label(text=text, font_size=dp(size), bold=bold, color=c,
              halign=halign, **kw)
    l.bind(size=lambda inst, v: inst.setter("text_size")(inst, (v[0], None)))
    return l

def inp(hint="0", **kw):
    return TextInput(
        hint_text=hint,
        text="0",
        multiline=False,
        input_filter="float",
        background_color=C_GRIS_CLARO,
        foreground_color=C_BLANCO,
        cursor_color=C_AMARILLO,
        font_size=dp(14),
        size_hint_y=None,
        height=dp(38),
        padding=[dp(8), dp(8)],
        **kw
    )

def boton(text, bg=None, fg=None, **kw):
    bg = bg or C_VERDE
    fg = fg or C_BLANCO
    b = Button(
        text=text,
        background_color=bg,
        color=fg,
        background_normal="",
        font_size=dp(15),
        bold=True,
        **kw
    )
    return b


# ── Pantalla: Ingreso de equipo ───────────────────────────────
class PanelEquipo(BoxLayout):
    CATS = [
        ("goles",    "⚽ Goles"),
        ("tarjetas", "🟨 Tarjetas"),
        ("corners",  "🚩 Corners"),
    ]

    def __init__(self, numero, **kw):
        super().__init__(orientation="vertical", spacing=dp(4),
                         padding=dp(6), **kw)
        self.numero = numero
        self._build()

    def _build(self):
        # Header
        hdr = BoxLayout(size_hint_y=None, height=dp(42),
                        padding=[0, dp(4)])
        hdr.add_widget(Label(
            text=f"EQUIPO {self.numero}",
            font_size=dp(15), bold=True, color=C_AMARILLO
        ))
        self.add_widget(hdr)

        # Nombre
        self.add_widget(lbl("Nombre del equipo:", size=12, color=C_VERDE_CLARO,
                            size_hint_y=None, height=dp(22)))
        self.tf_nombre = TextInput(
            hint_text=f"Ej: Alianza Lima",
            multiline=False,
            background_color=C_GRIS_CLARO,
            foreground_color=C_BLANCO,
            cursor_color=C_AMARILLO,
            font_size=dp(14),
            size_hint_y=None,
            height=dp(40),
            padding=[dp(8), dp(8)],
        )
        self.add_widget(self.tf_nombre)

        # Tabs
        tp = TabbedPanel(do_default_tab=False, tab_height=dp(36))
        self.inputs: Dict[str, List[TextInput]] = {}

        for key, label in self.CATS:
            item = TabbedPanelItem(text=label, font_size=dp(12))
            sv = ScrollView()
            grid = GridLayout(cols=2, spacing=dp(4), padding=dp(6),
                              size_hint_y=None)
            grid.bind(minimum_height=grid.setter("height"))

            entries = []
            for i in range(1, Predictor.N + 1):
                grid.add_widget(lbl(f"P{i:02d}:", size=12,
                                    size_hint_y=None, height=dp(36)))
                tf = inp()
                grid.add_widget(tf)
                entries.append(tf)

            sv.add_widget(grid)
            item.add_widget(sv)
            tp.add_widget(item)
            self.inputs[key] = entries

        self.add_widget(tp)

    def obtener_equipo(self):
        nombre = self.tf_nombre.text.strip()
        if not nombre:
            raise ValueError(f"Falta el nombre del Equipo {self.numero}.")

        datos = {}
        cat_labels = {"goles": "Goles", "tarjetas": "Tarjetas", "corners": "Corners"}
        for key, entries in self.inputs.items():
            vals = []
            for i, tf in enumerate(entries, 1):
                try:
                    v = float(tf.text.strip() or "0")
                    if v < 0:
                        raise ValueError(f"Equipo {self.numero} › {cat_labels[key]} P{i}: valor negativo.")
                    vals.append(v)
                except ValueError as e:
                    if "negativo" in str(e):
                        raise
                    raise ValueError(
                        f"Equipo {self.numero} › {cat_labels[key]} P{i}: '{tf.text}' inválido."
                    )
            datos[key] = vals
        return Equipo(nombre=nombre, **datos)


# ── Pantalla principal ────────────────────────────────────────
class MainScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        root = BoxLayout(orientation="vertical", spacing=dp(4))

        # Header
        hdr = BoxLayout(size_hint_y=None, height=dp(56),
                        padding=[dp(10), dp(6)])
        hdr.canvas.before.clear()
        with hdr.canvas.before:
            from kivy.graphics import Color, Rectangle
            Color(*C_VERDE)
            self._hdr_rect = Rectangle(pos=hdr.pos, size=hdr.size)
        hdr.bind(pos=lambda i,v: setattr(self._hdr_rect, "pos", v),
                 size=lambda i,v: setattr(self._hdr_rect, "size", v))

        hdr.add_widget(Label(
            text="⚽  PREDICTOR DE FÚTBOL",
            font_size=dp(16), bold=True, color=C_BLANCO
        ))
        root.add_widget(hdr)

        # Panels
        panels = BoxLayout(orientation="horizontal", spacing=dp(4),
                           padding=[dp(4), 0])
        self.panel1 = PanelEquipo(1)
        self.panel2 = PanelEquipo(2)
        panels.add_widget(self.panel1)
        panels.add_widget(self.panel2)
        root.add_widget(panels)

        # Botón
        btn = boton("🔮  CALCULAR PREDICCIÓN",
                    bg=C_AMARILLO, fg=C_GRIS_OSC,
                    size_hint_y=None, height=dp(50))
        btn.bind(on_press=self.calcular)
        root.add_widget(btn)

        self.add_widget(root)

    def calcular(self, *_):
        try:
            e1 = self.panel1.obtener_equipo()
            e2 = self.panel2.obtener_equipo()
        except ValueError as ex:
            self._popup_error(str(ex))
            return

        est1 = Predictor.estadisticas(e1)
        est2 = Predictor.estadisticas(e2)
        comb = Predictor.combinados(est1, est2)
        pred = Predictor.prediccion(e1.nombre, e2.nombre, est1, est2)

        # Pasar a pantalla de resultados
        app = App.get_running_app()
        app.sm.get_screen("result").mostrar(e1, e2, est1, est2, comb, pred)
        app.sm.current = "result"

    def _popup_error(self, msg):
        content = BoxLayout(orientation="vertical", padding=dp(12), spacing=dp(8))
        content.add_widget(Label(text=msg, color=C_BLANCO, font_size=dp(13)))
        btn = boton("Cerrar", bg=C_ROJO, size_hint_y=None, height=dp(42))
        content.add_widget(btn)
        p = Popup(title="⚠ Error de entrada", content=content,
                  size_hint=(0.9, 0.45), background_color=C_GRIS)
        btn.bind(on_press=p.dismiss)
        p.open()


# ── Pantalla de resultados ────────────────────────────────────
class ResultScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        root = BoxLayout(orientation="vertical", spacing=dp(4))

        # Header
        hdr = BoxLayout(size_hint_y=None, height=dp(50),
                        padding=[dp(10), dp(6)])
        with hdr.canvas.before:
            from kivy.graphics import Color, Rectangle
            Color(*C_VERDE)
            self._hr = Rectangle(pos=hdr.pos, size=hdr.size)
        hdr.bind(pos=lambda i,v: setattr(self._hr,"pos",v),
                 size=lambda i,v: setattr(self._hr,"size",v))
        hdr.add_widget(Label(text="📊  RESULTADOS",
                             font_size=dp(16), bold=True, color=C_BLANCO))
        root.add_widget(hdr)

        sv = ScrollView()
        self.result_layout = BoxLayout(orientation="vertical",
                                       spacing=dp(6), padding=dp(10),
                                       size_hint_y=None)
        self.result_layout.bind(minimum_height=self.result_layout.setter("height"))
        sv.add_widget(self.result_layout)
        root.add_widget(sv)

        btn = boton("← VOLVER", bg=C_GRIS_CLARO,
                    size_hint_y=None, height=dp(46))
        btn.bind(on_press=lambda *_: setattr(App.get_running_app().sm, "current", "main"))
        root.add_widget(btn)

        self.add_widget(root)

    def _row(self, label, val, color=C_BLANCO):
        row = BoxLayout(size_hint_y=None, height=dp(30), spacing=dp(4))
        row.add_widget(lbl(label, size=12, color=C_VERDE_CLARO,
                           size_hint_x=0.65, height=dp(30), size_hint_y=None))
        row.add_widget(lbl(val, size=12, color=color, bold=True,
                           halign="right", size_hint_x=0.35,
                           height=dp(30), size_hint_y=None))
        return row

    def _sep(self, color=C_VERDE):
        from kivy.uix.widget import Widget
        from kivy.graphics import Color, Rectangle
        w = Widget(size_hint_y=None, height=dp(2))
        with w.canvas:
            Color(*color)
            Rectangle(pos=w.pos, size=w.size)
        w.bind(pos=lambda i,v: setattr(Rectangle, "pos", v))
        return w

    def mostrar(self, e1, e2, est1, est2, comb, pred):
        rl = self.result_layout
        rl.clear_widgets()

        def seccion(titulo):
            rl.add_widget(Label(text=titulo, font_size=dp(13), bold=True,
                                color=C_AMARILLO, size_hint_y=None, height=dp(32)))

        def datos_equipo(e: Equipo, est: Dict):
            seccion(f"━━  {e.nombre.upper()}  ━━")
            rl.add_widget(self._row("Promedio goles",    f"{est['pg']:.2f}"))
            rl.add_widget(self._row("Promedio tarjetas", f"{est['pt']:.2f}"))
            rl.add_widget(self._row("Promedio corners",  f"{est['pc']:.2f}"))
            rl.add_widget(self._row("Varianza goles",    f"{est['vg']:.2f}"))
            rl.add_widget(self._row("Varianza tarjetas", f"{est['vt']:.2f}"))
            rl.add_widget(self._row("Varianza corners",  f"{est['vc']:.2f}"))

        datos_equipo(e1, est1)
        datos_equipo(e2, est2)

        seccion("━━  COMBINADOS  ━━")
        rl.add_widget(self._row("Prom. goles × 5%",     f"{comb['pg5']:.4f}"))
        rl.add_widget(self._row("Prom. tarjetas × 5%",  f"{comb['pt5']:.4f}"))
        rl.add_widget(self._row("Prom. corners × 5%",   f"{comb['pc5']:.4f}"))
        rl.add_widget(self._row("Var. goles × 0.5%",    f"{comb['vg05']:.4f}"))
        rl.add_widget(self._row("Var. tarjetas × 0.5%", f"{comb['vt05']:.4f}"))
        rl.add_widget(self._row("Var. corners × 0.5%",  f"{comb['vc05']:.4f}"))

        # Predicción final
        rl.add_widget(Label(text="", size_hint_y=None, height=dp(8)))
        pred_box = BoxLayout(size_hint_y=None, height=dp(60),
                             padding=[dp(8), dp(6)])
        with pred_box.canvas.before:
            from kivy.graphics import Color, RoundedRectangle
            Color(*C_VERDE)
            self._pred_bg = RoundedRectangle(pos=pred_box.pos,
                                             size=pred_box.size, radius=[dp(8)])
        pred_box.bind(
            pos=lambda i,v: setattr(self._pred_bg,"pos",v),
            size=lambda i,v: setattr(self._pred_bg,"size",v)
        )
        pred_box.add_widget(Label(
            text=f"🏆  {pred}",
            font_size=dp(15), bold=True, color=C_AMARILLO,
            halign="center"
        ))
        rl.add_widget(pred_box)


# ── App ───────────────────────────────────────────────────────
class PredictorApp(App):
    def build(self):
        self.title = "Predictor de Fútbol"
        self.sm = ScreenManager(transition=SlideTransition())
        self.sm.add_widget(MainScreen(name="main"))
        self.sm.add_widget(ResultScreen(name="result"))
        return self.sm


if __name__ == "__main__":
    PredictorApp().run()
