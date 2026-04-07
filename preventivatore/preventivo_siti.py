#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Preventivatore siti WordPress + Elementor — stima per commerciale (Nordest Italia).
Prezzi da prezzi_nordest.json (modificabile senza toccare il codice).
"""

from __future__ import annotations

import html
import json
import os
import sys
import threading
import time
import urllib.parse
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import tkinter as tk
from tkinter import (
    Tk,
    Toplevel,
    StringVar,
    IntVar,
    BooleanVar,
    DoubleVar,
    ttk,
    messagebox,
    END,
    scrolledtext,
)

CONFIG_PATH = Path(__file__).resolve().parent / "prezzi_nordest.json"

# Su macOS: tema ttk predefinito e font Windows possono lasciare la finestra vuota o illeggibile.
if sys.platform == "darwin":
    _FONT_TITLE = ("Helvetica Neue", 17, "bold")
    _FONT_NOTE = ("Helvetica Neue", 15)
    _FONT_MICRO = ("Helvetica Neue", 14)
    _FONT_INPUT = ("Helvetica Neue", 15)
    _FONT_MONO = ("Menlo", 15)
    _FONT_DIALOG = ("Helvetica Neue", 15)
    _FONT_BUTTON = ("Helvetica Neue", 15)
    _MAC_BG = "#ececec"
    _MAC_FG = "#1a1a1a"
    _MAC_MUTED = "#555555"
    _MAC_WRAP = 820
else:
    _FONT_NOTE = ("Segoe UI", 9)
    _FONT_MICRO = ("Segoe UI", 8)
    _FONT_MONO = ("Consolas", 10)
    _FONT_DIALOG = ("Segoe UI", 10)


def load_config() -> dict:
    with open(CONFIG_PATH, encoding="utf-8") as f:
        return json.load(f)


def fmt_eur(n: float) -> str:
    return f"€ {n:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


class _FV:
    """Valore finto con .get() per riusare _compute_quote senza Tk."""

    __slots__ = ("_v",)

    def __init__(self, v: object) -> None:
        self._v = v

    def get(self) -> object:
        return self._v


def _mac_check(parent: tk.Misc, **kw) -> tk.Checkbutton:
    kw.setdefault("bg", _MAC_BG)
    kw.setdefault("fg", _MAC_FG)
    kw.setdefault("activebackground", _MAC_BG)
    kw.setdefault("activeforeground", _MAC_FG)
    kw.setdefault("selectcolor", "#ffffff")
    kw.setdefault("highlightthickness", 0)
    kw.setdefault("font", _FONT_NOTE)
    return tk.Checkbutton(parent, **kw)


def _mac_apply_global_options(root: Tk) -> None:
    """Font per menu a tendina (OptionMenu) e controlli nativi che non ereditano dal parent."""
    root.option_add("*Menu.font", _FONT_INPUT)
    root.option_add("*Menubutton.font", _FONT_INPUT)


def _mac_option_menu(parent: tk.Misc, variable: StringVar, values: list[str], width_chars: int = 36) -> tk.OptionMenu:
    vals = list(values)
    if not vals:
        raise ValueError("option menu: serve almeno un valore")
    w = tk.OptionMenu(parent, variable, *vals)
    w.configure(font=_FONT_INPUT, anchor="w", highlightthickness=0)
    try:
        w.configure(width=width_chars)
    except tk.TclError:
        pass
    return w


def _mac_spinbox(parent: tk.Misc, **kw) -> tk.Spinbox:
    kw.setdefault("font", _FONT_INPUT)
    kw.setdefault("bg", "#ffffff")
    kw.setdefault("fg", _MAC_FG)
    kw.setdefault("insertbackground", _MAC_FG)
    kw.setdefault("highlightthickness", 1)
    kw.setdefault("highlightbackground", "#b0b0b0")
    kw.setdefault("highlightcolor", "#4a90d9")
    return tk.Spinbox(parent, **kw)


def _mac_button(parent: tk.Misc, **kw) -> tk.Button:
    kw.setdefault("font", _FONT_BUTTON)
    kw.setdefault("padx", 14)
    kw.setdefault("pady", 8)
    return tk.Button(parent, **kw)


def _mac_bring_to_front(w: tk.Misc) -> None:
    try:
        top = w.winfo_toplevel()
        top.lift()
        top.attributes("-topmost", True)
        top.update_idletasks()
        top.after(80, lambda: top.attributes("-topmost", False))
    except tk.TclError:
        pass


class PreventivoApp:
    def __init__(self, root: Tk) -> None:
        self.root = root
        self.root.title("Preventivo siti WP + Elementor (Nordest)")
        self.root.minsize(720, 560)
        try:
            self.cfg = load_config()
        except Exception as e:
            messagebox.showerror("Errore", f"Impossibile leggere {CONFIG_PATH}:\n{e}")
            sys.exit(1)

        self._build_vars()
        self._build_ui()

    def _build_vars(self) -> None:
        keys = list(self.cfg["bases"].keys())
        default_tipo = "vetrina" if "vetrina" in keys else (keys[0] if keys else "vetrina")
        self.var_tipo = StringVar(value=default_tipo)
        self.var_pagine = IntVar(value=5)
        self.var_complessita = StringVar(value="standard")
        self.var_ore_extra = DoubleVar(value=0.0)
        self.var_lingue_extra = IntVar(value=0)
        self.var_prodotti_extra = IntVar(value=0)

        self.opt_woo_addon = BooleanVar(value=False)
        self.opt_seo = BooleanVar(value=False)
        self.opt_copy_pages = IntVar(value=0)
        self.opt_forms = BooleanVar(value=False)
        self.opt_crm = BooleanVar(value=False)
        self.opt_elementor_pro = BooleanVar(value=False)
        self.opt_speed = BooleanVar(value=False)
        self.opt_legal = BooleanVar(value=False)
        self.opt_hosting = BooleanVar(value=True)
        self.opt_hosting_dr = BooleanVar(value=False)
        self.opt_hosting_av = BooleanVar(value=False)
        self.opt_hosting_bitninja = BooleanVar(value=False)
        self.opt_domain = BooleanVar(value=True)
        self.opt_manutenzione = BooleanVar(value=True)
        self.opt_wpml_license = BooleanVar(value=True)

        self._mac_tk = sys.platform == "darwin"
        self._hosting_addon_widgets: list[tk.Misc] = []
        self._spinboxes: list[tk.Misc] = []
        self._ui_ready = False

        comm = self.cfg.get("commercial", {})
        self.var_margine_pct = DoubleVar(value=float(comm.get("margin_percent_default", 25)))
        self.var_sconto_pct = DoubleVar(value=float(comm.get("discount_percent_default", 0)))

    def _build_ui(self) -> None:
        if self._mac_tk:
            self._build_ui_mac_tk()
            return

        pad = {"padx": 8, "pady": 4}
        main = ttk.Frame(self.root, padding=10)
        main.pack(fill="both", expand=True)

        ttk.Label(
            main,
            text="Stima indicativa per prima valutazione commerciale (WordPress + Elementor, Nordest).",
            wraplength=680,
        ).pack(anchor="w")

        ttk.Label(
            main,
            text="I valori non sono vincolanti: adatta prezzi_nordest.json al tuo listino.",
            font=_FONT_NOTE,
            foreground="#555",
        ).pack(anchor="w", pady=(0, 8))

        row1 = ttk.Frame(main)
        row1.pack(fill="x", **pad)
        ttk.Label(row1, text="Tipo progetto").pack(side="left")
        tipo_combo = ttk.Combobox(
            row1,
            textvariable=self.var_tipo,
            state="readonly",
            width=48,
            values=list(self.cfg["bases"].keys()),
        )
        tipo_combo.pack(side="left", padx=(8, 0))
        tipo_combo.bind("<<ComboboxSelected>>", self._on_tipo_selected)

        row2 = ttk.Frame(main)
        row2.pack(fill="x", **pad)
        ttk.Label(row2, text="Pagine totali (stimate)").pack(side="left")
        sp_pages = ttk.Spinbox(row2, from_=1, to=200, textvariable=self.var_pagine, width=8)
        sp_pages.pack(side="left", padx=(8, 24))
        self._spinboxes.append(sp_pages)
        ttk.Label(row2, text="Complessità").pack(side="left")
        ttk.Combobox(
            row2,
            textvariable=self.var_complessita,
            state="readonly",
            width=12,
            values=list(self.cfg["complexity_multiplier"].keys()),
        ).pack(side="left", padx=(8, 8))
        ttk.Label(
            row2,
            text="(definisce anche la % provvigione indicativa)",
            font=_FONT_MICRO,
            foreground="#555",
        ).pack(side="left")

        opts = ttk.LabelFrame(main, text="Opzioni", padding=8)
        opts.pack(fill="x", **pad)

        g1 = ttk.Frame(opts)
        g1.pack(fill="x")
        ttk.Checkbutton(
            g1,
            text="Aggiungi e-commerce su base non e-commerce",
            variable=self.opt_woo_addon,
        ).pack(anchor="w")
        ttk.Checkbutton(g1, text="SEO on-page (pacchetto)", variable=self.opt_seo).pack(anchor="w")
        ttk.Checkbutton(g1, text="Form avanzati / logica", variable=self.opt_forms).pack(anchor="w")
        ttk.Checkbutton(g1, text="Integrazione CRM / newsletter", variable=self.opt_crm).pack(anchor="w")

        g2 = ttk.Frame(opts)
        g2.pack(fill="x", pady=(6, 0))
        ttk.Checkbutton(
            g2,
            text="Licenza Elementor Pro (1 anno, voce a cliente)",
            variable=self.opt_elementor_pro,
        ).pack(anchor="w")
        ttk.Checkbutton(g2, text="Ottimizzazione velocità", variable=self.opt_speed).pack(anchor="w")
        ttk.Checkbutton(g2, text="Privacy / cookie (setup testi standard)", variable=self.opt_legal).pack(anchor="w")

        g3 = ttk.Frame(opts)
        g3.pack(fill="x", pady=(6, 0))
        ttk.Label(g3, text="Lingue oltre l'italiano (WPML)").pack(side="left")
        sp_lang = ttk.Spinbox(g3, from_=0, to=10, textvariable=self.var_lingue_extra, width=5)
        sp_lang.pack(side="left", padx=(6, 8))
        self._spinboxes.append(sp_lang)
        ttk.Checkbutton(
            g3,
            text="Voce licenza WPML 1 anno",
            variable=self.opt_wpml_license,
        ).pack(side="left", padx=(0, 16))
        ttk.Label(g3, text="Pagine con copywriting").pack(side="left")
        sp_copy = ttk.Spinbox(g3, from_=0, to=80, textvariable=self.opt_copy_pages, width=5)
        sp_copy.pack(side="left", padx=(6, 16))
        self._spinboxes.append(sp_copy)
        ttk.Label(g3, text="Prodotti extra (solo tipo e-commerce)").pack(side="left")
        sp_prod = ttk.Spinbox(g3, from_=0, to=5000, textvariable=self.var_prodotti_extra, width=8)
        sp_prod.pack(side="left", padx=(6, 0))
        self._spinboxes.append(sp_prod)

        ann = ttk.LabelFrame(main, text="Ricorrenti / consulenza", padding=8)
        ann.pack(fill="x", **pad)
        hp = float(self.cfg.get("hosting_annual_managed", {}).get("price", 220))
        ttk.Checkbutton(
            ann,
            text=f"Hosting WordPress gestito (12 mesi, da {fmt_eur(hp)}/anno + IVA)",
            variable=self.opt_hosting,
            command=self._on_hosting_toggle,
        ).pack(anchor="w")

        host_add = ttk.Frame(ann)
        host_add.pack(fill="x", padx=(18, 0), pady=(2, 4))
        ttk.Label(
            host_add,
            text="Opzioni hosting (solo con hosting incluso, tutte 12 mesi):",
            font=_FONT_MICRO,
            foreground="#555",
        ).pack(anchor="w")
        addons_cfg = self.cfg.get("hosting_addons_annual") or {}
        dr = addons_cfg.get("disaster_recovery") or {}
        av = addons_cfg.get("antivirus_malware") or {}
        bn = addons_cfg.get("bitninja") or {}
        self._hosting_addon_widgets.append(
            ttk.Checkbutton(
                host_add,
                text=f"{dr.get('label', 'Disaster recovery (12 mesi)')} (+{fmt_eur(float(dr.get('price', 0)))} /anno)",
                variable=self.opt_hosting_dr,
            )
        )
        self._hosting_addon_widgets.append(
            ttk.Checkbutton(
                host_add,
                text=f"{av.get('label', 'Antivirus (12 mesi)')} (+{fmt_eur(float(av.get('price', 0)))} /anno)",
                variable=self.opt_hosting_av,
            )
        )
        self._hosting_addon_widgets.append(
            ttk.Checkbutton(
                host_add,
                text=f"{bn.get('label', 'BitNinja (12 mesi)')} (+{fmt_eur(float(bn.get('price', 0)))} /anno)",
                variable=self.opt_hosting_bitninja,
            )
        )
        for w in self._hosting_addon_widgets:
            w.pack(anchor="w")

        ttk.Checkbutton(ann, text="Includi dominio (1° anno)", variable=self.opt_domain).pack(anchor="w")
        ttk.Checkbutton(
            ann,
            text="Stima manutenzione annuale (minimo o % sul netto progetto)",
            variable=self.opt_manutenzione,
        ).pack(anchor="w")
        row_h = ttk.Frame(ann)
        row_h.pack(fill="x", pady=(4, 0))
        ttk.Label(row_h, text="Ore consulenza / custom extra").pack(side="left")
        sp_ore = ttk.Spinbox(
            row_h,
            from_=0,
            to=500,
            increment=0.5,
            textvariable=self.var_ore_extra,
            width=8,
        )
        sp_ore.pack(side="left", padx=(8, 0))
        self._spinboxes.append(sp_ore)

        comm = self.cfg.get("commercial", {})
        marg_max = float(comm.get("margin_percent_max", 80))
        scont_max = float(comm.get("discount_percent_max", 50))
        comm_fr = ttk.LabelFrame(main, text="Listino commerciale (solo sviluppo one-off)", padding=8)
        comm_fr.pack(fill="x", **pad)
        row_c = ttk.Frame(comm_fr)
        row_c.pack(fill="x")
        ttk.Label(row_c, text="Margine / ricarico %").pack(side="left")
        sp_marg = ttk.Spinbox(
            row_c,
            from_=0,
            to=marg_max,
            increment=0.5,
            textvariable=self.var_margine_pct,
            width=7,
        )
        sp_marg.pack(side="left", padx=(6, 20))
        self._spinboxes.append(sp_marg)
        ttk.Label(row_c, text="Sconto commerciale %").pack(side="left")
        sp_scont = ttk.Spinbox(
            row_c,
            from_=0,
            to=scont_max,
            increment=0.5,
            textvariable=self.var_sconto_pct,
            width=7,
        )
        sp_scont.pack(side="left", padx=(6, 0))
        self._spinboxes.append(sp_scont)
        ttk.Label(
            comm_fr,
            text="Formula: imponibile tecnico × (1+margine) × (1−sconto). Hosting, dominio e manutenzione non sono scontati qui.",
            font=_FONT_MICRO,
            foreground="#555",
            wraplength=680,
        ).pack(anchor="w", pady=(6, 0))

        ttk.Label(
            comm_fr,
            text="Provvigione indicativa: legata al livello Complessità (standard / medio / alto). Non modifica l'offerta al cliente; base calcolo: imponibile progetto al cliente.",
            font=_FONT_MICRO,
            foreground="#555",
            wraplength=680,
        ).pack(anchor="w", pady=(8, 0))

        btn_row = ttk.Frame(main)
        btn_row.pack(fill="x", pady=10)
        ttk.Button(btn_row, text="Calcola preventivo", command=self.calcola).pack(side="left")
        ttk.Button(btn_row, text="Testo offerta (interno)", command=self.apri_generatore_offerta).pack(
            side="left", padx=(8, 0)
        )
        ttk.Button(btn_row, text="Copia riepilogo", command=self.copia).pack(side="left", padx=(8, 0))
        ttk.Button(btn_row, text="Esporta TXT…", command=self.esporta).pack(side="left", padx=(8, 0))
        ttk.Label(
            btn_row,
            text="  ·  Ricalcolo automatico al cambio opzioni",
            font=_FONT_MICRO,
            foreground="#555",
        ).pack(side="left", padx=(4, 0))

        st_out: dict = {"height": 16, "wrap": "word", "font": _FONT_MONO}
        if sys.platform == "darwin":
            st_out["bg"] = "#ffffff"
            st_out["fg"] = "#1a1a1a"
            st_out["insertbackground"] = "#1a1a1a"
        self.out = scrolledtext.ScrolledText(main, **st_out)
        self.out.pack(fill="both", expand=True, pady=(4, 0))

        self._on_tipo_change()
        self._sync_hosting_addons_state()
        self._ui_ready = True
        self._wire_auto_recalc()
        self.calcola()
        self.root.update_idletasks()
        self.root.update()

    def _build_ui_mac_tk(self) -> None:
        """Su alcune build macOS i widget ttk non vengono disegnati; usiamo solo tk classico."""
        _mac_apply_global_options(self.root)
        self.root.configure(bg=_MAC_BG)
        self.root.geometry("1000x920")
        self.root.minsize(860, 700)

        main = tk.Frame(self.root, bg=_MAC_BG)
        main.pack(fill="both", expand=True)

        hdr = tk.Frame(main, bg=_MAC_BG)
        hdr.pack(fill="x", padx=14, pady=(12, 6))
        tk.Label(
            hdr,
            text="Preventivo siti WP + Elementor (Nordest)",
            bg=_MAC_BG,
            fg=_MAC_FG,
            font=_FONT_TITLE,
            justify="left",
        ).pack(anchor="w")
        tk.Label(
            hdr,
            text="Stima indicativa per prima valutazione commerciale (WordPress + Elementor, Nordest).",
            bg=_MAC_BG,
            fg=_MAC_FG,
            font=_FONT_NOTE,
            wraplength=_MAC_WRAP,
            justify="left",
        ).pack(anchor="w", pady=(2, 0))
        tk.Label(
            hdr,
            text="I valori non sono vincolanti: adatta prezzi_nordest.json al tuo listino.",
            bg=_MAC_BG,
            fg=_MAC_MUTED,
            font=_FONT_MICRO,
            wraplength=_MAC_WRAP,
            justify="left",
        ).pack(anchor="w", pady=(0, 2))

        # Pannello inferiore fisso: riepilogo e azioni sempre visibili (scroll solo sul modulo sopra).
        bottom_dock = tk.Frame(main, bg="#dedede", relief=tk.GROOVE, borderwidth=1, padx=12, pady=10)
        bottom_dock.pack(side=tk.BOTTOM, fill=tk.X)

        tk.Label(
            bottom_dock,
            text="Riepilogo preventivo",
            bg="#dedede",
            fg=_MAC_FG,
            font=_FONT_TITLE,
        ).pack(anchor="w")

        out_wrap = tk.Frame(bottom_dock, bg="#dedede")
        out_wrap.pack(fill=tk.X, pady=(6, 10))
        self.out = scrolledtext.ScrolledText(
            out_wrap,
            height=13,
            width=92,
            wrap="word",
            font=_FONT_MONO,
            bg="#fafafa",
            fg="#111111",
            insertbackground="#111111",
            borderwidth=2,
            relief=tk.SUNKEN,
            highlightthickness=1,
            highlightbackground="#888888",
            padx=10,
            pady=10,
        )
        self.out.pack(fill=tk.X)

        btn_row = tk.Frame(bottom_dock, bg="#dedede")
        btn_row.pack(fill=tk.X)
        _mac_button(btn_row, text="Calcola preventivo", command=self.calcola).pack(side=tk.LEFT)
        _mac_button(btn_row, text="Testo offerta (interno)", command=self.apri_generatore_offerta).pack(
            side=tk.LEFT, padx=(12, 0)
        )
        _mac_button(btn_row, text="Copia riepilogo", command=self.copia).pack(side=tk.LEFT, padx=(12, 0))
        _mac_button(btn_row, text="Esporta TXT…", command=self.esporta).pack(side=tk.LEFT, padx=(12, 0))
        tk.Label(
            btn_row,
            text="  ·  Ricalcolo automatico al cambio opzioni",
            bg="#dedede",
            fg=_MAC_MUTED,
            font=_FONT_MICRO,
        ).pack(side=tk.LEFT, padx=(10, 0))

        scroll_outer = tk.Frame(main, bg=_MAC_BG)
        scroll_outer.pack(fill=tk.BOTH, expand=True, padx=14, pady=(4, 8))

        canvas = tk.Canvas(scroll_outer, bg=_MAC_BG, highlightthickness=0)
        vsb = tk.Scrollbar(scroll_outer, orient=tk.VERTICAL, command=canvas.yview)
        canvas.configure(yscrollcommand=vsb.set)

        gf = tk.Frame(canvas, bg=_MAC_BG)
        inner_id = canvas.create_window((0, 0), window=gf, anchor="nw")

        def _canvas_inner_width(event: tk.Event) -> None:
            canvas.itemconfigure(inner_id, width=max(int(event.width) - 8, 280))

        def _canvas_scrollregion(_event: tk.Event | None = None) -> None:
            canvas.configure(scrollregion=canvas.bbox("all"))

        gf.bind("<Configure>", lambda e: _canvas_scrollregion(e))
        canvas.bind("<Configure>", _canvas_inner_width)

        def _wheel(evt: tk.Event) -> str:
            if getattr(evt, "delta", 0):
                canvas.yview_scroll(int(-evt.delta / 120), "units")
            return "break"

        canvas.bind("<MouseWheel>", _wheel)
        canvas.bind("<Enter>", lambda e: canvas.focus_set())

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

        gr = 0
        tk.Label(gf, text="Tipo progetto", bg=_MAC_BG, fg=_MAC_FG, font=_FONT_NOTE).grid(
            row=gr, column=0, sticky="ne", padx=(0, 12), pady=4
        )
        om_tipo = _mac_option_menu(gf, self.var_tipo, list(self.cfg["bases"].keys()), width_chars=34)
        om_tipo.grid(row=gr, column=1, sticky="nw", pady=4)
        gr += 1

        tk.Label(gf, text="Pagine totali (stimate)", bg=_MAC_BG, fg=_MAC_FG, font=_FONT_NOTE).grid(
            row=gr, column=0, sticky="ne", padx=(0, 12), pady=4
        )
        sp_pages = _mac_spinbox(gf, from_=1, to=200, textvariable=self.var_pagine, width=10)
        sp_pages.grid(row=gr, column=1, sticky="w", pady=4)
        self._spinboxes.append(sp_pages)
        gr += 1

        tk.Label(gf, text="Complessità", bg=_MAC_BG, fg=_MAC_FG, font=_FONT_NOTE).grid(
            row=gr, column=0, sticky="ne", padx=(0, 12), pady=4
        )
        om_comp = _mac_option_menu(
            gf, self.var_complessita, list(self.cfg["complexity_multiplier"].keys()), width_chars=18
        )
        om_comp.grid(row=gr, column=1, sticky="nw", pady=4)
        gr += 1

        tk.Label(
            gf,
            text="(definisce anche la % provvigione indicativa)",
            bg=_MAC_BG,
            fg=_MAC_MUTED,
            font=_FONT_MICRO,
        ).grid(row=gr, column=0, columnspan=2, sticky="w", pady=(0, 6))
        gr += 1

        opts = tk.LabelFrame(gf, text=" Opzioni ", bg=_MAC_BG, fg=_MAC_FG, font=_FONT_NOTE, padx=12, pady=10)
        opts.grid(row=gr, column=0, columnspan=2, sticky="ew", pady=(4, 0))
        gr += 1

        g1 = tk.Frame(opts, bg=_MAC_BG)
        g1.pack(fill="x")
        _mac_check(g1, text="Aggiungi e-commerce su base non e-commerce", variable=self.opt_woo_addon).pack(anchor="w")
        _mac_check(g1, text="SEO on-page (pacchetto)", variable=self.opt_seo).pack(anchor="w")
        _mac_check(g1, text="Form avanzati / logica", variable=self.opt_forms).pack(anchor="w")
        _mac_check(g1, text="Integrazione CRM / newsletter", variable=self.opt_crm).pack(anchor="w")

        g2 = tk.Frame(opts, bg=_MAC_BG)
        g2.pack(fill="x", pady=(8, 0))
        _mac_check(
            g2,
            text="Licenza Elementor Pro (1 anno, voce a cliente)",
            variable=self.opt_elementor_pro,
        ).pack(anchor="w")
        _mac_check(g2, text="Ottimizzazione velocità", variable=self.opt_speed).pack(anchor="w")
        _mac_check(g2, text="Privacy / cookie (setup testi standard)", variable=self.opt_legal).pack(anchor="w")

        g3 = tk.Frame(opts, bg=_MAC_BG)
        g3.pack(fill="x", pady=(10, 0))
        g3.columnconfigure(1, weight=0)

        tk.Label(
            g3,
            text="Lingue oltre l'italiano (WPML)",
            bg=_MAC_BG,
            fg=_MAC_FG,
            font=_FONT_NOTE,
        ).grid(row=0, column=0, sticky="e", padx=(0, 8), pady=4)
        sp_lang = _mac_spinbox(g3, from_=0, to=10, textvariable=self.var_lingue_extra, width=6)
        sp_lang.grid(row=0, column=1, sticky="w", pady=4)
        self._spinboxes.append(sp_lang)

        _mac_check(g3, text="Voce licenza WPML 1 anno", variable=self.opt_wpml_license).grid(
            row=1, column=0, columnspan=4, sticky="w", pady=(2, 4)
        )

        tk.Label(
            g3,
            text="Pagine con copywriting",
            bg=_MAC_BG,
            fg=_MAC_FG,
            font=_FONT_NOTE,
        ).grid(row=2, column=0, sticky="e", padx=(0, 8), pady=4)
        sp_copy = _mac_spinbox(g3, from_=0, to=80, textvariable=self.opt_copy_pages, width=6)
        sp_copy.grid(row=2, column=1, sticky="w", pady=4)
        self._spinboxes.append(sp_copy)

        tk.Label(
            g3,
            text="Prodotti extra (solo e-commerce)",
            bg=_MAC_BG,
            fg=_MAC_FG,
            font=_FONT_NOTE,
        ).grid(row=2, column=2, sticky="e", padx=(16, 8), pady=4)
        sp_prod = _mac_spinbox(g3, from_=0, to=5000, textvariable=self.var_prodotti_extra, width=10)
        sp_prod.grid(row=2, column=3, sticky="w", pady=4)
        self._spinboxes.append(sp_prod)

        ann = tk.LabelFrame(
            gf, text=" Ricorrenti / consulenza ", bg=_MAC_BG, fg=_MAC_FG, font=_FONT_NOTE, padx=12, pady=10
        )
        ann.grid(row=gr, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        gr += 1

        hp = float(self.cfg.get("hosting_annual_managed", {}).get("price", 220))
        _mac_check(
            ann,
            text=f"Hosting WordPress gestito (12 mesi, da {fmt_eur(hp)}/anno + IVA)",
            variable=self.opt_hosting,
            command=self._on_hosting_toggle,
        ).pack(anchor="w")

        host_add = tk.Frame(ann, bg=_MAC_BG)
        host_add.pack(fill="x", padx=(18, 0), pady=(2, 4))
        tk.Label(
            host_add,
            text="Opzioni hosting (solo con hosting incluso, tutte 12 mesi):",
            bg=_MAC_BG,
            fg=_MAC_MUTED,
            font=_FONT_MICRO,
        ).pack(anchor="w")
        addons_cfg = self.cfg.get("hosting_addons_annual") or {}
        dr = addons_cfg.get("disaster_recovery") or {}
        av = addons_cfg.get("antivirus_malware") or {}
        bn = addons_cfg.get("bitninja") or {}
        self._hosting_addon_widgets.append(
            _mac_check(
                host_add,
                text=f"{dr.get('label', 'Disaster recovery (12 mesi)')} (+{fmt_eur(float(dr.get('price', 0)))} /anno)",
                variable=self.opt_hosting_dr,
            )
        )
        self._hosting_addon_widgets.append(
            _mac_check(
                host_add,
                text=f"{av.get('label', 'Antivirus (12 mesi)')} (+{fmt_eur(float(av.get('price', 0)))} /anno)",
                variable=self.opt_hosting_av,
            )
        )
        self._hosting_addon_widgets.append(
            _mac_check(
                host_add,
                text=f"{bn.get('label', 'BitNinja (12 mesi)')} (+{fmt_eur(float(bn.get('price', 0)))} /anno)",
                variable=self.opt_hosting_bitninja,
            )
        )
        for w in self._hosting_addon_widgets:
            w.pack(anchor="w")

        _mac_check(ann, text="Includi dominio (1° anno)", variable=self.opt_domain).pack(anchor="w")
        _mac_check(
            ann,
            text="Stima manutenzione annuale (minimo o % sul netto progetto)",
            variable=self.opt_manutenzione,
        ).pack(anchor="w")
        row_h = tk.Frame(ann, bg=_MAC_BG)
        row_h.pack(fill="x", pady=(6, 0))
        tk.Label(row_h, text="Ore consulenza / custom extra", bg=_MAC_BG, fg=_MAC_FG, font=_FONT_NOTE).pack(
            side="left"
        )
        sp_ore = _mac_spinbox(row_h, from_=0, to=500, increment=0.5, textvariable=self.var_ore_extra, width=10)
        sp_ore.pack(side="left", padx=(10, 0))
        self._spinboxes.append(sp_ore)

        comm = self.cfg.get("commercial", {})
        marg_max = float(comm.get("margin_percent_max", 80))
        scont_max = float(comm.get("discount_percent_max", 50))
        comm_fr = tk.LabelFrame(
            gf,
            text=" Listino commerciale (solo sviluppo one-off) ",
            bg=_MAC_BG,
            fg=_MAC_FG,
            font=_FONT_NOTE,
            padx=12,
            pady=10,
        )
        comm_fr.grid(row=gr, column=0, columnspan=2, sticky="ew", pady=(10, 0))

        row_c = tk.Frame(comm_fr, bg=_MAC_BG)
        row_c.pack(fill="x")
        tk.Label(row_c, text="Margine / ricarico %", bg=_MAC_BG, fg=_MAC_FG, font=_FONT_NOTE).pack(side="left")
        sp_marg = _mac_spinbox(
            row_c, from_=0, to=marg_max, increment=0.5, textvariable=self.var_margine_pct, width=8
        )
        sp_marg.pack(side="left", padx=(10, 24))
        self._spinboxes.append(sp_marg)
        tk.Label(row_c, text="Sconto commerciale %", bg=_MAC_BG, fg=_MAC_FG, font=_FONT_NOTE).pack(side="left")
        sp_scont = _mac_spinbox(
            row_c, from_=0, to=scont_max, increment=0.5, textvariable=self.var_sconto_pct, width=8
        )
        sp_scont.pack(side="left", padx=(10, 0))
        self._spinboxes.append(sp_scont)
        tk.Label(
            comm_fr,
            text="Formula: imponibile tecnico × (1+margine) × (1−sconto). Hosting, dominio e manutenzione non sono scontati qui.",
            bg=_MAC_BG,
            fg=_MAC_MUTED,
            font=_FONT_MICRO,
            wraplength=_MAC_WRAP,
            justify="left",
        ).pack(anchor="w", pady=(8, 0))

        tk.Label(
            comm_fr,
            text="Provvigione indicativa: legata al livello Complessità (standard / medio / alto). Non modifica l'offerta al cliente; base calcolo: imponibile progetto al cliente.",
            bg=_MAC_BG,
            fg=_MAC_MUTED,
            font=_FONT_MICRO,
            wraplength=_MAC_WRAP,
            justify="left",
        ).pack(anchor="w", pady=(8, 0))

        self._on_tipo_change()
        self._sync_hosting_addons_state()
        self._ui_ready = True
        self._wire_auto_recalc()
        self.calcola()
        self.root.update_idletasks()
        self.root.update()

    def _trigger_recalc(self, *_args) -> None:
        if not self._ui_ready:
            return
        self.root.after_idle(self.calcola)

    def _wire_auto_recalc(self) -> None:
        if self._mac_tk:
            self.var_tipo.trace_add("write", self._on_tipo_selected)
        for v in (
            self.var_pagine,
            self.var_complessita,
            self.var_ore_extra,
            self.var_lingue_extra,
            self.var_prodotti_extra,
            self.opt_copy_pages,
            self.opt_woo_addon,
            self.opt_seo,
            self.opt_forms,
            self.opt_crm,
            self.opt_elementor_pro,
            self.opt_speed,
            self.opt_legal,
            self.opt_hosting_dr,
            self.opt_hosting_av,
            self.opt_hosting_bitninja,
            self.opt_domain,
            self.opt_manutenzione,
            self.opt_wpml_license,
            self.var_margine_pct,
            self.var_sconto_pct,
        ):
            v.trace_add("write", self._trigger_recalc)
        for sb in self._spinboxes:
            sb.bind("<FocusOut>", self._trigger_recalc)
            sb.bind("<Return>", self._trigger_recalc)

    def _on_tipo_selected(self, *_args) -> None:
        self._on_tipo_change()
        self._trigger_recalc()

    def _on_hosting_toggle(self) -> None:
        self._sync_hosting_addons_state()
        self._trigger_recalc()

    def _sync_hosting_addons_state(self) -> None:
        for w in self._hosting_addon_widgets:
            if self.opt_hosting.get():
                if self._mac_tk:
                    w.config(state=tk.NORMAL)
                else:
                    w.state(["!disabled"])
            else:
                if self._mac_tk:
                    w.config(state=tk.DISABLED)
                else:
                    w.state(["disabled"])

    def _on_tipo_change(self, *_args) -> None:
        k = self.var_tipo.get()
        base = self.cfg["bases"].get(k, {})
        inc = int(base.get("included_pages", 5))
        self.var_pagine.set(inc)

    def _compute_quote(self) -> dict:
        cfg = self.cfg
        iva = float(cfg.get("iva_percent", 22))
        comm = cfg.get("commercial", {})
        tipo = self.var_tipo.get()
        base_info = cfg["bases"][tipo]
        included = int(base_info["included_pages"])
        pagine = max(1, int(self.var_pagine.get()))
        base_price = float(base_info["price"])
        extra_pages = max(0, pagine - included)
        extra_cost = extra_pages * float(cfg["extra_page_price"])
        complessita_key = self.var_complessita.get()
        mult = float(cfg["complexity_multiplier"].get(complessita_key, 1.0))
        subtotal_core = (base_price + extra_cost) * mult

        opts = cfg["options"]
        dev_extra = 0.0
        option_lines: list[str] = []
        scope_cliente: list[str] = []

        scope_cliente.append(
            f"Realizzazione sito web: {base_info['label']}, su piattaforma WordPress con Elementor (layout responsive)."
        )
        scope_cliente.append(f"Estensione indicativa: circa {pagine} pagine.")
        scope_cliente.append(
            f"Livello di complessità progetto: «{complessita_key}» (coerente con tempi e articolazione delle attività)."
        )

        if tipo != "ecommerce" and self.opt_woo_addon.get():
            p = float(opts["woocommerce_addon"]["price"])
            dev_extra += p
            option_lines.append(f"  {opts['woocommerce_addon']['label']}: {fmt_eur(p)}")
            scope_cliente.append(opts["woocommerce_addon"]["label"] + ".")

        n_lang = max(0, int(self.var_lingue_extra.get()))
        if n_lang:
            setup = float(opts["wpml_setup_base"]["price"])
            dev_extra += setup
            option_lines.append(f"  {opts['wpml_setup_base']['label']}: {fmt_eur(setup)}")
            per_lang = float(opts["wpml_per_extra_language"]["price"])
            p_lang = n_lang * per_lang
            dev_extra += p_lang
            option_lines.append(
                f"  {opts['wpml_per_extra_language']['label']} × {n_lang}: {fmt_eur(p_lang)}"
            )
            lic_note = ""
            if self.opt_wpml_license.get():
                lic = float(opts["wpml_license_annual"]["price"])
                dev_extra += lic
                option_lines.append(f"  {opts['wpml_license_annual']['label']}: {fmt_eur(lic)}")
                lic_note = " Voce licenza WPML primo anno inclusa in preventivo."
            scope_cliente.append(
                f"Sito multilingue con WPML: {n_lang} lingua/e oltre l'italiano, configurazione e impaginazione.{lic_note}"
            )

        if self.opt_seo.get():
            p = float(opts["seo_onpage"]["price"])
            dev_extra += p
            option_lines.append(f"  {opts['seo_onpage']['label']}: {fmt_eur(p)}")
            scope_cliente.append(opts["seo_onpage"]["label"] + ".")

        n_copy = max(0, int(self.opt_copy_pages.get()))
        if n_copy:
            p = n_copy * float(opts["copywriting_per_page"]["price"])
            dev_extra += p
            option_lines.append(f"  Copywriting ({n_copy} pagine): {fmt_eur(p)}")
            scope_cliente.append(f"Copywriting professionale per {n_copy} pagina/e.")

        if self.opt_forms.get():
            p = float(opts["advanced_forms"]["price"])
            dev_extra += p
            option_lines.append(f"  {opts['advanced_forms']['label']}: {fmt_eur(p)}")
            scope_cliente.append(opts["advanced_forms"]["label"] + ".")

        if self.opt_crm.get():
            p = float(opts["crm_integration"]["price"])
            dev_extra += p
            option_lines.append(f"  {opts['crm_integration']['label']}: {fmt_eur(p)}")
            scope_cliente.append(opts["crm_integration"]["label"] + ".")

        if self.opt_elementor_pro.get():
            p = float(opts["elementor_pro_license"]["price"])
            dev_extra += p
            option_lines.append(f"  {opts['elementor_pro_license']['label']}: {fmt_eur(p)}")
            scope_cliente.append(
                "Licenza Elementor Pro (primo anno): voce a carico committente, come da preventivo."
            )

        if self.opt_speed.get():
            p = float(opts["speed_optimization"]["price"])
            dev_extra += p
            option_lines.append(f"  {opts['speed_optimization']['label']}: {fmt_eur(p)}")
            scope_cliente.append(opts["speed_optimization"]["label"] + ".")

        if self.opt_legal.get():
            p = float(opts["legal_pages_setup"]["price"])
            dev_extra += p
            option_lines.append(f"  {opts['legal_pages_setup']['label']}: {fmt_eur(p)}")
            scope_cliente.append(opts["legal_pages_setup"]["label"] + ".")

        ore = max(0.0, float(self.var_ore_extra.get()))
        if ore:
            rate = float(cfg["hourly_consulting"])
            p = ore * rate
            dev_extra += p
            option_lines.append(f"  Consulenza ({ore} h × {fmt_eur(rate)}): {fmt_eur(p)}")
            scope_cliente.append(
                f"Ore di consulenza / sviluppo su misura incluse in offerta: {ore:g} h."
            )

        if tipo == "ecommerce":
            extra_prod = max(0, int(self.var_prodotti_extra.get()))
            batch = int(cfg["ecommerce_extra_product_batch"]["batch_size"])
            price_batch = float(cfg["ecommerce_extra_product_batch"]["price"])
            if extra_prod > 0:
                batches = (extra_prod + batch - 1) // batch
                p = batches * price_batch
                dev_extra += p
                option_lines.append(
                    f"  Prodotti oltre pacchetto ({extra_prod} → {batches} blocchi da {batch}): {fmt_eur(p)}"
                )
                scope_cliente.append(
                    f"Inserimento catalogo esteso: circa {extra_prod} prodotti oltre il pacchetto base (stima a blocchi)."
                )

        imponibile_tecnico = subtotal_core + dev_extra
        margine_pct = max(0.0, min(float(self.var_margine_pct.get()), float(comm.get("margin_percent_max", 80))))
        sconto_pct = max(0.0, min(float(self.var_sconto_pct.get()), float(comm.get("discount_percent_max", 50))))
        pre_sconto = imponibile_tecnico * (1.0 + margine_pct / 100.0)
        importo_margine = pre_sconto - imponibile_tecnico
        imponibile_cliente = pre_sconto * (1.0 - sconto_pct / 100.0)
        importo_sconto = pre_sconto - imponibile_cliente
        iva_progetto = imponibile_cliente * (iva / 100.0)
        totale_progetto_iva = imponibile_cliente + iva_progetto

        pv_levels_cfg = comm.get("provvigione_by_complexity") or comm.get("provvigione_levels") or {}
        pv_default = {
            "standard": {"label": "Standard", "percent": 15},
            "medio": {"label": "Medio", "percent": 25},
            "alto": {"label": "Alto", "percent": 30},
        }
        pv_info = pv_levels_cfg.get(complessita_key)
        if not isinstance(pv_info, dict) or "percent" not in pv_info:
            pv_info = pv_default.get(complessita_key, pv_default["standard"])
        pv_pct = float(pv_info.get("percent", 15))
        pv_label = str(pv_info.get("label", complessita_key))
        pv_importo = imponibile_cliente * (pv_pct / 100.0)

        annual = 0.0
        annual_lines: list[str] = []
        scope_ricorrenti: list[str] = []
        maint = 0.0
        if self.opt_hosting.get():
            hm = cfg["hosting_annual_managed"]
            p = float(hm["price"])
            annual += p
            annual_lines.append(f"  {hm['label']}: {fmt_eur(p)} /anno (12 mesi)")
            scope_ricorrenti.append(
                f"hosting WordPress gestito 12 mesi (base {fmt_eur(p)}/anno + IVA)"
            )
            addons = cfg.get("hosting_addons_annual") or {}
            if self.opt_hosting_dr.get():
                item = addons.get("disaster_recovery") or {}
                ap = float(item.get("price", 0))
                if ap > 0:
                    annual += ap
                    annual_lines.append(f"  {item.get('label', 'Disaster recovery')}: {fmt_eur(ap)}")
                    scope_ricorrenti.append(item.get("label", "disaster recovery").lower())
            if self.opt_hosting_av.get():
                item = addons.get("antivirus_malware") or {}
                ap = float(item.get("price", 0))
                if ap > 0:
                    annual += ap
                    annual_lines.append(f"  {item.get('label', 'Antivirus')}: {fmt_eur(ap)}")
                    scope_ricorrenti.append(item.get("label", "antivirus").lower())
            if self.opt_hosting_bitninja.get():
                item = addons.get("bitninja") or {}
                ap = float(item.get("price", 0))
                if ap > 0:
                    annual += ap
                    annual_lines.append(f"  {item.get('label', 'BitNinja')}: {fmt_eur(ap)}")
                    scope_ricorrenti.append(item.get("label", "BitNinja").lower())
        if self.opt_domain.get():
            p = float(cfg["domain_annual"]["price"])
            annual += p
            annual_lines.append(f"  {cfg['domain_annual']['label']}: {fmt_eur(p)}")
            scope_ricorrenti.append(cfg["domain_annual"]["label"].lower())
        if self.opt_manutenzione.get():
            pct_m = float(cfg["maintenance_annual_percent_of_net"])
            minimum = float(cfg["maintenance_annual_minimum"])
            maint = max(minimum, imponibile_cliente * pct_m)
            annual += maint
            annual_lines.append(
                f"  Manutenzione annua (max tra minimo {fmt_eur(minimum)} e {pct_m*100:g}% sull'imponibile progetto al cliente): {fmt_eur(maint)}"
            )
            scope_ricorrenti.append(
                f"piano manutenzione annuale stimato ({fmt_eur(maint)} + IVA, soggetto a contratto)"
            )

        iva_ann = annual * (iva / 100.0) if annual else 0.0
        totale_annuale_iva = annual + iva_ann

        return {
            "iva": iva,
            "tipo": tipo,
            "base_info": base_info,
            "pagine": pagine,
            "included": included,
            "extra_pages": extra_pages,
            "base_price": base_price,
            "extra_cost": extra_cost,
            "extra_page_unit": float(cfg["extra_page_price"]),
            "complessita_key": complessita_key,
            "mult": mult,
            "subtotal_core": subtotal_core,
            "dev_extra": dev_extra,
            "option_lines": option_lines,
            "option_empty": dev_extra == 0.0,
            "imponibile_tecnico": imponibile_tecnico,
            "margine_pct": margine_pct,
            "sconto_pct": sconto_pct,
            "pre_sconto": pre_sconto,
            "importo_margine": importo_margine,
            "imponibile_cliente": imponibile_cliente,
            "importo_sconto": importo_sconto,
            "iva_progetto": iva_progetto,
            "totale_progetto_iva": totale_progetto_iva,
            "pv_pct": pv_pct,
            "pv_label": pv_label,
            "pv_importo": pv_importo,
            "annual": annual,
            "annual_lines": annual_lines,
            "iva_ann": iva_ann,
            "totale_annuale_iva": totale_annuale_iva,
            "maint": maint,
            "scope_cliente": scope_cliente,
            "scope_ricorrenti": scope_ricorrenti,
        }

    def _format_report(self, q: dict) -> list[str]:
        lines: list[str] = []
        cfg = self.cfg
        iva = q["iva"]
        base_info = q["base_info"]

        lines.append("=== PROGETTO (sviluppo) ===")
        lines.append(f"{base_info['label']}")
        lines.append(
            f"  Base: {fmt_eur(q['base_price'])}  |  Pagine incluse: {q['included']}  |  Pagine stimate: {q['pagine']}"
        )
        if q["extra_pages"]:
            lines.append(
                f"  Pagine extra ({q['extra_pages']} × {fmt_eur(q['extra_page_unit'])}): {fmt_eur(q['extra_cost'])}"
            )
        lines.append(f"  Moltiplicatore complessità ({q['complessita_key']}): ×{q['mult']}")
        lines.append(f"  Subtotale core: {fmt_eur(q['subtotal_core'])}")
        lines.append("")

        lines.append("=== OPZIONI ONE-OFF ===")
        if q["option_empty"]:
            lines.append("  (nessuna opzione selezionata)")
        else:
            lines.extend(q["option_lines"])
        lines.append(f"  Totale opzioni: {fmt_eur(q['dev_extra'])}")
        lines.append("")

        lines.append(f"Imponibile tecnico (core + opzioni, listino interno): {fmt_eur(q['imponibile_tecnico'])}")
        lines.append("")

        lines.append("=== POLITICA COMMERCIALE (sviluppo) ===")
        lines.append(
            f"  Margine / ricarico {q['margine_pct']:g}%: +{fmt_eur(q['importo_margine'])}  →  prima sconto: {fmt_eur(q['pre_sconto'])}"
        )
        if q["sconto_pct"] > 0:
            lines.append(f"  Sconto commerciale {q['sconto_pct']:g}%: −{fmt_eur(q['importo_sconto'])}")
        else:
            lines.append("  Sconto commerciale: nessuno")
        lines.append(f"  Imponibile progetto al cliente: {fmt_eur(q['imponibile_cliente'])}")
        lines.append("")
        lines.append(f"IVA {iva:g}% su imponibile cliente: {fmt_eur(q['iva_progetto'])}")
        lines.append(f"TOTALE PROGETTO CON IVA: {fmt_eur(q['totale_progetto_iva'])}")
        lines.append("")

        lines.append("=== INDICATORE PROVVIGIONE (interno, non in fattura) ===")
        lines.append(
            f"  Da complessità «{q['complessita_key']}» ({q['pv_label']}) — {q['pv_pct']:g}% sull'imponibile progetto al cliente ({fmt_eur(q['imponibile_cliente'])})"
        )
        lines.append(f"  Provvigione stimata (imponibile): {fmt_eur(q['pv_importo'])}")
        lines.append(
            "  Non sommare al totale cliente: è solo riferimento per il commerciale / piano provvigioni."
        )
        lines.append("")

        lines.append("=== VOCE ANNUALE (stima 1° anno, facoltative) ===")
        if q["annual"]:
            lines.extend(q["annual_lines"])
            lines.append(f"  Subtotale annuale stimato (imponibile): {fmt_eur(q['annual'])}")
            lines.append(f"  IVA {iva:g}% su annuale: {fmt_eur(q['iva_ann'])}")
            lines.append(f"  TOTALE ANNUALE CON IVA: {fmt_eur(q['totale_annuale_iva'])}")
        else:
            lines.append("  (nessuna voce annuale selezionata)")

        lines.append("")
        lines.append("--- Note ---")
        lines.append(base_info.get("description", ""))
        lines.append("")
        lines.append(
            "Le stime sono indicative: validare scope, contenuti e vincoli legali (privacy, cookie, e-commerce) prima dell'offerta vincolante."
        )
        return lines

    def _build_offerta_testo(self, q: dict) -> str:
        base_info = q["base_info"]
        titolo_tipo = base_info.get("label", "Sito web")
        oggetto = f"Offerta — {titolo_tipo} (WordPress + Elementor)"

        bullets = "\n".join(f"• {s}" for s in q["scope_cliente"])
        iva = q["iva"]

        blocco_prezzi = (
            f"Investimento una tantum (sviluppo e configurazione):\n"
            f"  imponibile {fmt_eur(q['imponibile_cliente'])}\n"
            f"  IVA {iva:g}% {fmt_eur(q['iva_progetto'])}\n"
            f"  totale {fmt_eur(q['totale_progetto_iva'])}\n"
        )

        if q["annual"] > 0:
            ric = ", ".join(q["scope_ricorrenti"]) if q["scope_ricorrenti"] else "voci ricorrenti"
            blocco_prezzi += (
                f"\nStima costi primo anno (ricorrenti, facoltativi / da contratto separato):\n"
                f"  imponibile {fmt_eur(q['annual'])}\n"
                f"  IVA {iva:g}% {fmt_eur(q['iva_ann'])}\n"
                f"  totale {fmt_eur(q['totale_annuale_iva'])}\n"
                f"(Dettaglio: {ric}.)\n"
            )

        testo_cliente = (
            f"Oggetto: {oggetto}\n\n"
            f"Gentile Cliente,\n\n"
            f"con riferimento alla Sua richiesta, inviamo un'offerta indicativa per il progetto descritto sinteticamente di seguito.\n\n"
            f"Ambito dei lavori (sintesi)\n"
            f"{bullets}\n\n"
            f"{blocco_prezzi}\n"
            f"L'offerta è da intendersi non vincolante fino a conferma scritta del perimetro funzionale, dei contenuti forniti dal Cliente e di eventuali integrazioni terze. "
            f"I tempi di consegna e le modalità di pagamento saranno definite in fase di ordine.\n\n"
            f"Cordiali saluti,\n"
            f"[Nome azienda / referente]\n"
        )

        interno = (
            f"{'─' * 60}\n"
            f"USO INTERNO — non inviare al cliente\n"
            f"{'─' * 60}\n\n"
            f"Imponibile tecnico (listino interno): {fmt_eur(q['imponibile_tecnico'])}\n"
            f"Margine applicato: {q['margine_pct']:g}%  |  Sconto commerciale: {q['sconto_pct']:g}%\n"
            f"Provvigione indicativa ({q['pv_label']}, {q['pv_pct']:g}% su imponibile cliente): {fmt_eur(q['pv_importo'])}\n"
            f"(La provvigione non compare nel testo per il cliente.)\n"
        )

        return testo_cliente + "\n\n" + interno

    def calcola(self) -> None:
        q = self._compute_quote()
        self._last_quote = q
        lines = self._format_report(q)
        self._last_text = "\n".join(lines)
        self.out.delete("1.0", END)
        self.out.insert("1.0", self._last_text)

    def apri_generatore_offerta(self) -> None:
        q = self._compute_quote()
        self._last_quote = q
        testo = self._build_offerta_testo(q)

        win = Toplevel(self.root)
        win.title("Generatore testo offerta (interno)")
        win.minsize(560, 480)
        if sys.platform == "darwin":
            win.configure(bg=_MAC_BG)

        if self._mac_tk:
            win.geometry("820x680")
            win.minsize(640, 480)
            win.transient(self.root)
            _mac_bring_to_front(win)
            win.after(50, lambda: win.focus_force())

            frm = tk.Frame(win, bg=_MAC_BG, padx=14, pady=12)
            frm.pack(fill="both", expand=True)
            tk.Label(
                frm,
                text="Bozza per email / documento: sezione superiore per il cliente, blocco «USO INTERNO» in calce.",
                bg=_MAC_BG,
                fg=_MAC_FG,
                font=_FONT_NOTE,
                wraplength=_MAC_WRAP,
                justify="left",
            ).pack(anchor="w", pady=(0, 10))
            txt = scrolledtext.ScrolledText(
                frm,
                height=24,
                wrap="word",
                font=_FONT_DIALOG,
                bg="#ffffff",
                fg=_MAC_FG,
                insertbackground=_MAC_FG,
                borderwidth=2,
                relief="solid",
                highlightthickness=0,
                padx=8,
                pady=8,
            )
            txt.pack(fill="both", expand=True, pady=(0, 10))
            txt.insert("1.0", testo)

            def copia_offerta() -> None:
                _mac_bring_to_front(win)
                win.clipboard_clear()
                win.clipboard_append(txt.get("1.0", END).rstrip())
                messagebox.showinfo("Copiato", "Testo offerta negli appunti.", parent=win)

            row = tk.Frame(frm, bg=_MAC_BG)
            row.pack(fill="x")
            _mac_button(row, text="Copia tutto", command=copia_offerta).pack(side="left")
            _mac_button(row, text="Chiudi", command=win.destroy).pack(side="left", padx=(12, 0))
        else:
            frm = ttk.Frame(win, padding=10)
            frm.pack(fill="both", expand=True)

            ttk.Label(
                frm,
                text="Bozza per email / documento: sezione superiore per il cliente, blocco «USO INTERNO» in calce.",
                wraplength=520,
            ).pack(anchor="w", pady=(0, 8))

            st_off: dict = {"height": 22, "wrap": "word", "font": _FONT_DIALOG}
            txt = scrolledtext.ScrolledText(frm, **st_off)
            txt.pack(fill="both", expand=True, pady=(0, 8))
            txt.insert("1.0", testo)

            def copia_offerta() -> None:
                win.clipboard_clear()
                win.clipboard_append(txt.get("1.0", END).rstrip())
                messagebox.showinfo("Copiato", "Testo offerta negli appunti.", parent=win)

            row = ttk.Frame(frm)
            row.pack(fill="x")
            ttk.Button(row, text="Copia tutto", command=copia_offerta).pack(side="left")
            ttk.Button(row, text="Chiudi", command=win.destroy).pack(side="left", padx=(8, 0))

    def copia(self) -> None:
        if not hasattr(self, "_last_text"):
            if self._mac_tk:
                _mac_bring_to_front(self.root)
            messagebox.showinfo("Info", "Calcola prima il preventivo.", parent=self.root)
            return
        if self._mac_tk:
            _mac_bring_to_front(self.root)
        self.root.clipboard_clear()
        self.root.clipboard_append(self._last_text)
        messagebox.showinfo("Copiato", "Riepilogo negli appunti.", parent=self.root)

    def esporta(self) -> None:
        if not hasattr(self, "_last_text"):
            if self._mac_tk:
                _mac_bring_to_front(self.root)
            messagebox.showinfo("Info", "Calcola prima il preventivo.", parent=self.root)
            return
        from tkinter import filedialog

        if self._mac_tk:
            _mac_bring_to_front(self.root)
        path = filedialog.asksaveasfilename(
            parent=self.root,
            defaultextension=".txt",
            filetypes=[("Testo", "*.txt"), ("Tutti i file", "*.*")],
            title="Salva preventivo",
        )
        if not path:
            return
        Path(path).write_text(self._last_text, encoding="utf-8")
        messagebox.showinfo("Salvato", path, parent=self.root)


def _mac_default_form(cfg: dict) -> tuple[dict[str, str], set[str]]:
    comm = cfg.get("commercial", {})
    keys = list(cfg["bases"].keys())
    default_tipo = "vetrina" if "vetrina" in keys else keys[0]
    base = cfg["bases"][default_tipo]
    fd: dict[str, str] = {
        "tipo": default_tipo,
        "pagine": str(int(base.get("included_pages", 5))),
        "complessita": "standard",
        "ore_extra": "0",
        "lingue_extra": "0",
        "prodotti_extra": "0",
        "copy_pages": "0",
        "margine": str(comm.get("margin_percent_default", 25)),
        "sconto": str(comm.get("discount_percent_default", 0)),
    }
    chk = {"hosting", "domain", "manutenzione", "wpml_license"}
    return fd, chk


def _mac_flat_from_post(qs: dict[str, list[str]]) -> dict[str, str]:
    return {k: (v[0] if v else "") for k, v in qs.items()}


def _mac_app_from_form(cfg: dict, flat: dict[str, str]) -> object:
    def ib(name: str, default: int = 0) -> _FV:
        try:
            return _FV(int(float(str(flat.get(name, default)).replace(",", "."))))
        except (TypeError, ValueError):
            return _FV(default)

    def fb(name: str) -> _FV:
        return _FV(flat.get(name) == "on")

    def ff(name: str, default: float = 0.0) -> _FV:
        try:
            return _FV(float(str(flat.get(name, default)).replace(",", ".")))
        except (TypeError, ValueError):
            return _FV(default)

    comm = cfg.get("commercial", {})
    bases = list(cfg["bases"].keys())
    tipo = str(flat.get("tipo", bases[0]))
    if tipo not in cfg["bases"]:
        tipo = bases[0]
    ck = list(cfg["complexity_multiplier"].keys())
    comp = str(flat.get("complessita", ck[0]))
    if comp not in cfg["complexity_multiplier"]:
        comp = ck[0]

    app = object.__new__(PreventivoApp)
    app.cfg = cfg
    app.var_tipo = _FV(tipo)
    app.var_pagine = ib("pagine", int(cfg["bases"][tipo]["included_pages"]))
    app.var_complessita = _FV(comp)
    app.var_ore_extra = ff("ore_extra", 0.0)
    app.var_lingue_extra = ib("lingue_extra", 0)
    app.var_prodotti_extra = ib("prodotti_extra", 0)
    app.opt_copy_pages = ib("copy_pages", 0)
    app.opt_woo_addon = fb("woo_addon")
    app.opt_seo = fb("seo")
    app.opt_forms = fb("forms")
    app.opt_crm = fb("crm")
    app.opt_elementor_pro = fb("elementor_pro")
    app.opt_speed = fb("speed")
    app.opt_legal = fb("legal")
    app.opt_hosting = fb("hosting")
    app.opt_hosting_dr = fb("hosting_dr")
    app.opt_hosting_av = fb("hosting_av")
    app.opt_hosting_bitninja = fb("hosting_bitninja")
    app.opt_domain = fb("domain")
    app.opt_manutenzione = fb("manutenzione")
    app.opt_wpml_license = fb("wpml_license")
    app.var_margine_pct = ff("margine", float(comm.get("margin_percent_default", 25)))
    app.var_sconto_pct = ff("sconto", float(comm.get("discount_percent_default", 0)))
    return app


def _mac_form_state_from_flat(flat: dict[str, str], cfg: dict) -> tuple[dict[str, str], set[str]]:
    fd, _ = _mac_default_form(cfg)
    for k in fd:
        if k in flat:
            fd[k] = flat[k]
    checks = {
        "woo_addon",
        "seo",
        "forms",
        "crm",
        "elementor_pro",
        "speed",
        "legal",
        "hosting",
        "hosting_dr",
        "hosting_av",
        "hosting_bitninja",
        "domain",
        "manutenzione",
        "wpml_license",
    }
    chk = {n for n in checks if flat.get(n) == "on"}
    return fd, chk


def _mac_web_page_html(
    cfg: dict,
    fd: dict[str, str],
    chk: set[str],
    report: str | None,
    offerta: str | None,
    error: str | None,
) -> str:
    def sel_tipo() -> str:
        lines: list[str] = []
        for k, info in cfg["bases"].items():
            lab = html.escape(str(info.get("label", k)))
            kk = html.escape(k)
            s = " selected" if fd.get("tipo") == k else ""
            lines.append(f'<option value="{kk}"{s}>{lab}</option>')
        return "\n".join(lines)

    def sel_comp() -> str:
        lines = []
        for k in cfg["complexity_multiplier"].keys():
            kk = html.escape(k)
            s = " selected" if fd.get("complessita") == k else ""
            lines.append(f'<option value="{kk}"{s}>{kk}</option>')
        return "\n".join(lines)

    def c(name: str) -> str:
        return " checked" if name in chk else ""

    hp = float(cfg.get("hosting_annual_managed", {}).get("price", 220))
    addons = cfg.get("hosting_addons_annual") or {}
    dr = addons.get("disaster_recovery") or {}
    av = addons.get("antivirus_malware") or {}
    bn = addons.get("bitninja") or {}

    err_html = f'<p class="err">{html.escape(error)}</p>' if error else ""

    rep_html = ""
    if report is not None:
        rep_html = (
            "<h2>Riepilogo</h2>"
            f'<pre id="report">{html.escape(report)}</pre>'
            "<p class=\"hint\">Seleziona il testo sopra e copia (⌘C), oppure usa il pulsante del browser.</p>"
        )

    off_html = ""
    if offerta is not None:
        off_html = (
            "<h2>Testo offerta (interno + cliente)</h2>"
            f'<pre id="offerta">{html.escape(offerta)}</pre>'
        )

    return f"""<!DOCTYPE html>
<html lang="it">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>Preventivo WP + Elementor</title>
<style>
body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  margin: 0; background: #e8e8e8; color: #111; font-size: 16px; line-height: 1.45; }}
main {{ max-width: 920px; margin: 0 auto; padding: 1rem 1.25rem 2rem; }}
h1 {{ font-size: 1.35rem; margin-bottom: 0.5rem; }}
.sub {{ color: #444; font-size: 0.95rem; margin-bottom: 1rem; }}
.grid {{ display: grid; grid-template-columns: minmax(180px, 240px) 1fr; gap: 0.5rem 1rem; align-items: center; margin: 0.35rem 0; }}
.grid label {{ text-align: right; font-weight: 500; }}
@media (max-width: 640px) {{ .grid {{ grid-template-columns: 1fr; }} .grid label {{ text-align: left; }} }}
fieldset {{ border: 1px solid #bbb; border-radius: 8px; padding: 0.75rem 1rem; margin: 1rem 0; background: #f5f5f5; }}
legend {{ font-weight: 600; padding: 0 0.35rem; }}
select, input[type="number"] {{ width: 100%; max-width: 420px; padding: 0.45rem 0.5rem; font-size: 1rem;
  border: 1px solid #888; border-radius: 6px; box-sizing: border-box; }}
.checkline {{ display: flex; align-items: flex-start; gap: 0.5rem; margin: 0.35rem 0; }}
.checkline input {{ margin-top: 0.25rem; }}
.actions {{ display: flex; flex-wrap: wrap; gap: 0.75rem; margin: 1.25rem 0; }}
button {{ padding: 0.55rem 1rem; font-size: 1rem; border-radius: 8px; border: 1px solid #333;
  background: #222; color: #fff; cursor: pointer; }}
button:hover {{ background: #444; }}
.err {{ background: #fdd; border: 1px solid #c00; padding: 0.75rem; border-radius: 6px; }}
pre {{ background: #fafafa; border: 1px solid #999; padding: 1rem; overflow: auto; max-height: 420px;
  font-size: 0.88rem; white-space: pre-wrap; border-radius: 6px; }}
.hint {{ font-size: 0.9rem; color: #555; }}
</style>
</head>
<body>
<main>
<h1>Preventivo siti WP + Elementor (Nordest)</h1>
<p class="sub">Stima indicativa. Listino: <code>prezzi_nordest.json</code>. Su macOS questa pagina web sostituisce la finestra Tk se il sistema non la disegna correttamente.</p>
{err_html}
<form method="post" action="/">
<div class="grid"><label for="tipo">Tipo progetto</label><select name="tipo" id="tipo">{sel_tipo()}</select></div>
<div class="grid"><label for="pagine">Pagine (stimate)</label><input type="number" name="pagine" id="pagine" min="1" max="200" value="{html.escape(fd.get("pagine", "5"))}"/></div>
<div class="grid"><label for="complessita">Complessità</label><select name="complessita" id="complessita">{sel_comp()}</select></div>
<div class="grid"><label for="ore_extra">Ore consulenza extra</label><input type="number" name="ore_extra" id="ore_extra" step="0.5" min="0" value="{html.escape(fd.get("ore_extra", "0"))}"/></div>
<div class="grid"><label for="lingue_extra">Lingue WPML oltre IT</label><input type="number" name="lingue_extra" id="lingue_extra" min="0" max="10" value="{html.escape(fd.get("lingue_extra", "0"))}"/></div>
<div class="grid"><label for="copy_pages">Pagine copywriting</label><input type="number" name="copy_pages" id="copy_pages" min="0" max="80" value="{html.escape(fd.get("copy_pages", "0"))}"/></div>
<div class="grid"><label for="prodotti_extra">Prodotti extra (e-commerce)</label><input type="number" name="prodotti_extra" id="prodotti_extra" min="0" value="{html.escape(fd.get("prodotti_extra", "0"))}"/></div>
<div class="grid"><label for="margine">Margine %</label><input type="number" name="margine" id="margine" step="0.5" min="0" value="{html.escape(fd.get("margine", "25"))}"/></div>
<div class="grid"><label for="sconto">Sconto %</label><input type="number" name="sconto" id="sconto" step="0.5" min="0" value="{html.escape(fd.get("sconto", "0"))}"/></div>

<fieldset><legend>Opzioni</legend>
<div class="checkline"><input type="checkbox" name="woo_addon" id="woo_addon" value="on"{c("woo_addon")}/><label for="woo_addon">E-commerce su base non e-commerce</label></div>
<div class="checkline"><input type="checkbox" name="seo" id="seo" value="on"{c("seo")}/><label for="seo">SEO on-page</label></div>
<div class="checkline"><input type="checkbox" name="forms" id="forms" value="on"{c("forms")}/><label for="forms">Form avanzati</label></div>
<div class="checkline"><input type="checkbox" name="crm" id="crm" value="on"{c("crm")}/><label for="crm">CRM / newsletter</label></div>
<div class="checkline"><input type="checkbox" name="elementor_pro" id="elementor_pro" value="on"{c("elementor_pro")}/><label for="elementor_pro">Licenza Elementor Pro (1 anno)</label></div>
<div class="checkline"><input type="checkbox" name="speed" id="speed" value="on"{c("speed")}/><label for="speed">Ottimizzazione velocità</label></div>
<div class="checkline"><input type="checkbox" name="legal" id="legal" value="on"{c("legal")}/><label for="legal">Privacy / cookie</label></div>
<div class="checkline"><input type="checkbox" name="wpml_license" id="wpml_license" value="on"{c("wpml_license")}/><label for="wpml_license">Licenza WPML 1 anno</label></div>
</fieldset>

<fieldset><legend>Ricorrenti</legend>
<div class="checkline"><input type="checkbox" name="hosting" id="hosting" value="on"{c("hosting")}/><label for="hosting">Hosting gestito (12 mesi, da {html.escape(fmt_eur(hp))}/anno + IVA)</label></div>
<div class="checkline"><input type="checkbox" name="hosting_dr" id="hosting_dr" value="on"{c("hosting_dr")}/><label for="hosting_dr">{html.escape(str(dr.get("label", "DR")))}</label></div>
<div class="checkline"><input type="checkbox" name="hosting_av" id="hosting_av" value="on"{c("hosting_av")}/><label for="hosting_av">{html.escape(str(av.get("label", "AV")))}</label></div>
<div class="checkline"><input type="checkbox" name="hosting_bitninja" id="hosting_bitninja" value="on"{c("hosting_bitninja")}/><label for="hosting_bitninja">{html.escape(str(bn.get("label", "BitNinja")))}</label></div>
<div class="checkline"><input type="checkbox" name="domain" id="domain" value="on"{c("domain")}/><label for="domain">Dominio 1° anno</label></div>
<div class="checkline"><input type="checkbox" name="manutenzione" id="manutenzione" value="on"{c("manutenzione")}/><label for="manutenzione">Manutenzione annua</label></div>
</fieldset>

<div class="actions">
<button type="submit" name="do" value="calc">Calcola riepilogo e offerta</button>
</div>
</form>
{rep_html}
{off_html}
</main>
</body>
</html>"""


def run_mac_web_ui() -> None:
    try:
        cfg = load_config()
    except Exception as e:
        print(f"Errore lettura config: {e}", file=sys.stderr)
        sys.exit(1)

    fd0, chk0 = _mac_default_form(cfg)

    class _H(BaseHTTPRequestHandler):
        def log_message(self, format: str, *args: object) -> None:
            return

        def do_GET(self) -> None:
            if self.path != "/" and not self.path.startswith("/?"):
                self.send_error(404)
                return
            page = _mac_web_page_html(cfg, fd0, chk0, None, None, None)
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(page.encode("utf-8"))

        def do_POST(self) -> None:
            if self.path != "/":
                self.send_error(404)
                return
            try:
                n = int(self.headers.get("Content-Length", "0"))
                body = self.rfile.read(n).decode("utf-8")
                flat = _mac_flat_from_post(urllib.parse.parse_qs(body, keep_blank_values=True))
                app = _mac_app_from_form(cfg, flat)
                q = PreventivoApp._compute_quote(app)
                report = "\n".join(PreventivoApp._format_report(app, q))
                offerta = PreventivoApp._build_offerta_testo(app, q)
                fd, chk = _mac_form_state_from_flat(flat, cfg)
                page = _mac_web_page_html(cfg, fd, chk, report, offerta, None)
            except Exception as e:
                fd, chk = fd0, chk0
                page = _mac_web_page_html(cfg, fd, chk, None, None, f"{type(e).__name__}: {e}")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(page.encode("utf-8"))

    srv = ThreadingHTTPServer(("127.0.0.1", 0), _H)
    port = srv.server_port
    th = threading.Thread(target=srv.serve_forever, daemon=True)
    th.start()
    url = f"http://127.0.0.1:{port}/"
    print(f"\n  Preventivatore (interfaccia web)\n  Apri nel browser: {url}\n  (solo questo computer — localhost)\n")
    try:
        webbrowser.open(url)
    except OSError:
        pass
    try:
        if sys.stdin.isatty():
            input("  Premi Invio per chiudere il server…\n")
        else:
            while True:
                time.sleep(3600)
    except (KeyboardInterrupt, EOFError):
        pass
    finally:
        srv.shutdown()


def main() -> None:
    if sys.platform == "darwin" and os.environ.get("PREVENTIVATORE_TK") != "1":
        run_mac_web_ui()
        return

    root = Tk()
    if sys.platform == "darwin":
        root.update_idletasks()
        # Con l'UI tk su macOS i font sono espliciti (14 pt); evitiamo tk scaling che spesso riduce troppo i controlli.
    style = ttk.Style()
    if sys.platform == "win32":
        style.theme_use("vista")
    elif sys.platform == "darwin":
        # «clam» disegna in modo esplicito; «aqua» a volte fallisce con certe build Tcl/Tk.
        for name in ("clam", "alt", "aqua"):
            if name in style.theme_names():
                style.theme_use(name)
                break
    try:
        PreventivoApp(root)
    except Exception as e:
        messagebox.showerror("Errore avvio", f"{type(e).__name__}: {e}\n\nDettaglio in Terminale se lanci da console.")
        raise
    root.mainloop()


if __name__ == "__main__":
    main()
