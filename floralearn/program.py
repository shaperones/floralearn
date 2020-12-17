def rel_to_abs_path(*pth):
    import os
    sep = os.sep
    return sep.join(__file__.split(sep)[:-2] + list(pth))


favorites = []
last_open = ""
DB_PATH = rel_to_abs_path("floralearn", "db.json")
FAVORITES_PATH = rel_to_abs_path("usrdata", "favorites")
LASTOPEN_PATH = rel_to_abs_path("usrdata", "lastopen")
data = {}


def get_favorites(path=FAVORITES_PATH):
    """Favorite items receiving function. Should be called when 'favorites' button is pressed"""
    with open(path) as fin:
        return fin.read().split("\n")


def add_favorite(item, path=FAVORITES_PATH):
    """Favorite items memorizing function. Should be called when 'add to favorite' button is pressed"""
    with open(path, mode="a") as fout:
        fout.writelines([item])


def set_last_opened(item, path=LASTOPEN_PATH):
    """Last opened item memorization. Should be called when an item is being opened (slower) / app's exit (faster)"""
    with open(path, mode="w") as fout:
        fout.write(item)


def get_last_opened(path=LASTOPEN_PATH):
    """Last opened item receiving. Should be called on startup"""
    with open(path) as fin:
        return fin.read()


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


class Program:
    def __init__(self):
        pass

    def main(self):
        global data
        data = load_db()

        import os
        global favorites, last_open
        if not os.path.exists(FAVORITES_PATH):
            with open(FAVORITES_PATH, "w") as fout:
                fout.write("")
        favorites = get_favorites(FAVORITES_PATH)
        if not os.path.exists(LASTOPEN_PATH):
            with open(LASTOPEN_PATH, "w") as fout:
                fout.write("")
        last_open = get_last_opened(LASTOPEN_PATH)
        # if last_open:
        #     load(last_open)
        # else:
        #     load(root)

        # main loop

        return 0

