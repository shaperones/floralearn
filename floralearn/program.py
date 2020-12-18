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
    """Defines colors for UI. Green."""
    background = Color(228 / 255, 245 / 255, 177 / 255)
    buttons = Color(202 / 255, 207 / 255, 149 / 255, 50 / 255)
    lines = Color(132 / 255, 161 / 255, 81 / 255)


def rel_to_abs_path(*pth):
    """helper function. Transforms relative file path to absolute depending on your operation system"""
    import os
    sep = os.sep
    return sep.join(__file__.split(sep)[:-2] + list(pth))


def perform(func, *args, **kwargs):
    """Allows you to tie arguments to given function. They will be passed when function will be called.
    Example:
        def foo(a, b, mul=2):
            return a + b * mul

        performed_foo = perform(foo, 2, 3, mul=2)
        print(performed_foo(3, 4, 5))  # new given args are ignored completely
        # output: 8
    """
    def this(*_, **__):
        return func(*args, **kwargs)
    return this


favorites = []      # self-explanatory.     stores your favorite nodes
DB_PATH = rel_to_abs_path("floralearn", "db.json")
FAVORITES_PATH = rel_to_abs_path("usrdata", "favorites")        # relative paths to database and user data
current_path = ""   # current path in tree. Consists only '0' and '1', explaining your way to current node
# how_to_decode: move from left to right in current_path, start from root node in a tree. If current symbol in
# current path is '0' => you need to go upper in a tree, else down.
data = {}           # tree itself. each node have following form:
#   {
#       "теза": {
#           # subtree for thesis
#           ...
#       },
#       "антитеза": {
#           # subtree for antithesis
#           ...
#       }
#   }

poses = {}          # one-level dictionary (no nesting) path-to-place
# where each node should be displayed in tree_displaying_screen
quotes = {}         # one-level dict path-to-quotes where if item is a list with 2 strings => this node is not end
# and have thesis (first) and antithesis (second). else it's an end_node and have only name of such Family
node_offset = (800, 400)        # ui setting in constant.
# TODO maybe it is better to place it somewhere else in the future, not in code
node_size = (600, 300)          # ui setting in constant


def proceed_tree():
    """function for giving each node of tree it's placement in tree_displaying_screen"""
    global data, poses
    size = {}       # this dict will contain sizes of each subtree (size is amount of end_nodes)
    # next it will help us to place all the nodes so they do not overlap

    def get_sizes(subtree, path):
        """Recursive DFS-search in tree, filling out the 'size' dictionary. After DFS scanned all children
        of a node it will say that size of this node = size of 1st children + size of 2nd children.
        Also this DFS filling out the 'quotes' dictionary, telling about each node what theses is it contain"""
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
        """Recursive DFS-search in tree, filling out the 'poses' dictionary. Positioning is working in the following way
        1) All the end-nodes shall all have the same distance between their centers' Y.
        2) All node's subtree's should not have children between each other (in projection on OY)
        So they do not overlap anyhow"""
        if subtree.get("__id__") == "end_node":
            poses[path] = (len(path) * node_offset[0], y_bounds[0])
            return
        poses[path] = (len(path) * node_offset[0], (y_bounds[0] + y_bounds[1]) // 2)
        # node is placed in center of it's tree
        get_poses(subtree[list(subtree.keys())[0]], path + "0",
                  (y_bounds[0], y_bounds[1] - size[path + "1"] * (node_offset[1])))
        get_poses(subtree[list(subtree.keys())[1]], path + "1",
                  (y_bounds[0] + size[path + "0"] * (node_offset[1]), y_bounds[1]))

    width = (size[""] - 1) * (node_offset[1])   # max distance between two end-node's center's Y
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
    """Loads database from local storage to memory"""
    import json
    with open(DB_PATH) as db:
        return json.loads(db.read())


class TreeWidget(Scatter):
    """Widget used to draw a tree. It uses the dict 'poses' where we determined where each node
    should be drawn so they do not overlap. Each node is a button where is displayed respective
    thesis and antithesis. Whole tree can be moved and zoomed in or out like the 'Scatter' widget"""
    def collide_point(self, x, y):
        """Pro-gamer move so moving widget never move it's touch-colliding bound-box.
        (it do not ties bounds to position - it makes every point you touch to be a part
        of a bound-box)"""
        return True

    def __init__(self, **kwargs):
        """Draws tree nodes and connect them with lines"""
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
                                           on_release=perform(open_quotes, quote=key),
                                           text_size=(500, 200),
                                           halign='center',
                                           valign='center',
                                           color=ColorTable.lines.rgba,
                                           background_color=bg_color1,
                                           border=[10] * 4))
                else:
                    self.add_widget(Button(pos=item, size=(node_size[0], node_size[1] // 2),
                                           text=quotes[key][0],
                                           text_size=(500, 100),
                                           halign='center',
                                           valign='center',
                                           on_release=perform(open_quotes, quote=key),
                                           color=ColorTable.lines.rgba,
                                           background_color=bg_color0,
                                           border=[10] * 4))
                    self.add_widget(Button(pos=(item[0], item[1] + node_size[1] // 2),
                                           size=(node_size[0], node_size[1] // 2),
                                           text=quotes[key][1],
                                           text_size=(500, 100),
                                           halign='center',
                                           valign='center',
                                           on_release=perform(open_quotes, quote=key),
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
    """Screen containing the TreeWidget."""
    def on_enter(self, *args):
        self.clear_widgets()
        with self.canvas:
            self.canvas.clear()
            Color(*ColorTable.background.rgba)
            Rectangle(pos=(0, 0), size=(1000, 1000))
        self.add_widget(TreeWidget())


class QuotesScreen(Screen):
    """Screen containing quotes of the current node. Also acts as a main screen"""
    def __init__(self, **kwargs):
        super(QuotesScreen, self).__init__(**kwargs)
        with self.canvas:
            Color(*ColorTable.background.rgba)
            Rectangle(pos=(0, 0), size=(1000, 1000))

    def on_enter(self, *args):
        """Draws to big buttons (thesis and antithesis) and some smaller buttons to
        move you to TreeScreen, FavoritesScreen and add current node to favorites"""
        self.clear_widgets()
        if len(quotes[current_path]) == 1:
            self.add_widget(Label(text=quotes[current_path][0], color=ColorTable.lines.rgba))
        else:
            layout = BoxLayout(orientation="vertical", size=self.size,
                               pos=self.pos, padding=[100])
            layout.add_widget(Button(
                text=quotes[current_path][0],
                text_size=(600, 400),
                halign='center',
                valign='center',
                color=ColorTable.lines.rgba,
                on_release=perform(open_quotes, quote=current_path + "0"),
                background_color=ColorTable.buttons.rgba,
                border=[10]*4))
            layout.add_widget(Button(
                text=quotes[current_path][1],
                text_size=(600, 400),
                halign='center',
                valign='center',
                color=ColorTable.lines.rgba,
                on_release=perform(open_quotes, quote=current_path + "1"),
                background_color=ColorTable.buttons.rgba,
                border=[10] * 4))
            self.add_widget(layout)
        layout = BoxLayout(orientation="horizontal", size_hint=(.2, .1), pos=(0, 0))
        layout.add_widget(Button(text="tree", on_release=open_tree,
                                 color=ColorTable.lines.rgba,
                                 background_color=ColorTable.buttons.rgba,
                                 border=[10] * 4))
        layout.add_widget(Button(text="F", on_release=open_favorites,
                                 color=ColorTable.lines.rgba,
                                 background_color=ColorTable.buttons.rgba,
                                 border=[10] * 4
                                 ))
        layout.add_widget(Button(text="+F", on_release=self.add_fav,
                                 color=ColorTable.lines.rgba,
                                 background_color=ColorTable.buttons.rgba,
                                 border=[10] * 4
                                 ))
        self.add_widget(layout)

    def add_fav(self, *args):
        """Adds current node to favorites at the end"""
        global favorites
        favorites.append(current_path)
        save_favorites()


class FavoritesScreen(Screen):
    """Screen to display list of favorite nodes. Each node can be deleted with a button at right"""
    def on_enter(self, *args):
        with self.canvas:
            Color(*ColorTable.background.rgba)
            Rectangle(pos=(0, 0), size=(1000, 1000))
        self.clear_widgets()
        sv = ScrollView()
        layout = GridLayout(cols=1, size_hint_y=None, height=50 * len(favorites))
        for num, fav in enumerate(favorites):
            bl = BoxLayout(orientation="horizontal")
            bl.add_widget(Button(text=quotes[fav][0], on_release=perform(open_quotes, quote=fav),
                                 text_size=(800, 50),
                                 halign='center',
                                 valign='center',
                                 color=ColorTable.lines.rgba,
                                 background_color=ColorTable.buttons.rgba,
                                 border=[10] * 4))
            bl.add_widget(Button(size_hint=(.2, 1), text="del", on_release=perform(self.delete_fav, num),
                                 color=ColorTable.lines.rgba,
                                 background_color=ColorTable.buttons.rgba,
                                 border=[10] * 4))
            layout.add_widget(bl)
        sv.add_widget(layout)
        self.add_widget(sv)

    def delete_fav(self, index):
        """Deletes favorite by it's index"""
        global favorites
        favorites.pop(index)
        save_favorites()
        self.on_enter()


class ThisScreenManager(ScreenManager):
    """Main Screen Manager. Used to switch between screens from any point of the code"""
    def __init__(self, **kwargs):
        super(ThisScreenManager, self).__init__(**kwargs)
        self.tree_screen = TreeScreen(name="tree")
        self.quotes_screen = QuotesScreen(name="quotes")
        self.favorites_screen = FavoritesScreen(name="favorites")
        self.add_widget(self.quotes_screen)
        self.add_widget(self.tree_screen)
        self.add_widget(self.favorites_screen)


screen_manager = None       # screen_manager is declared in global scope so it can be used from anywhere
screen_manager: ThisScreenManager


def open_quotes(*args, quote=None):
    """Open QuotesScreen and changes current quote if such passed"""
    global current_path
    if quote is not None:
        current_path = quote
    if screen_manager.current == "quotes":
        screen_manager.switch_to(screen_manager.favorites_screen)
    # this shenanigan is used because screen manager do not reload screens if you jumped from the
    # same screen
    screen_manager.switch_to(screen_manager.quotes_screen)


def open_tree(*args):
    """Open TreeScreen"""
    screen_manager.switch_to(screen_manager.tree_screen)


def open_favorites(*args):
    """Open FavoritesScreen"""
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

        # check for 'favorites' file if exists ... if not - create one
        import os
        global favorites
        if not os.path.exists(FAVORITES_PATH):
            with open(FAVORITES_PATH, "w") as fout:
                fout.write("")
        favorites = get_favorites(FAVORITES_PATH)

        ThisApp().run()

        return 0
