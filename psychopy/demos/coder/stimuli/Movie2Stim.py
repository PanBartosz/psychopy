"""
Demo using the experimental MovieStim2 to play a video file. Path of video
needs to updated to point to a video you have. MovieStim2 does /not/ require
avbin to be installed. But...

Movie2 does require:
~~~~~~~~~~~~~~~~~~~~~

1. Python OpenCV package (so openCV libs and the cv2 python interface).
    *. For Windows, a binary installer is available at http://www.lfd.uci.edu/~gohlke/pythonlibs/#opencv
    *. For Linux, it is available via whatever package manager you use.
    *. For OSX, ..... ?
2. VLC application. Just install the standard VLC (32bit) for your OS. http://www.videolan.org/vlc/index.html
"""

from psychopy import visual, core, event
import time

videopath=r'D:\Dropbox\WinPython-32bit-2.7.6.0\my-code\pycvlcmovie\Epic.mp4'

win = visual.Window([1024, 768])

# Create your movie stim.
mov = visual.MovieStim2(win, videopath,
                       size=1024,
                       # pos specifies the /center/ of the movie stim location
                       pos=[0, 100],
                       flipVert=False,
                       flipHoriz=False,
                       loop=False)

keystext = "PRESS 'q' or 'escape' to Quit.\n"
keystext += "#     's': Stop/restart Movie.\n"
keystext += "#     'p': Pause/Unpause Movie.\n"
keystext += "#     '>': Seek Forward 1 Second.\n"
keystext += "#     '<': Seek Backward 1 Second.\n"
keystext += "#     '-': Decrease Movie Volume.\n"
keystext += "#     '+': Increase Movie Volume."
text = visual.TextBox(win,keystext, font_name=None, bold=False, italic=False,
                      font_size=21, font_color=[-1, -1, -1, 1],
                      textgrid_shape=(36, 7), pos=(0, -350), units = 'pix',
                      grid_vert_justification='center',
                      grid_horz_justification='left', align_horz='center',
                      align_vert='bottom',
                      autoLog=False, interpolate=True)

# Start the movie stim by preparing it to play and then calling flip()
shouldflip = mov.play()
while mov.status != visual.FINISHED:
    # if only a movie stim is being shown on the window, only flip when a new
    # frame should be displayed. On a 60 Hz monitor playing a 30 Hz video, this
    # cuts CPU usage of the psychopy app. by almost 50%.
    if shouldflip:
        text.draw()
        win.flip()
    else:
        time.sleep(0.001)
    shouldflip = mov.draw()

    for key in event.getKeys():
        if key in ['escape', 'q']:
            win.close()
            core.quit()
        elif key in ['s',]:
            if mov.status in [visual.PLAYING, visual.PAUSED]:
                # Stop playing the movie stim. This also unloads the current
                # movie resources, freeing the memory used. If you want to
                # play a movie again with the current mov instance, call
                # the three methods as shown in the following else statement.
                mov.stop()
                win.flip()
                text.draw()
                win.flip()
            else:
                # If the mov has been stopped; to start it again, you must
                # load the movie file, call play.
                mov.loadMovie(videopath)
                shouldflip = mov.play()
        elif key in ['p',]:
            # If you want to pause the movie while it is playing, and then want
            # to later resume playing from where the mov was paused, do this..
            if mov.status == visual.PLAYING:
                mov.pause()
            elif mov.status == visual.PAUSED:
                mov.play()
                text.draw()
                win.flip()
        elif key == 'period':
            # skip ahead 1 second in movie.
            ntime = min(mov.getCurrentFrameTime()+1.0, mov.duration)
            mov.seek(ntime)
        elif key == 'comma':
            # skip back 1 second in movie.
            ntime = max(mov.getCurrentFrameTime()-1.0,0.0)
            mov.seek(ntime)
        elif key == 'minus':
            # decrease movie sound a bit
            cv = max(mov.getVolume()-5, 0)
            mov.setVolume(cv)
        elif key == 'equal':
            # increase movie sound a bit
            cv = mov.getVolume()
            cv = min(mov.getVolume()+5, 100)
            mov.setVolume(cv)

core.quit()