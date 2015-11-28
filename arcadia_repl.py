import sublime, sublime_plugin
import re, socket

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
    repl.settings().set("scope_name", "source.repl")
    repl.set_scratch(True)
    repl.set_syntax_file("Packages/arcadia-repl/Clojure.tmLanguage")
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

def format_input_text(text):
    print(text)
    res = text.replace("=>", "►", 1).replace("\r", "")
    error = re.findall(r"(\w[^:\W\n]+): ([^\n]+)\n", res)
    if len(error) > 0:
        _ns = re.split("\n", res)[-1]
        res = "".join(re.split("\n", res)[1:-1]).replace("  at ", "\n").replace(" in ", "\n  ").replace(" (", "\n  (")
        res = ":" + str(error[0][0]) + "\n\""+error[0][1] + "\"" + res +"\n"+_ns
    return res 

def update(window):
    repl = get_repl(window)
    try:
        data = format_input_text(sock.recvfrom(1024)[0].decode("utf-8"))
        repl.run_command("arcadia_repl_insert", {"data":"\n"+data})
    except: None
    sublime.set_timeout(lambda: update(window), 100)

def place_cursor_at_end(view):
    view.sel().clear()
    end_region = sublime.Region(view.size(),view.size())
    view.sel().add(end_region)
    G["prompt"] = view.size()
    view.show(end_region)

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

def format_transfered_text(view, text):
    namespacedecl = view.find(r"^[^;]*?\(", 0)
    if namespacedecl and view.scope_name(namespacedecl.end()-1).startswith("source.clojure meta.function.namespace.clojure"):
        namespacedecl = view.extract_scope(namespacedecl.end()-1)
        pos = namespacedecl.begin() + 3
        while pos < namespacedecl.end():
            namespace = view.find(r"[\}\s][A-Za-z\_!\?\*\+\-][\w!\?\*\+\-:]*(\.[\w!\?\*\+\-:]+)*", pos)
            if not namespace:
                break
            elif view.scope_name(namespace.begin() + 1).startswith("source.clojure meta.function.namespace.clojure entity.name.namespace.clojure"):
                text = "(do (in-ns '" + view.substr(namespace)[1:] + ")" + text + ")"
                break
            else:
                pos = namespace.end()
    return text

class ArcadiaReplTransferCommand(sublime_plugin.TextCommand):
    def run(self, edit, scope="block"):
        repl = get_repl(self.view.window())
        regions, sel = [],[]
        for region in self.view.sel(): sel.append(region)
        if scope == "block": self.view.run_command("expand_selection", {"to": "brackets"})
        for idx in range(len(self.view.sel())):
            if scope == "selection":
                s = self.view.sel()[idx]
                regions.append(sublime.Region(s.begin(), s.end()))
            elif scope == "block":
                regions.append(sublime.Region(self.view.sel()[idx].a - 1, self.view.sel()[idx].b + 1))
            elif scope == "file":
                regions = [sublime.Region(0, self.view.size())]
        for pair in regions: 
            print(pair)
            for text in find_blocks(self.view, pair.a, pair.b):
                print(text)
                send_repl(format_transfered_text(self.view, text))
        self.view.sel().clear()
        for region in sel: self.view.sel().add(region)
    
def find_blocks(view, start, end):
    idx, depth = start, 0
    regions, res = [], []
    while idx < end:
        enclosure = view.find(r"\"[^\"]*\"|;[^\n]*\n|\(|\[|\{|\)|\]|\}", idx)
        if not enclosure: break
        if view.substr(enclosure) in ("(", "[", "{"):
            if depth == 0: res.append(enclosure.a)
            depth += 1
        elif view.substr(enclosure) in (")", "]", "}"):
            depth -= 1
            if depth == 0: regions.append(view.substr(sublime.Region(res.pop(), enclosure.b)))
        idx = enclosure.end()
    return regions
