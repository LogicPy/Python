#!/usr/bin/env python3
import cairo
import ctypes
import ctypes.util
import os
import random
import subprocess
import sys
import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
from gi.repository import Gdk, GLib, Gtk

# Native C-Level PAM Authentication via ctypes
libpam = ctypes.CDLL(ctypes.util.find_library("pam") or "libpam.so.0")

class PamHandle(ctypes.Structure):
    pass

class PamMessage(ctypes.Structure):
    _fields_ = [("msg_style", ctypes.c_int), ("msg", ctypes.c_char_p)]

class PamResponse(ctypes.Structure):
    _fields_ = [("resp", ctypes.c_char_p), ("resp_retcode", ctypes.c_int)]

PAM_CONV_FUNC = ctypes.CFUNCTYPE(
    ctypes.c_int,
    ctypes.c_int,
    ctypes.POINTER(ctypes.POINTER(PamMessage)),
    ctypes.POINTER(ctypes.POINTER(PamResponse)),
    ctypes.c_void_p,
)

class PamConv(ctypes.Structure):
    _fields_ = [("conv", PAM_CONV_FUNC), ("appdata_ptr", ctypes.c_void_p)]

def pam_authenticate(username, password):
    """Authenticate username and password directly against system libpam."""
    libc = ctypes.CDLL(None)
    
    def conv_cb(num_msg, msg, resp, appdata_ptr):
        reply_size = ctypes.sizeof(PamResponse) * num_msg
        p_reply = libc.malloc(reply_size)
        ctypes.memset(p_reply, 0, reply_size)
        
        reply_arr = (PamResponse * num_msg).from_address(p_reply)
        for i in range(num_msg):
            pwd_bytes = password.encode("utf-8")
            pwd_len = len(pwd_bytes) + 1
            buf = libc.malloc(pwd_len)
            ctypes.memmove(buf, pwd_bytes, pwd_len)
            reply_arr[i].resp = ctypes.cast(buf, ctypes.c_char_p)
            reply_arr[i].resp_retcode = 0

        resp[0] = ctypes.cast(p_reply, ctypes.POINTER(PamResponse))
        return 0

    callback = PAM_CONV_FUNC(conv_cb)
    conv = PamConv(callback, None)
    pamh = ctypes.POINTER(PamHandle)()

    res = libpam.pam_start(b"login", username.encode("utf-8"), ctypes.byref(conv), ctypes.byref(pamh))
    if res == 0:
        res = libpam.pam_authenticate(pamh, 0)
    libpam.pam_end(pamh, res)
    return res == 0


def set_super_key_enabled(enabled: bool):
    """Temporarily disables or re-enables Pop!_OS / Gnome Shell overlay hotkeys."""
    try:
        val = "'Super_L'" if enabled else "''"
        subprocess.run(
            ["gsettings", "set", "org.gnome.mutter", "overlay-key", val],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    except Exception:
        pass


class MatrixCanvas(Gtk.DrawingArea):
    """Cairo Canvas for rendering falling green Matrix code rain with persistent black background."""

    def __init__(self):
        super().__init__()
        self.connect("draw", self.on_draw)

        self.chars = [chr(i) for i in range(0x30A0, 0x30FF)] + [
            str(i) for i in range(10)
        ] + ["#", "$", "*", "%", "@"]
        self.font_size = 18
        self.drops = []
        self.initialized = False
        self.surface = None

        GLib.timeout_add(33, self.update_frame)

    def init_drops(self, width):
        columns = int(width / self.font_size) + 1
        self.drops = [random.randint(-50, 0) for _ in range(columns)]
        self.initialized = True

    def update_frame(self):
        self.queue_draw()
        return True

    def on_draw(self, widget, cr):
        alloc = self.get_allocation()
        width, height = alloc.width, alloc.height

        if not self.initialized:
            self.init_drops(width)

        if (
            self.surface is None
            or self.surface.get_width() != width
            or self.surface.get_height() != height
        ):
            self.surface = cr.get_target().create_similar(
                cairo.CONTENT_COLOR, width, height
            )
            s_cr = cairo.Context(self.surface)
            s_cr.set_source_rgb(0.0, 0.0, 0.0)
            s_cr.rectangle(0, 0, width, height)
            s_cr.fill()

        s_cr = cairo.Context(self.surface)
        s_cr.set_source_rgba(0.0, 0.0, 0.0, 0.12)
        s_cr.rectangle(0, 0, width, height)
        s_cr.fill()

        s_cr.select_font_face("Noto Sans CJK JP", 0, 0)
        s_cr.set_font_size(self.font_size)

        for i, y in enumerate(self.drops):
            x = i * self.font_size
            char = random.choice(self.chars)

            s_cr.set_source_rgb(0.0, 0.7, 0.2)
            s_cr.move_to(x, y * self.font_size)
            s_cr.show_text(char)

            if y * self.font_size > height and random.random() > 0.975:
                self.drops[i] = 0
            else:
                self.drops[i] += 1

        cr.set_source_surface(self.surface, 0, 0)
        cr.paint()


class SecondaryLockWindow(Gtk.Window):
    """Secondary Monitor display running Matrix animation overlay."""
    def __init__(self, display, monitor):
        super().__init__()
        self.connect("delete-event", lambda w, e: True)
        self.set_keep_above(True)
        self.set_decorated(False)
        self.set_skip_taskbar_hint(True)
        self.set_skip_pager_hint(True)
        
        geometry = monitor.get_geometry()
        self.move(geometry.x, geometry.y)
        self.resize(geometry.width, geometry.height)
        self.fullscreen_on_monitor(display.get_default_screen(), display.get_n_monitors() - 1)

        canvas = MatrixCanvas()
        self.add(canvas)


class MainLockWindow(Gtk.Window):

    def __init__(self, secondary_windows):
        super().__init__(title="Matrix Terminal Lock")
        self.secondary_windows = secondary_windows

        # Block close signals & keys
        self.connect("delete-event", self.on_delete_event)
        self.connect("key-press-event", self.on_key_press_event)

        self.fullscreen()
        self.set_keep_above(True)
        self.set_decorated(False)
        self.set_skip_taskbar_hint(True)
        self.set_skip_pager_hint(True)

        self.connect("map-event", self.on_map_grab_inputs)

        overlay = Gtk.Overlay()
        self.add(overlay)

        self.canvas = MatrixCanvas()
        overlay.add(self.canvas)

        css = b"""
        .lock-card {
            background-color: rgba(13, 13, 13, 0.85);
            border: 2px solid #00ff66;
            border-radius: 8px;
            padding: 30px;
        }
        label { color: #00ff66; font-size: 20px; font-family: monospace; }
        entry { 
            background-color: #1a1a1a; 
            color: #00ff66; 
            border: 1px solid #00ff66; 
            font-size: 18px; 
            padding: 8px;
            font-family: monospace;
        }
        """
        provider = Gtk.CssProvider()
        provider.load_from_data(css)
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(), provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        vbox.get_style_context().add_class("lock-card")
        vbox.set_valign(Gtk.Align.CENTER)
        vbox.set_halign(Gtk.Align.CENTER)

        self.status_label = Gtk.Label(label="[ SYSTEM LOCKED ]\nEnter Password:")
        vbox.pack_start(self.status_label, True, True, 0)

        self.password_entry = Gtk.Entry()
        self.password_entry.set_visibility(False)
        self.password_entry.connect("activate", self.on_unlock)
        vbox.pack_start(self.password_entry, True, True, 0)

        overlay.add_overlay(vbox)

    def on_delete_event(self, widget, event):
        return True

    def on_key_press_event(self, widget, event):
        if (event.state & Gdk.ModifierType.MOD1_MASK) and event.keyval == Gdk.KEY_F4:
            return True
        if event.keyval in (Gdk.KEY_Super_L, Gdk.KEY_Super_R, Gdk.KEY_Hyper_L, Gdk.KEY_Hyper_R):
            return True
        return False

    def on_map_grab_inputs(self, widget, event):
        window = self.get_window()
        if window:
            device_manager = window.get_display().get_device_manager()
            client_pointer = device_manager.get_client_pointer()
            client_pointer.grab(
                window,
                Gdk.GrabOwnership.NONE,
                False,
                Gdk.EventMask.ALL_EVENTS_MASK,
                None,
                Gdk.CURRENT_TIME,
            )

    def on_unlock(self, widget):
        password = self.password_entry.get_text()
        current_user = os.getenv("USER", "admin")

        if pam_authenticate(current_user, password):
            # Restore Super key behavior on unlock
            set_super_key_enabled(True)
            
            for win in self.secondary_windows:
                win.destroy()
            Gtk.main_quit()
        else:
            self.status_label.set_text("[ ACCESS DENIED ]\nTry Again:")
            self.password_entry.set_text("")


if __name__ == "__main__":
    # Disable Super key overlay while locked
    set_super_key_enabled(False)
    
    display = Gdk.Display.get_default()
    n_monitors = display.get_n_monitors()
    
    secondary_windows = []
    
    for i in range(1, n_monitors):
        monitor = display.get_monitor(i)
        win = SecondaryLockWindow(display, monitor)
        win.show_all()
        secondary_windows.append(win)

    main_win = MainLockWindow(secondary_windows)
    main_win.connect("destroy", Gtk.main_quit)
    main_win.show_all()
    
    try:
        Gtk.main()
    finally:
        # Guarantee Super key functionality is restored even if script exits unexpectedly
        set_super_key_enabled(True)
