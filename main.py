import os
import sys
from pynput import keyboard
import timer
import win32api
import win32con
import win32gui_struct
try:
    import winxpgui as win32gui
except ImportError:
    import win32gui
import tkinter as tk
import itertools, glob
import webbrowser

query = ""
search_type = ""

class SysTrayIcon(object):
    QUIT = 'QUIT'
    SPECIAL_ACTIONS = [QUIT]
    
    FIRST_ID = 1023
    
    def __init__(self,
                 icon,
                 hover_text,
                 menu_options,
                 on_quit=None,
                 default_menu_index=None,
                 window_class_name=None,):
        
        self.icon = icon
        self.hover_text = hover_text
        self.on_quit = on_quit
        
        menu_options = menu_options + (('Quit', self.QUIT),)
        self._next_action_id = self.FIRST_ID
        self.menu_actions_by_id = set()
        self.menu_options = self._add_ids_to_menu_options(list(menu_options))
        self.menu_actions_by_id = dict(self.menu_actions_by_id)
        del self._next_action_id
        
        
        self.default_menu_index = (default_menu_index or 0)
        self.window_class_name = window_class_name or "SysTrayIconPy"
        
        message_map = {win32gui.RegisterWindowMessage("TaskbarCreated"): self.restart,
                       win32con.WM_DESTROY: self.destroy,
                       win32con.WM_COMMAND: self.command,
                       win32con.WM_USER+20 : self.notify,}
                       
        window_class = win32gui.WNDCLASS()
        hinst = window_class.hInstance = win32gui.GetModuleHandle(None)
        window_class.lpszClassName = self.window_class_name
        window_class.style = win32con.CS_VREDRAW | win32con.CS_HREDRAW;
        window_class.hCursor = win32gui.LoadCursor(0, win32con.IDC_ARROW)
        window_class.hbrBackground = win32con.COLOR_WINDOW
        window_class.lpfnWndProc = message_map
        classAtom = win32gui.RegisterClass(window_class)
        style = win32con.WS_OVERLAPPED | win32con.WS_SYSMENU
        self.hwnd = win32gui.CreateWindow(classAtom,
                                          self.window_class_name,
                                          style,
                                          0,
                                          0,
                                          win32con.CW_USEDEFAULT,
                                          win32con.CW_USEDEFAULT,
                                          0,
                                          0,
                                          hinst,
                                          None)
        win32gui.UpdateWindow(self.hwnd)
        self.notify_id = None
        self.refresh_icon()
        
        win32gui.PumpMessages()

    def _add_ids_to_menu_options(self, menu_options):
        result = []
        for menu_option in menu_options:
            option_text, option_action = menu_option
            if callable(option_action) or option_action in self.SPECIAL_ACTIONS:
                self.menu_actions_by_id.add((self._next_action_id, option_action))
                result.append(menu_option + (self._next_action_id,))
            elif non_string_iterable(option_action):
                result.append((option_text,
                               self._add_ids_to_menu_options(option_action),
                               self._next_action_id))
            else:
                print ('Unknown item', option_text, option_action)
            self._next_action_id += 1
        return result
        
    def refresh_icon(self):
        hinst = win32gui.GetModuleHandle(None)
        if os.path.isfile(self.icon):
            icon_flags = win32con.LR_LOADFROMFILE | win32con.LR_DEFAULTSIZE
            hicon = win32gui.LoadImage(hinst,
                                       self.icon,
                                       win32con.IMAGE_ICON,
                                       0,
                                       0,
                                       icon_flags)
        else:
            print ("Can't find icon file - using default.")
            hicon = win32gui.LoadIcon(0, win32con.IDI_APPLICATION)

        if self.notify_id: message = win32gui.NIM_MODIFY
        else: message = win32gui.NIM_ADD
        self.notify_id = (self.hwnd,
                          0,
                          win32gui.NIF_ICON | win32gui.NIF_MESSAGE | win32gui.NIF_TIP,
                          win32con.WM_USER+20,
                          hicon,
                          self.hover_text)
        win32gui.Shell_NotifyIcon(message, self.notify_id)

    def restart(self, hwnd, msg, wparam, lparam):
        self.refresh_icon()

    def destroy(self, hwnd, msg, wparam, lparam):
        if self.on_quit: self.on_quit(self)
        nid = (self.hwnd, 0)
        win32gui.Shell_NotifyIcon(win32gui.NIM_DELETE, nid)
        win32gui.PostQuitMessage(0)

    def notify(self, hwnd, msg, wparam, lparam):
        if lparam == win32con.WM_LBUTTONDBLCLK:
            self.execute_menu_option(self.default_menu_index + self.FIRST_ID)
        elif lparam == win32con.WM_RBUTTONUP:
            self.show_menu()
        elif lparam == win32con.WM_LBUTTONUP:
            pass
        return True

    def show_menu(self):
        menu = win32gui.CreatePopupMenu()
        self.create_menu(menu, self.menu_options)
        
        pos = win32gui.GetCursorPos()
        win32gui.SetForegroundWindow(self.hwnd)
        win32gui.TrackPopupMenu(menu,
                                win32con.TPM_LEFTALIGN,
                                pos[0],
                                pos[1],
                                0,
                                self.hwnd,
                                None)
        win32gui.PostMessage(self.hwnd, win32con.WM_NULL, 0, 0)
    
    def create_menu(self, menu, menu_options):
        for option_text, option_action, option_id in menu_options[::-1]:
            
            if option_id in self.menu_actions_by_id:                
                item, extras = win32gui_struct.PackMENUITEMINFO(text=option_text, wID=option_id)
                win32gui.InsertMenuItem(menu, 0, 1, item)
            else:
                submenu = win32gui.CreatePopupMenu()
                self.create_menu(submenu, option_action)
                item, extras = win32gui_struct.PackMENUITEMINFO(text=option_text, hSubMenu=submenu)
                win32gui.InsertMenuItem(menu, 0, 1, item)

    def command(self, hwnd, msg, wparam, lparam):
        id = win32gui.LOWORD(wparam)
        self.execute_menu_option(id)
        
    def execute_menu_option(self, id):
        menu_action = self.menu_actions_by_id[id]      
        if menu_action == self.QUIT:
            win32gui.DestroyWindow(self.hwnd)
        else:
            menu_action(self)
            
def non_string_iterable(obj):
    try:
        iter(obj)
    except TypeError:
        return False
    else:
        return not isinstance(obj, str)

def search():
    global search_type

    window = tk.Tk()
    window.lift()
    window.wm_attributes("-topmost", 1)
    window.focus_force()
    window.iconbitmap('./favicon.ico')
    ws = window.winfo_screenwidth() # width of the screen
    hs = window.winfo_screenheight() # height of the screen
    window.geometry('%dx%d+%d+%d' % (380, 50, ws - 400, hs - 150))
    window.title(search_type)
    window.resizable(width=False, height=False)
    form_entry = tk.Frame(master = window)
    user_input = tk.Entry(master = form_entry, width = 50)

    def get_input(*args):
        global query
        query = user_input.get()
        window.destroy()

    def close(*args):
        global query 
        query = ""
        window.destroy()

    def on_focus_out(event):
        if event.widget == user_input:
            global query 
            query = ""
            window.destroy()


    user_input.focus_set()
    window.bind('<Return>', get_input)
    window.bind('<Escape>', close)
    window.bind("<FocusOut>", on_focus_out)

    btn_search = tk.Button(master = form_entry,
                           text = "Search",
                           command = get_input)

    user_input.grid(row = 0, column = 0, sticky = "e")
    btn_search.grid(row = 0, column = 1, padx = 10)
    form_entry.grid(row = 0, column = 0, padx = 10, pady = 10)

    window.mainloop()

if __name__ == '__main__':
    icon = "favicon.ico"
    hover_text = "Quick and Simple"
    
    YTCOMBINATION = {keyboard.Key.alt_l, keyboard.KeyCode.from_char('x')}
    GGCOMBINATION = {keyboard.Key.alt_l, keyboard.KeyCode.from_char('z')}
    current = set()

    def youtube_search(SysTrayIcon):
        global query
        global search_type
        current.clear()
        search_type = "Search Youtube"
        search()
        query.replace(" ", "+")
        if query != "":
            webbrowser.open('https://www.youtube.com/results?search_query=' + query, new=0)
        query = ""

    def google_search(sysTrayIcon):
        global query
        global search_type
        current.clear()
        search_type = "Search Google"
        search()
        query.replace(" ", "+")
        if query != "":
            webbrowser.open('https://www.google.com/search?q=' + query, new=0)
        query = ""

    menu_options = (('Search Google', google_search), ('Search Youtube', youtube_search))

    def on_press(key):
        global query
        global search_type

        if key in YTCOMBINATION or key in GGCOMBINATION:
            current.add(key)
            if all(k in current for k in YTCOMBINATION):
                current.clear()
                search_type = "Search Youtube"
                search()
                query.replace(" ", "+")
                if query != "":
                    webbrowser.open('https://www.youtube.com/results?search_query=' + query, new=0)
                query = ""
            elif all(k in current for k in GGCOMBINATION):
                current.clear()
                search_type = "Search Google"
                search()
                query.replace(" ", "+")
                if query != "":
                    webbrowser.open('https://www.google.com/search?q=' + query, new=0)
                query = ""

    def on_release(key):
        try:
            current.remove(key)
        except KeyError:
            pass

    lis = keyboard.Listener(on_press=on_press, on_release=on_release)
    lis.start()

    SysTrayIcon(icon, hover_text, menu_options, on_quit=None, default_menu_index=1)

    sys.exit()
