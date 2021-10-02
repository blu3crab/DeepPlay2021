import sys

import matplotlib as mpl
mpl.use("TkAgg")

if sys.version_info[0] < 3:
    import Tkinter as tk
else:
    import tkinter as tk

import logging.handlers

from matplotlib.backends import tkagg
from matplotlib.backends.backend_agg import FigureCanvasAgg

import matplotlib.pyplot as plt


logging.basicConfig(
        filename='example.log',
        level=logging.DEBUG,
        format='[%(asctime)s %(levelname)s] (%(threadName)-10s) %(message)s',
    )

window = tk.Tk()


def drawfigureandgetphoto(canvas, figure, loc=(0, 0)):
    figure_canvas_agg = FigureCanvasAgg(figure)
    figure_canvas_agg.draw()
    figure_x, figure_y, figure_w, figure_h = figure.bbox.bounds
    figure_w, figure_h = int(figure_w), int(figure_h)
    photo = tk.PhotoImage(master=canvas, width=figure_w, height=figure_h)
    # Position: convert from top-left anchor to center anchor
    canvas.create_image(loc[0] + figure_w/2, loc[1] + figure_h/2, image=photo)
    tkagg.blit(photo, figure_canvas_agg.get_renderer()._renderer, colormode=2)
    return photo

def createcanvas(w,h):
    window.title("A figure in a canvas")
    canvas = tk.Canvas(window, width=w, height=h)
    canvas.pack()
    return canvas

if __name__ == '__main__':
    # Create a canvas with width 500 and height 500
    canvas = createcanvas(500, 500)

    # Create the figures with width 1500 and height 200
    fig1 = plt.figure(figsize=(1.5, 2))
    fig2 = plt.figure(figsize=(1.5, 2))

    # start from X 15% of figure width, and Y 15% of figure height, height is 75% of figure and width is 75% of figure
    ax1 = fig1.add_axes([.15, .15, .75, .75])
    X = [1, 2, 3, 4, 5, 6, ]
    Y = [2, 4, 6, 4, 10, 8]
    ax1.set_title("my first chart", color='k')
    ax1.plot(X, Y, linewidth=1)

    # start from X 15% of figure width, and Y 15% of figure height, height is 75% of figure and width is 75% of figure
    ax2 = fig2.add_axes([.15, .15, .75, .75])
    X2 = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
    Y2 = [2, 1, 6, 4, 8, 10, 15, 12, 3, 4, 8, 9, 1, 2, 3, 4, 5, 6, 7, 3]
    ax2.set_title("my second chart", color='k')
    ax2.plot(X2, Y2, linewidth=1)

    # put figure 1 at x50,y100 and figure 2 at x250,y 100 of canvas
    photo1 = drawfigureandgetphoto(canvas, fig1, loc=(50, 100))
    photo2 = drawfigureandgetphoto(canvas, fig2, loc=(250, 100))

    # create sample text at x 200 and y 50 of canvas
    canvas.create_text(200, 50, text="Zero-crossing", anchor="s")

    window.mainloop()
