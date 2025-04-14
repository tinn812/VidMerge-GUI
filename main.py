from tkinterdnd2 import DND_FILES, TkinterDnD
from vidmerge_gui import VideoAudioMergerApp, ThemedDnDApp
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

if __name__ == "__main__":
    root = ThemedDnDApp()
    app = VideoAudioMergerApp(root)
    root.mainloop()

