import bpy
from time import time

def get_prefs():
    return bpy.context.preferences.addons['BDSM'].preferences


def navigation_passthrough(event, alt=True, wheel=False):
    if alt and wheel:
        return event.type in {'MIDDLEMOUSE'} or event.type.startswith('NDOF') or (event.alt and event.type in {'LEFTMOUSE', 'RIGHTMOUSE'} and event.value == 'PRESS') or event.type in {'WHEELUPMOUSE', 'WHEELDOWNMOUSE'}
    elif alt:
        return event.type in {'MIDDLEMOUSE'} or event.type.startswith('NDOF') or (event.alt and event.type in {'LEFTMOUSE', 'RIGHTMOUSE'} and event.value == 'PRESS')
    elif wheel:
        return event.type in {'MIDDLEMOUSE'} or event.type.startswith('NDOF') or event.type in {'WHEELUPMOUSE', 'WHEELDOWNMOUSE'}
    else:
        return event.type in {'MIDDLEMOUSE'} or event.type.startswith('NDOF')

def init_timer_modal(self, debug=False):

    self.start = time()

    self.countdown = self.time * get_prefs().machin3_punchit_modal_hud_timeout

    if debug:
        print(f"initiating timer with a countdown of {self.time}s ({self.time * get_prefs().machin3_punchit_modal_hud_timeout}s)")

def set_countdown(self, debug=False):
    self.countdown = self.time * get_prefs().machin3_punchit_modal_hud_timeout - (time() - self.start)

    if debug:
        print("countdown:", self.countdown)

def get_timer_progress(self, debug=False):

    progress =  self.countdown / (self.time * get_prefs().machin3_punchit_modal_hud_timeout)

    if debug:
        print("progress:", progress)

    return progress

def ignore_events(event, none=True, timer=True, timer_report=True):
    ignore = ['INBETWEEN_MOUSEMOVE', 'WINDOW_DEACTIVATE']

    if none:
        ignore.append('NONE')

    if timer:
        ignore.extend(['TIMER', 'TIMER1', 'TIMER2', 'TIMER3'])

    if timer_report:
        ignore.append('TIMER_REPORT')

    return event.type in ignore

def force_ui_update(context, active=None):
    if context.mode == 'OBJECT':
        if active:
            active.select_set(True)
        else:
            visible = context.visible_objects
            if visible:
                visible[0].select_set(visible[0].select_get())
    elif context.mode == 'EDIT_MESH':
        context.active_object.select_set(True)