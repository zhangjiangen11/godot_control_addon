@tool
extends EditorPlugin

var D:Documentation
var Edited_Node:ExpandableButton
var project = ProjectSettings
var my_theme:Theme
var Loader = ResourceLoader
var Saver = ResourceSaver
var inspector_plugin

func _enter_tree():
	D = Documentation.new()
	print_rich("[color=YELLOW_GREEN]● Control++:  Loading...\n	  «»-«»-«»")
	#print_rich("[color=VIOLET]● Control++:  The documentation for GDExtension is not suported![/color]")
	inspector_plugin = preload("res://addons/Control++/inspector_plugin.gd").new()
	add_inspector_plugin(inspector_plugin)
	Edited_Node = ExpandableButton.new()
	my_theme = Loader.load("res://addons/Control++/_ExpandableButton_hidden.theme","Theme")
	var project_theme_path = project.get_setting("gui/theme/custom")
	print_rich("[color=YELLOW_GREEN]	  «»-«»-«»\n● Control++:  Loaded![color=SNOW]")

func _process(delta):
	if D.pass_time(delta,2):
		var project_theme_path = project.get_setting("gui/theme/custom")
		#print_rich("[color=YELLOW_GREEN]● Control++:  gui/theme/custom == "+project_theme+"[/color]")
		if project_theme_path == "":
			print_rich("[color=YELLOW_GREEN]● Control++:  gui/theme/custom == null[/color]")
			project.set_setting("gui/theme/custom","res://project_theme.theme")
			project_theme_path = "res://project_theme.theme"
		var project_theme = Theme.new()
		if Loader.exists(project_theme_path,"Theme"):
			project_theme = Loader.load(project_theme_path,"Theme")
		project_theme.merge_with(my_theme)
		project_theme.add_type("RevisedButton")
		Saver.save(project_theme,project_theme_path)

func _handles(object: Object):
	if object is ExpandableButton:
		return true

func _edit(object: Object):
	#print(object)
	if !object:
		#print(Edited_Node," reduced because of ",object)
		Edited_Node.reduce()
		return
	if object is ExpandableButton:
		if object != Edited_Node:
			#print(Edited_Node," reduced")
			Edited_Node.reduce()
		Edited_Node = object
		#print(Edited_Node," expanded")
		Edited_Node.expand()


func _exit_tree():
	remove_inspector_plugin(inspector_plugin)
	project.save()
	pass
