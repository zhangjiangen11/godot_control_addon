#include "expandable_button.h"
#include <godot_cpp/core/class_db.hpp>
#include <godot_cpp/classes/engine.hpp>

using namespace godot;

void ExpandableButton::_bind_methods() {
    // Expansion Size Property
    ClassDB::bind_method(D_METHOD("set_expansion_size", "p_size"), &ExpandableButton::set_expansion_size);
	ClassDB::bind_method(D_METHOD("get_expansion_size"), &ExpandableButton::get_expansion_size);
	ClassDB::add_property("ExpandableButton", PropertyInfo(Variant::INT, "expansion_size"), "set_expansion_size", "get_expansion_size");
	// Expansion Indentation Property
	ClassDB::bind_method(D_METHOD("set_expansion_indentation", "p_indentation"), &ExpandableButton::set_expansion_indentation);
	ClassDB::bind_method(D_METHOD("get_expansion_indentation"), &ExpandableButton::get_expansion_indentation);
	ClassDB::add_property("ExpandableButton", PropertyInfo(Variant::INT, "expansion_indentation"), "set_expansion_indentation", "get_expansion_indentation");
	// Expansion Speed Property
	ClassDB::bind_method(D_METHOD("set_expansion_speed", "p_speed"), &ExpandableButton::set_expansion_speed);
	ClassDB::bind_method(D_METHOD("get_expansion_speed"), &ExpandableButton::get_expansion_speed);
	ClassDB::add_property("ExpandableButton", PropertyInfo(Variant::FLOAT, "expansion_speed"), "set_expansion_speed", "get_expansion_speed");
	// Expand Methods
	ClassDB::bind_method(D_METHOD("expand"), &ExpandableButton::expand);
	ClassDB::bind_method(D_METHOD("reduce"), &ExpandableButton::reduce);
}

ExpandableButton::ExpandableButton() {
	RevisedButton::set_is_text_off(true);

	// Initialize internal childs
	expansion_parent = memnew(Control);
	expansion = memnew(RevisedButton);
	idle_time_timer = memnew(Timer);
	base = memnew(Button);

    // Create internal tree
	add_child(expansion_parent, false, INTERNAL_MODE_FRONT);
	expansion_parent->add_child(expansion, false, INTERNAL_MODE_FRONT);
	expansion_parent->add_child(idle_time_timer, false, INTERNAL_MODE_FRONT);
	add_child(base, false, INTERNAL_MODE_FRONT);

	// Setup childs
	idle_time_timer->set_one_shot(true);
	expansion_parent->set_clip_contents(true);
    expansion_parent->set_mouse_filter(Control::MouseFilter::MOUSE_FILTER_IGNORE);
	Error err1 = idle_time_timer->connect("timeout", Callable(this, "on_timer_out"));
	set_expansion_size(expansion_size);
	reduce();
}

ExpandableButton::~ExpandableButton() {
	expansion_parent->queue_free();
	expansion->queue_free();
	idle_time_timer->queue_free();
	base->queue_free();
}

void ExpandableButton::update_base_size() {
    Vector2 b_siz = base->get_size();
    //Vector2 ep_siz = expansion_parent->get_size();
    b_siz.y = old_size.y;
    b_siz.x = old_size.x;
    base->set_size(b_siz);
}

void ExpandableButton::expand() {
    //expansion_parent->show();
    is_expanded = true;
}

void ExpandableButton::reduce() {
    //expansion_parent->hide();
    is_expanded = false;
}

void ExpandableButton::_process(double delta) {
    RevisedButton::_process(delta);
    double height = get_size().y;
    double width = get_size().x;
    Vector2 siz = expansion_parent->get_size();
    Vector2 pos = expansion_parent->get_position();
    Vector2 pos_ex = expansion->get_position();

    if(old_size.y!=height) {
        old_size.y = height;
        siz.y = height;
    }

    if(Engine::get_singleton()->is_editor_hint()) {
        if(old_size.x!=width)
            old_size.x = width;

        expansion->set_size(Vector2(expansion_size+expansion_indentation,siz.y));
        pos_ex.x = pos_ex.x+expansion_indentation;
        double delta_speed = delta*speed*expansion_size/10;

        if(siz.x>expansion_size){
            siz.x -= delta_speed;
            width -= delta_speed;
        }
        if(is_expanded){
            if(siz.x+delta_speed<=expansion_size) siz.x += delta_speed;
            if(pos_ex.x+delta_speed<=0) pos_ex.x+=delta_speed;
            else pos_ex.x = 0;
        }
        if(!is_expanded){
            if(siz.x>0) siz.x -= delta_speed;
            if(pos_ex.x>-expansion_size) pos_ex.x-=delta_speed;
        }
        width = siz.x+old_size.x;
        pos.x = width-siz.x;
        pos_ex.x = pos_ex.x-expansion_indentation;

    } else {
        if(old_size.x!=width-siz.x)
            old_size.x = width-siz.x;

        expansion->set_size(Vector2(expansion_size+expansion_indentation,siz.y));
        pos_ex.x = pos_ex.x+expansion_indentation;
        double delta_speed = delta*speed*expansion_size/10;

        if(siz.x>expansion_size){
            siz.x -= delta_speed;
            width -= delta_speed;
        }
        if(is_expanded){
            if(siz.x+delta_speed<=expansion_size) siz.x += delta_speed;
            if(pos_ex.x+delta_speed<=0) pos_ex.x+=delta_speed;
            else pos_ex.x = 0;
        }
        if(!is_expanded){
            if(siz.x>0) siz.x -= delta_speed;
            if(pos_ex.x>-expansion_size) pos_ex.x-=delta_speed;
        }
        width = siz.x+old_size.x;
        pos.x = width-siz.x;
        pos_ex.x = pos_ex.x-expansion_indentation;

        set_size(Vector2(width,height));
    }

    expansion_parent->set_size(siz);
    expansion_parent->set_position(pos);
    expansion->set_position(pos_ex);
    base->set_size(old_size);//update_base_size();

    Ref<Texture2D> texture = get_button_icon();
    Ref<Texture2D> texture2 = base->get_button_icon();
    if(texture!=texture2) {
        base->set_button_icon(texture);
    }
}

void ExpandableButton::set_is_text_off(bool p_status) {
    is_text_off = p_status;
}

bool ExpandableButton::get_is_text_off() {
    return is_text_off;
}

void ExpandableButton::set_expansion_size(int p_size) {
    expansion_size_full = p_size;
    expansion_size = p_size - expansion_indentation;
}

int ExpandableButton::get_expansion_size() {
    return expansion_size_full;
}

void ExpandableButton::set_expansion_indentation(int p_indentation) {
    expansion_indentation = p_indentation;
    expansion_size = expansion_size_full - expansion_indentation;
    Vector2 pos = expansion_parent->get_position();
    pos.x = old_size.x-expansion_indentation;
    expansion_parent->set_position(pos);
}

int ExpandableButton::get_expansion_indentation() {
    return expansion_indentation;
}

void ExpandableButton::set_expansion_speed(double p_speed) {
    speed = p_speed;
}

double ExpandableButton::get_expansion_speed() {
    return speed;
}
