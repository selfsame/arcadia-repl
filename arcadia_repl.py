import json
import os.path
import re
import sublime
import sublime_plugin


instance = []

class ReplView():
    def __init__(self, view):
        self.view = view

class ArcadiaRepl(sublime_plugin.EventListener):

    def on_load(self, view):
        print("ArcadiaRepl on_load")

    def _resolve_window(self, view):
        window = view.window()

        if window:
            return window

        return sublime.active_window()

class StartArcadiaReplCommand(sublime_plugin.TextCommand):

    def __init__(self, view):
        super().__init__(view)
        self.window = view.window()

    def run(self, edit):
        if len(instance) > 0:
            print(instance[0].view)
            return None
        else:
            (group, index) = self.window.get_view_index(self.view)
            repl_window = self.window.new_file()
            repl_window.set_name("*REPL* (arcadia)")
            self.window.set_view_index(repl_window, group + 1, len(self.window.views_in_group(group + 1)))
            self.window.focus_view(self.view)
            instance.append(ReplView(repl_window))
            print(instance[0].view)
            view.window().run_command("repl_open",{"encoding":"utf8","type": "subprocess","cmd":["ping", "8.8.8.8"]})
            return None