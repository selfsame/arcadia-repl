import sublime
import socket

UDP_IP = "127.0.0.1"
UDP_PORT = 11211
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setblocking(False)
G = {"prompt": 0, "hist": 0}
history = []

def create_repl(window):
    current_view = window.active_view()
    (group, index) = window.get_view_index(current_view)
    repl = window.new_file()
    repl.set_name("*REPL* (arcadia)")
    repl.settings().set("arcadia_repl", True)
    repl.set_scratch(True)
    repl.set_syntax_file("Packages/Clojure/Clojure.tmLanguage")
    window.set_view_index(repl, group + 1, len(window.views_in_group(group + 1)))
    window.focus_view(current_view)
    repl.run_command("arcadia_repl_clear")
    return repl

def get_repl(window):
    for v in window.views():
        if v.name() == "*REPL* (arcadia)": return v

def entered_text(view): return view.substr(sublime.Region(G["prompt"], view.size()))

def send_repl(text):
    if text == "": 
        text = " "
    elif len(history) == 0 or (G["hist"] == 0 and history[-1] != text):
        history.append(text)
    G["hist"] = 0
    sock.sendto(text.encode('utf-8'), (UDP_IP, UDP_PORT))

def update(window):
    repl = get_repl(window)
    try:
        data = sock.recvfrom(1024)[0].decode("utf-8").replace("=>", ">", 1).replace("\r", "")
        repl.run_command("arcadia_repl_insert", {"data":"\n"+data})
    except: None
    sublime.set_timeout(lambda: update(window), 100)

def place_cursor_at_end(view):
    view.sel().clear()
    view.sel().add(sublime.Region(view.size(),view.size()))
    G["prompt"] = view.size()

class StartArcadiaReplCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        window = self.view.window()
        repl = get_repl(window) or create_repl(window)
        window.focus_view(get_repl(window))
        update(window)

class ArcadiaReplEnterCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        send_repl(entered_text(self.view))

class ArcadiaReplInsertCommand(sublime_plugin.TextCommand):
    def run(self, edit, data):
        repl = get_repl(self.view.window())
        repl.insert(edit,repl.size(), data)
        place_cursor_at_end(repl)

class ArcadiaReplClearCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        repl = get_repl(self.view.window())
        repl.replace(edit,sublime.Region(0, repl.size()), ">")
        place_cursor_at_end(repl)

class ArcadiaReplHistoryCommand(sublime_plugin.TextCommand):
    def run(self, edit, i=0):
        repl = get_repl(self.view.window())
        if (len(history) * -1) <= G["hist"] + i < 0:
            G["hist"] += i
            print(history[G["hist"]])
            repl.replace(edit,sublime.Region(G["prompt"], repl.size()), history[G["hist"]])

class ArcadiaReplTransferCommand(sublime_plugin.TextCommand):
    def run(self, edit, scope="block"):
        repl = get_repl(self.view.window())
        text = ""
        sel = []
        for region in self.view.sel(): sel.append(region)
        if scope == "block": self.view.run_command("expand_selection", {"to": "brackets"})
        for idx in range(len(self.view.sel())):
            if scope == "selection":
                text += self.view.substr(self.view.sel()[idx])
            elif scope == "block":
                text += self.view.substr(sublime.Region(self.view.sel()[idx].a - 1, self.view.sel()[idx].b + 1))
            elif scope == "file":
                text = self.view.substr(sublime.Region(0, self.view.size()))
        self.view.sel().clear()
        for region in sel: self.view.sel().add(region)
        send_repl(text)