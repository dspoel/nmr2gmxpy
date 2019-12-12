from progressbar import ProgressBar, ETA, Percentage, Bar, Counter
from datetime import datetime as dt

class TaskMonitor(ProgressBar):

    def __init__(self, *args, **kwargs):
        start_time = "Start: " + dt.now().strftime("%H:%M:%S")
        bar = Bar(left = "[", right = "]", marker = ":", fill = ".")
        counter = Counter("%d/" + str(kwargs["maxval"]))
        kwargs["widgets"] = [start_time, "  ", ETA(), "  ", counter, "  ", \
                Percentage(), "  ", bar]
        ProgressBar.__init__(self, *args, **kwargs)
