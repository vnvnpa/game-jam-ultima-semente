class_name RecordPopup
extends Control
## Janela de registro narrativo. Layout em scenes/ui/record_popup.tscn.

signal closed

@onready var title_label: Label = %RecordTitle
@onready var text_label: Label = %RecordText
@onready var close_button: Button = %CloseButton


func _ready() -> void:
	close_button.pressed.connect(func() -> void: closed.emit())
	UIKit.wire_buttons(self)


func setup(title: String, text: String) -> void:
	title_label.text = title
	text_label.text = text
