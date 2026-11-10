"""Gera ui/game_theme.tres (tema em pixel art). Rode depois de gen_ui_*.py."""
import os
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
UI = "res://assets/art/ui/"

ext = {}   # id -> (type, path)
subs = []  # (id, type, body)


def tex(key, fname):
    ext["tx_" + key] = ("Texture2D", UI + fname)
    return "tx_" + key


def box(sid, key, fname, m, cm=None, draw_center=True, axis=None, extra=""):
    t = tex(key, fname)
    lines = ['texture = ExtResource("%s")' % t]
    ml, mt, mr, mb = m if isinstance(m, (tuple, list)) else (m, m, m, m)
    lines += ["texture_margin_left = %s" % float(ml), "texture_margin_top = %s" % float(mt),
              "texture_margin_right = %s" % float(mr), "texture_margin_bottom = %s" % float(mb)]
    if cm:
        cl, ct, cr, cb = cm
        lines += ["content_margin_left = %s" % float(cl), "content_margin_top = %s" % float(ct),
                  "content_margin_right = %s" % float(cr), "content_margin_bottom = %s" % float(cb)]
    if not draw_center:
        lines.append("draw_center = false")
    if axis:
        lines.append("axis_stretch_horizontal = %d" % axis)
    if extra:
        lines.append(extra)
    subs.append((sid, "StyleBoxTexture", "\n".join(lines)))
    return sid


def empty(sid):
    subs.append((sid, "StyleBoxEmpty", ""))
    return sid


ext["pixel_font"] = ("FontFile", UI + "pixel.ttf")

BTN_CM = (14, 8, 14, 10)
sb_norm = box("sb_btn_n", "bnorm", "button_normal.png", 8, BTN_CM)
sb_hov = box("sb_btn_h", "bhov", "button_hover.png", 8, BTN_CM)
sb_pre = box("sb_btn_p", "bpre", "button_pressed.png", 8, (14, 10, 14, 8))
sb_dis = box("sb_btn_d", "bdis", "button_disabled.png", 8, BTN_CM)
sb_foc = box("sb_btn_f", "bfoc", "button_focus.png", 8, BTN_CM, draw_center=False)
PAN_CM = (16, 14, 16, 14)
sb_modal = box("sb_modal", "modal", "panel_modal.png", 12, PAN_CM)
sb_card = box("sb_card", "card", "panel_card.png", 12, (14, 12, 14, 12))
sb_evo = box("sb_evo", "evo", "panel_card_evo.png", 12, (14, 12, 14, 12))
sb_owned = box("sb_owned", "owned", "panel_card_owned.png", 12, (14, 12, 14, 12))
sb_detail = box("sb_detail", "card", "panel_card.png", 12, (14, 12, 14, 12))
sb_hud = box("sb_hud", "hud", "panel_hud.png", 8, (12, 8, 12, 8))
sb_boss = box("sb_boss", "boss", "panel_boss.png", 12, (14, 10, 14, 10))
sb_skill = box("sb_skill", "hud", "panel_hud.png", 8, (8, 6, 8, 6))
sb_bar_bg = box("sb_bar_bg", "barbg", "bar_bg.png", (2, 3, 2, 3))
sb_hp = box("sb_hp", "hp", "bar_hp.png", (2, 4, 2, 4))
sb_o2 = box("sb_o2", "o2", "bar_o2.png", (2, 4, 2, 4))
sb_xp = box("sb_xp", "xp", "bar_xp.png", (2, 4, 2, 4))
sb_bossbar = box("sb_bossbar", "bossbar", "bar_boss.png", (2, 4, 2, 4))
sb_slider = box("sb_slider", "sgroove", "slider_groove.png", (3, 3, 3, 3), (0, 5, 0, 5))
sb_sfill = box("sb_sfill", "sfill", "slider_fill.png", (3, 3, 3, 3), (0, 5, 0, 5))
sb_scroll = box("sb_scroll", "scbg", "scroll_bg.png", 3, (5, 5, 5, 5))
sb_grab = box("sb_grab", "scgr", "scroll_grabber.png", 3, (5, 5, 5, 5))
sb_tab_s = box("sb_tab_s", "tabs", "tab_selected.png", (8, 8, 8, 4), (14, 6, 14, 6))
sb_tab_u = box("sb_tab_u", "tabu", "tab_unselected.png", (8, 8, 8, 4), (14, 6, 14, 6))
sb_tab_h = box("sb_tab_h", "tabh", "tab_hover.png", (8, 8, 8, 4), (14, 6, 14, 6))
sb_tab_p = box("sb_tab_p", "tabp", "tab_panel.png", 6, (6, 6, 6, 6))
sb_sep = box("sb_sep", "sep", "separator.png", (9, 0, 9, 0), None)
e_empty = empty("sb_empty")
ext["tx_tick"] = ("Texture2D", UI + "slider_tick.png")
ext["tx_grab"] = ("Texture2D", UI + "slider_grabber.png")
ext["tx_grab_hi"] = ("Texture2D", UI + "slider_grabber_hi.png")
ext["tx_chk_on"] = ("Texture2D", UI + "check_on.png")
ext["tx_chk_off"] = ("Texture2D", UI + "check_off.png")
ext["tx_chk_on_hi"] = ("Texture2D", UI + "check_on_hi.png")
ext["tx_chk_off_hi"] = ("Texture2D", UI + "check_off_hi.png")

R = []
a = R.append
a('default_font = ExtResource("pixel_font")')
a("default_font_size = 16")
a("Label/colors/font_color = Color(0.9, 0.96, 0.93, 1)")
a("Label/colors/font_shadow_color = Color(0.02, 0.04, 0.08, 0.75)")
a("Label/constants/shadow_offset_x = 2")
a("Label/constants/shadow_offset_y = 2")
a("Button/colors/font_color = Color(0.82, 0.95, 0.9, 1)")
a("Button/colors/font_hover_color = Color(1, 1, 1, 1)")
a("Button/colors/font_pressed_color = Color(0.56, 0.88, 0.75, 1)")
a("Button/colors/font_disabled_color = Color(0.36, 0.46, 0.45, 1)")
a("Button/colors/font_focus_color = Color(1, 1, 1, 1)")
a("Button/colors/font_outline_color = Color(0.02, 0.05, 0.06, 1)")
a("Button/font_sizes/font_size = 16")
a('Button/styles/normal = SubResource("%s")' % sb_norm)
a('Button/styles/hover = SubResource("%s")' % sb_hov)
a('Button/styles/pressed = SubResource("%s")' % sb_pre)
a('Button/styles/disabled = SubResource("%s")' % sb_dis)
a('Button/styles/focus = SubResource("%s")' % sb_foc)
# CheckBox: sem o estilo de botão (o Godot herdaria Button/normal)
a("CheckBox/colors/font_color = Color(0.9, 0.96, 0.93, 1)")
a("CheckBox/colors/font_hover_color = Color(1, 1, 1, 1)")
a("CheckBox/colors/font_pressed_color = Color(0.56, 0.88, 0.75, 1)")
a("CheckBox/constants/h_separation = 10")
for st in ("normal", "hover", "pressed", "disabled", "hover_pressed"):
    a('CheckBox/styles/%s = SubResource("%s")' % (st, e_empty))
a('CheckBox/styles/focus = SubResource("%s")' % sb_foc)
a('CheckBox/icons/checked = ExtResource("tx_chk_on")')
a('CheckBox/icons/unchecked = ExtResource("tx_chk_off")')
a('CheckBox/icons/checked_disabled = ExtResource("tx_chk_on")')
a('CheckBox/icons/unchecked_disabled = ExtResource("tx_chk_off")')
a('CheckBox/icons/radio_checked = ExtResource("tx_chk_on_hi")')
a('CheckBox/icons/radio_unchecked = ExtResource("tx_chk_off_hi")')
# sliders
a('HSlider/styles/slider = SubResource("%s")' % sb_slider)
a('HSlider/styles/grabber_area = SubResource("%s")' % sb_sfill)
a('HSlider/styles/grabber_area_highlight = SubResource("%s")' % sb_sfill)
a('HSlider/icons/grabber = ExtResource("tx_grab")')
a('HSlider/icons/grabber_highlight = ExtResource("tx_grab_hi")')
a('HSlider/icons/grabber_disabled = ExtResource("tx_grab")')
a("HSlider/constants/center_grabber = 0")
a('HSlider/icons/tick = ExtResource("tx_tick")')
# scrollbars
for sbn in ("VScrollBar", "HScrollBar"):
    a('%s/styles/scroll = SubResource("%s")' % (sbn, sb_scroll))
    a('%s/styles/scroll_focus = SubResource("%s")' % (sbn, sb_scroll))
    a('%s/styles/grabber = SubResource("%s")' % (sbn, sb_grab))
    a('%s/styles/grabber_highlight = SubResource("%s")' % (sbn, sb_grab))
    a('%s/styles/grabber_pressed = SubResource("%s")' % (sbn, sb_grab))
# abas
a('TabContainer/styles/tab_selected = SubResource("%s")' % sb_tab_s)
a('TabContainer/styles/tab_unselected = SubResource("%s")' % sb_tab_u)
a('TabContainer/styles/tab_hovered = SubResource("%s")' % sb_tab_h)
a('TabContainer/styles/tab_disabled = SubResource("%s")' % sb_tab_u)
a('TabContainer/styles/tab_focus = SubResource("%s")' % sb_foc)
a('TabContainer/styles/panel = SubResource("%s")' % sb_tab_p)
a("TabContainer/colors/font_selected_color = Color(0.82, 0.98, 0.9, 1)")
a("TabContainer/colors/font_unselected_color = Color(0.5, 0.68, 0.64, 1)")
a("TabContainer/colors/font_hovered_color = Color(0.9, 1, 0.95, 1)")
a("TabContainer/font_sizes/font_size = 16")
# separador e containers
a('HSeparator/styles/separator = SubResource("%s")' % sb_sep)
a("HSeparator/constants/separation = 9")
a('PanelContainer/styles/panel = SubResource("%s")' % sb_card)
a('TooltipPanel/styles/panel = SubResource("%s")' % sb_hud)
a("VBoxContainer/constants/separation = 8")
a("HBoxContainer/constants/separation = 10")
for nm, sbid in (("ModalPanel", sb_modal), ("CardPanel", sb_card), ("EvoCardPanel", sb_evo), ("OwnedCardPanel", sb_owned),
                 ("DetailPanel", sb_detail), ("HudPanel", sb_hud), ("BossPanel", sb_boss), ("SkillPanel", sb_skill)):
    a('%s/base_type = &"PanelContainer"' % nm)
    a('%s/styles/panel = SubResource("%s")' % (nm, sbid))
a('TitleLabel/base_type = &"Label"')
a("TitleLabel/colors/font_color = Color(0.56, 0.88, 0.75, 1)")
a("TitleLabel/colors/font_shadow_color = Color(0.1, 0.06, 0.2, 0.95)")
a("TitleLabel/constants/shadow_offset_x = 3")
a("TitleLabel/constants/shadow_offset_y = 3")
a("TitleLabel/font_sizes/font_size = 32")
for nm, col in (("DimLabel", "0.52, 0.68, 0.64"), ("GoodLabel", "0.6, 0.95, 0.55"), ("BadLabel", "1, 0.5, 0.56"),
                ("WarnLabel", "1, 0.85, 0.4"), ("BioLabel", "0.82, 0.96, 0.45"), ("NucLabel", "0.55, 0.88, 1"),
                ("AccentLabel", "0.56, 0.88, 0.75")):
    a('%s/base_type = &"Label"' % nm)
    a("%s/colors/font_color = Color(%s, 1)" % (nm, col))
for nm, fill in (("HpBar", sb_hp), ("O2Bar", sb_o2), ("XpBar", sb_xp), ("BossBar", sb_bossbar)):
    a('%s/base_type = &"ProgressBar"' % nm)
    a('%s/styles/fill = SubResource("%s")' % (nm, fill))
    a('%s/styles/background = SubResource("%s")' % (nm, sb_bar_bg))

out = ["[gd_resource type=\"Theme\" load_steps=%d format=3]\n" % (len(ext) + len(subs) + 1)]
for k, (typ, path) in ext.items():
    out.append('[ext_resource type="%s" path="%s" id="%s"]' % (typ, path, k))
out.append("")
for sid, typ, body in subs:
    out.append('[sub_resource type="%s" id="%s"]' % (typ, sid))
    if body:
        out.append(body)
    out.append("")
out.append("[resource]")
out += R
open(os.path.join(ROOT, "ui", "game_theme.tres"), "w", encoding="utf-8").write("\n".join(out) + "\n")
print("tema escrito:", len(ext), "recursos,", len(subs), "estilos")
