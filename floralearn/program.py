favorites = []
last_open = ""


def get_favorites(path="usrdata\\favorites"):
    """Favorite items receiving function. Should be called when 'favorites' button is pressed"""
    try:
        with open(path) as fin:
            return fin.read().split("\n")
    except FileNotFoundError:
        pass
    except Exception:
        pass


def add_favorite(item, path="usrdata\\favorites"):
    """Favorite items memorizing function. Should be called when 'add to favorite' button is pressed"""
    try:
        with open(path, mode="a") as fout:
            fout.writelines([item])
    except FileNotFoundError:
        pass
    except Exception:
        pass


def set_last_opened(item, path="usrdata\\lastopen"):
    """Last opened item memorization. Should be called when an item is being opened (slower) / app's exit (faster)"""
    try:
        with open(path, mode="w") as fout:
            fout.write(item)
    except FileNotFoundError:
        pass
    except Exception:
        pass


def get_last_opened(path="usrdata\\lastopen"):
    """Last opened item receiving. Should be called on startup"""
    try:
        with open(path) as fin:
            return fin.read()
    except FileNotFoundError:
        pass
    except Exception:
        pass


class Program:
    def __init__(self):
        pass

    def main(self):
        # load db
        # ...
        # check for files
        import os
        try:
            global favorites, last_open
            if not os.path.exists("usrdata\\favorites"):
                with open("usrdata\\favorites", "w") as fout:
                    fout.write("")
            favorites = get_favorites("usrdata\\favorites")
            if not os.path.exists("usrdata\\lastopen"):
                with open("usrdata\\lastopen", "w") as fout:
                    fout.write("")
            last_open = get_last_opened("usrdata\\lastopen")
        except Exception:
            pass
        # if last_open:
        #     load(last_open)
        # else:
        #     load(root)

        # main loop

        return 0
