from kivy.uix.scatter import Scatter
from kivy.uix.button import Button
from kivy.uix.screenmanager import Screen, ScreenManager, NoTransition
from kivy.app import App
from kivy.graphics import Color, Line, Rectangle
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView


class ColorTable:
    background = Color(228 / 255, 245 / 255, 177 / 255)
    buttons = Color(202 / 255, 207 / 255, 149 / 255, 50 / 255)
    lines = Color(132 / 255, 161 / 255, 81 / 255)


def rel_to_abs_path(*pth):
    import os
    sep = os.sep
    return sep.join(__file__.split(sep)[:-2] + list(pth))


def perform(func, *args, **kwargs):
    def this(*_, **__):
        return func(*args, **kwargs)
    return this


favorites = []
DB_PATH = rel_to_abs_path("floralearn", "db.json")
FAVORITES_PATH = rel_to_abs_path("usrdata", "favorites")
current_path = ""
data = {}
poses = {}
quotes = {}
node_offset = (300, 200)
node_size = (200, 150)


def proceed_tree():
    global data, poses
    size = {}

    def get_sizes(subtree, path):
        if subtree.get("__id__") == "end_node":
            size[path] = 1
            quotes[path] = [subtree["name"]]
            return 1
        size[path] = get_sizes(subtree[list(subtree.keys())[0]], path + "0") + \
                     get_sizes(subtree[list(subtree.keys())[1]], path + "1")
        quotes[path] = list(subtree.keys())
        return size[path]

    get_sizes(data, "")

    def get_poses(subtree, path, y_bounds):
        if subtree.get("__id__") == "end_node":
            poses[path] = (len(path) * node_offset[0], y_bounds[0])
            return
        poses[path] = (len(path) * node_offset[0], (y_bounds[0] + y_bounds[1]) // 2)
        get_poses(subtree[list(subtree.keys())[0]], path + "0",
                  (y_bounds[0], y_bounds[1] - size[path + "1"] * (node_offset[1])))
        get_poses(subtree[list(subtree.keys())[1]], path + "1",
                  (y_bounds[0] + size[path + "0"] * (node_offset[1]), y_bounds[1]))

    width = (size[""] - 1) * (node_offset[1])
    get_poses(data, "", (-width // 2, width // 2))


def get_favorites(path=FAVORITES_PATH):
    """Favorite items receiving function. Should be called when 'favorites' button is pressed"""
    with open(path) as fin:
        return fin.read().split("\n")


def save_favorites(path=FAVORITES_PATH):
    """Favorite items memorizing function. Should be called when 'add to favorite' button is pressed"""
    with open(path, mode="wt") as fout:
        fout.write("\n".join(favorites))


def load_db():
    import json
    with open(DB_PATH) as db:
        return json.loads(db.read())


def get_subtree(pth):
    global data
    cur = data
    i = 0
    while i < len(pth):
        cur = cur[list(cur.keys())[int(pth[i])]]
        i += 1
    return cur


class TreeWidget(Scatter):
    def collide_point(self, x, y):
        return True

    def __init__(self, **kwargs):
        super(TreeWidget, self).__init__(do_rotation=False, **kwargs)
        self.clear_widgets()
        with self.canvas:
            # Color(0.5, 0.5, 0.5, 0.5)
            for key, item in poses.items():
                bg_color0 = bg_color1 = ColorTable.buttons.rgba
                if key == current_path[:len(key)] and key != current_path:
                    if current_path[len(key)] == "0":
                        bg_color0 = ColorTable.lines.rgba
                    else:
                        bg_color1 = ColorTable.lines.rgba
                if len(quotes[key]) == 1:
                    if key == current_path:
                        bg_color1 = ColorTable.lines.rgba
                    self.add_widget(Button(pos=item, size=node_size, text=quotes[key][0],
                                           on_press=perform(open_quotes, quote=key),
                                           color=ColorTable.lines.rgba,
                                           background_color=bg_color1,
                                           border=[10] * 4))
                else:
                    self.add_widget(Button(pos=item, size=(node_size[0], node_size[1] // 2),
                                           text=quotes[key][0],
                                           on_press=perform(open_quotes, quote=key),
                                           color=ColorTable.lines.rgba,
                                           background_color=bg_color0,
                                           border=[10] * 4))
                    self.add_widget(Button(pos=(item[0], item[1] + node_size[1] // 2),
                                           size=(node_size[0], node_size[1] // 2),
                                           text=quotes[key][1],
                                           on_press=perform(open_quotes, quote=key),
                                           color=ColorTable.lines.rgba,
                                           background_color=bg_color1,
                                           border=[10] * 4))

                if key != "":
                    p_pos = poses[key[:-1]]
                    Color(*ColorTable.lines.rgba)
                    if key[-1] == "0":
                        Line(points=[p_pos[0] + node_size[0], p_pos[1] + node_size[1] // 4,
                                     item[0], item[1] + node_size[1] // 2])
                    else:
                        Line(points=[p_pos[0] + node_size[0], p_pos[1] + node_size[1] * 3 // 4,
                                     item[0], item[1] + node_size[1] // 2])


class TreeScreen(Screen):
    def on_enter(self, *args):
        self.clear_widgets()
        with self.canvas:
            self.canvas.clear()
            Color(*ColorTable.background.rgba)
            Rectangle(pos=(0, 0), size=(1000, 1000))
        self.add_widget(TreeWidget())


class QuotesScreen(Screen):
    def __init__(self, **kwargs):
        super(QuotesScreen, self).__init__(**kwargs)
        with self.canvas:
            Color(*ColorTable.background.rgba)
            Rectangle(pos=(0, 0), size=(1000, 1000))

    def on_enter(self, *args):
        self.clear_widgets()
        if len(quotes[current_path]) == 1:
            self.add_widget(Label(text=quotes[current_path][0], color=ColorTable.lines.rgba))
        else:
            layout = BoxLayout(orientation="vertical", size=self.size,
                               pos=self.pos, padding=[100])
            layout.add_widget(Button(
                text=quotes[current_path][0],
                color=ColorTable.lines.rgba,
                on_press=perform(open_quotes, quote=current_path + "0"),
                background_color=ColorTable.buttons.rgba,
                border=[10]*4))
            layout.add_widget(Button(
                text=quotes[current_path][1],
                color=ColorTable.lines.rgba,
                on_press=perform(open_quotes, quote=current_path + "1"),
                background_color=ColorTable.buttons.rgba,
                border=[10] * 4))
            self.add_widget(layout)
        layout = BoxLayout(orientation="horizontal", size_hint=(.2, .1), pos=(0, 0))
        layout.add_widget(Button(text="tree", on_press=open_tree,
                                 color=ColorTable.lines.rgba,
                                 background_color=ColorTable.buttons.rgba,
                                 border=[10] * 4))
        layout.add_widget(Button(text="favs", on_press=open_favorites,
                                 color=ColorTable.lines.rgba,
                                 background_color=ColorTable.buttons.rgba,
                                 border=[10] * 4
                                 ))
        layout.add_widget(Button(text="add\nto\nfavs", on_press=self.add_fav,
                                 color=ColorTable.lines.rgba,
                                 background_color=ColorTable.buttons.rgba,
                                 border=[10] * 4
                                 ))
        self.add_widget(layout)

    def add_fav(self, *args):
        global favorites
        favorites.append(current_path)
        save_favorites()


class FavoritesScreen(Screen):
    def on_enter(self, *args):
        with self.canvas:
            Color(*ColorTable.background.rgba)
            Rectangle(pos=(0, 0), size=(1000, 1000))
        self.clear_widgets()
        sv = ScrollView()
        layout = GridLayout(cols=1, size_hint_y=None, height=50 * len(favorites))
        for num, fav in enumerate(favorites):
            bl = BoxLayout(orientation="horizontal")
            bl.add_widget(Button(text=quotes[fav][0], on_press=perform(open_quotes, quote=fav),
                                 color=ColorTable.lines.rgba,
                                 background_color=ColorTable.buttons.rgba,
                                 border=[10] * 4))
            bl.add_widget(Button(size_hint=(.2, 1), text="del", on_press=perform(self.delete_fav, num),
                                 color=ColorTable.lines.rgba,
                                 background_color=ColorTable.buttons.rgba,
                                 border=[10] * 4))
            layout.add_widget(bl)
        sv.add_widget(layout)
        self.add_widget(sv)

    def delete_fav(self, index):
        global favorites
        favorites.pop(index)
        save_favorites()
        self.on_enter()


class ThisScreenManager(ScreenManager):
    def __init__(self, **kwargs):
        super(ThisScreenManager, self).__init__(**kwargs)
        self.tree_screen = TreeScreen(name="tree")
        self.quotes_screen = QuotesScreen(name="quotes")
        self.favorites_screen = FavoritesScreen(name="favorites")
        self.add_widget(self.quotes_screen)
        self.add_widget(self.tree_screen)
        self.add_widget(self.favorites_screen)


screen_manager = None
screen_manager: ThisScreenManager


def open_quotes(*args, quote=None):
    global current_path
    if quote:
        current_path = quote
    screen_manager.switch_to(screen_manager.favorites_screen)
    screen_manager.switch_to(screen_manager.quotes_screen)


def open_tree(*args):
    screen_manager.switch_to(screen_manager.tree_screen)


def open_favorites(*args):
    screen_manager.switch_to(screen_manager.favorites_screen)


class ThisApp(App):
    def build(self):
        global screen_manager
        screen_manager = ThisScreenManager(transition=NoTransition())
        return screen_manager


class Program:
    def __init__(self):
        pass

    def main(self):
        global data
        data = load_db()
        proceed_tree()

        import os
        global favorites
        if not os.path.exists(FAVORITES_PATH):
            with open(FAVORITES_PATH, "w") as fout:
                fout.write("")
        favorites = get_favorites(FAVORITES_PATH)

        ThisApp().run()

        return 0

