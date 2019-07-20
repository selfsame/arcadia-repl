import sublime, sublime_plugin
import re, socket

UDP_IP = "127.0.0.1"
UDP_PORT = 11211
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setblocking(False)
G = {"prompt": 10, "hist": 0, "namespace": " unknown=>", "active": False}
history = []

print("arcadia-repl loaded!")
print("active", G["active"])

def create_repl(window):
    current_view = window.active_view()
    (group, index) = window.get_view_index(current_view)
    repl = window.new_file()
    repl.set_name("*arcadia-repl*")
    repl.settings().set("arcadia_repl", True)
    repl.settings().set("scope_name", "source.arcadia")
    repl.settings().set("word_wrap", True)
    repl.settings().set("line_numbers", False)
    repl.settings().set("gutter", False)
    repl.settings().set("word_wrap", False)
    repl.set_scratch(True)
    repl.set_syntax_file("Packages/arcadia-repl/Clojure.tmLanguage")
    window.set_view_index(repl, group + 1, len(window.views_in_group(group + 1)))
    window.focus_view(current_view)
    send_repl("*ns*", False)
    history = []
    return repl

def get_repl(window):
    for v in window.views():
        if v.name() == "*arcadia-repl*": 
            return v
    for w in sublime.windows():
        for v in w.views():
            if v.name() == "*arcadia-repl*": 
                return v

def view_ns(view):
    namespacedecl = view.find(r"^[^;]*?\(", 0)
    namespacedecl = view.extract_scope(namespacedecl.end()-1)
    pos = namespacedecl.begin() + 3
    while pos < namespacedecl.end():
        namespace = view.find(r"[\}\s][A-Za-z\_!\?\*\+\-][\w!\?\*\+\-:]*(\.[\w!\?\*\+\-:]+)*", pos)
        nsn = view.substr(namespace)[1:]
        return nsn
    return False

def entered_text(view): return view.substr(sublime.Region(G["prompt"], view.size()))

def send_repl(text, manual):
    special = re.search(r'\*[1-9][0-9]*', text)
    if text == "": 
        text = " "
        history.append(text)
        G["hist"] = 0
    elif special:
        n = int(special.group()[1:])
        if (len(history) >= n):
            text = history[len(history) - n]
            G["hist"] = 0
    elif manual:
        history.append(text)
        G["hist"] = 0
    print(text)
    sock.sendto(text.encode('utf-8'), (UDP_IP, UDP_PORT))

def format_input_text(text):
    prompt = re.search(r"\n.+$", text)
    if prompt:
        res = text[:(len(prompt.group()) - 1) * -1]
        G["namespace"] = prompt.group()
        r2 = re.search("[\\n]*$", res)
        if r2:
            res = res[:len(r2.group()) * -1]
        else:
            res = res[-2:]
        res += prompt.group()
    return res

def update(window):
    repl = get_repl(window)
    try:
        data = format_input_text(sock.recvfrom(8192)[0].decode("utf-8"))
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
        G["active"] = True
        window = self.view.window()
        repl = get_repl(window) or create_repl(window)
        window.focus_view(get_repl(window))
        update(window)

class PluginEventListener(sublime_plugin.EventListener):
    def on_query_context(self, view, key, operator, operand, match_all):
        if key == "arcadia_udp":
            return G["active"] or False



class ArcadiaReplEnterUdpCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        if not G["active"]: pass
        send_repl(entered_text(self.view), True)

class ArcadiaReplInsertUdpCommand(sublime_plugin.TextCommand):
    def run(self, edit, data):
        if not G["active"]: pass
        repl = get_repl(self.view.window())
        repl.insert(edit,repl.size(), data)
        place_cursor_at_end(repl)

class ArcadiaReplClearUdpCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        if not G["active"]: pass
        repl = get_repl(self.view.window())
        repl.replace(edit,sublime.Region(0, repl.size()), G["namespace"][1:])
        place_cursor_at_end(repl)

class ArcadiaReplHistoryUdpCommand(sublime_plugin.TextCommand):
    def run(self, edit, i=0):
        if not G["active"]: pass
        repl = get_repl(self.view.window())
        if (len(history) * -1) <= G["hist"] + i < 0:
            G["hist"] += i
            repl.replace(edit,sublime.Region(G["prompt"], repl.size()), history[G["hist"]])

class ArcadiaReplRequireUdpCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        if not G["active"]: pass
        repl = get_repl(self.view.window())
        if self.view == repl: return False
        nsn = view_ns(self.view)
        if nsn:
            send_repl("(do (require '"+nsn+ " :reload) (find-ns '"+nsn+ "))", False)

def format_transfered_text(view, text):
    if view == get_repl(view.window()):
        return text
    nsn = view_ns(view)
    if nsn:
        return "(do (if-not (find-ns '" + nsn + ") (try (require '" + nsn + " :reload) (catch Exception e (ns " + nsn + " )))) (in-ns '" + nsn + ") " + text + ")"
    return text

def transfer_naked(view):
    view.run_command("expand_selection", {"to": "brackets"})
    if view.substr(view.sel()[0]) == "":
        _s = view.sel()[0]
        view.run_command("expand_selection", {"to": "line"})
        send_repl(format_transfered_text(view, view.substr(view.sel()[0])), False)
        view.sel().clear()
        view.sel().add(_s)
        return True
    return False

class ArcadiaReplTransferUdpCommand(sublime_plugin.TextCommand):
    def run(self, edit, scope="block"):
        if not G["active"]: pass
        repl = get_repl(self.view.window())
        regions, sel = [],[]
        for region in self.view.sel(): sel.append(region)
        if scope == "file":
            send_repl("(do " + self.view.substr(sublime.Region(0, self.view.size())) + ")", False)
            return True
        if scope == "selection":
            for s in sel:
                send_repl(format_transfered_text(self.view, self.view.substr(s)), False)
            return True
        if scope == "block": 
            if transfer_naked(self.view): return True
        if scope == "top-form": 
            if transfer_naked(self.view): return True
            #expand until no change, also make sure sel end is not going backwards
            la = self.view.sel()[0].a
            lb = self.view.sel()[0].b
            for i in range(40):
                self.view.run_command("expand_selection", {"to": "brackets"})
                if (self.view.sel()[0].b < lb):
                    self.view.sel().clear()
                    self.view.sel().add(sublime.Region(la, lb))
                    break
                if (self.view.sel()[0].a == la) & (self.view.sel()[0].b == lb):
                    break
                la = self.view.sel()[0].a
                lb = self.view.sel()[0].b
                
            send_repl(format_transfered_text(self.view, self.view.substr(self.view.sel()[0])), False)
            self.view.sel().clear()
            for region in sel: self.view.sel().add(region)
            return True
        for idx in range(len(self.view.sel())):
            if scope == "block":
                regions.append(sublime.Region(self.view.sel()[idx].a - 1, self.view.sel()[idx].b + 1))
        for pair in regions: 
            for text in find_blocks(self.view, pair.a, pair.b):
                send_repl(format_transfered_text(self.view, text), False)
        self.view.sel().clear()
        for region in sel: self.view.sel().add(region)
    
def find_blocks(view, start, end):
    idx, depth = start, 0
    regions, res = [], []
    while idx < end:
        enclosure = view.find(r"\"[^\"]*\"|;[^\n]*\n|\(|\[|\{|\)|\]|\}", idx)
        if not enclosure: 
            break
        if view.substr(enclosure) in ("(", "[", "{", "("):
            if depth == 0: 
                if view.substr(sublime.Region(enclosure.a-1, enclosure.a)) == "'":
                    res.append(enclosure.a-1)
                else: res.append(enclosure.a)
            depth += 1
        elif view.substr(enclosure) in (")", "]", "}"):
            depth -= 1
            if depth == 0: regions.append(view.substr(sublime.Region(res.pop(), enclosure.b)))
        idx = enclosure.end()
    return regions