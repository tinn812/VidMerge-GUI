from tkinterdnd2 import DND_FILES, TkinterDnD
from vidmerge_gui import VideoAudioMergerApp

if __name__ == "__main__":
    root = TkinterDnD.Tk()
    app = VideoAudioMergerApp(root)
    root.mainloop()