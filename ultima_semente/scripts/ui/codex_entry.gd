class_name CodexEntry
extends VBoxContainer
## Entrada do arquivo biológico (scenes/ui/codex_entry.tscn).

@onready var title_label: Label = %EntryTitle
@onready var body_label: Label = %EntryBody


func setup(title: String, body: String, locked: bool = false) -> void:
	title_label.text = title
	body_label.text = body
	body_label.visible = body != ""
	title_label.theme_type_variation = &"DimLabel" if locked else &"AccentLabel"
