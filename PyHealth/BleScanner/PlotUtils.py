###############################################################################
#   BleHealthScanner.PlotUtils
#
#       plot pie chart
#           def plotPie(filename, title,
#               percent_duration, alert_discontinuity_counter, slices_label):
#       plot stacked bar chart & save as filename
#           def plotStackedBar(filename, title,
#               ble_percent_duration, app_percent_duration, tx_percent_duration,
#               alert_discontinuity_counter, series_labels):
#       stacked bar chart utility function
#           def stacked_bar(data, series_labels, color_labels, category_labels=None,
#                 show_values=False, value_format="{}", y_label=None,
#                 grid=True, reverse=False):
#
#   Created by MatthewTucker on 16MAY19.
###############################################################################

import matplotlib.pyplot as plt
import numpy as np

import Settings

###############################################################################
# plot pie chart
def plotPie(filename, title, percent_duration, alert_discontinuity_counter, slices_label):

    # set percentages for slices, labels & colors
    slices_percent = [percent_duration[Settings.ALERT_INDEX_GREEN],
                      percent_duration[Settings.ALERT_INDEX_YELLOW],
                      percent_duration[Settings.ALERT_INDEX_RED],
                      percent_duration[Settings.ALERT_INDEX_GRAY]]
    # inactive_label = 'inactive(' + str(alert_discontinuity_counter) + ')'
    # slices_label = ['ideal', 'degraded', 'unavailable', inactive_label]
    colors = ['g', 'y', 'r', 'tab:gray']
    plt.pie(slices_percent, labels=slices_label, colors=colors, startangle=90, autopct='%.0f%%')
    plt.title(title)
    if filename != "": plt.savefig(filename)
    plt.show()

###############################################################################
# plot stacked bar chart
def plotStackedBar(filename, title, ble_percent_duration, app_percent_duration, tx_percent_duration, alert_discontinuity_counter, series_labels):
    plt.figure(figsize=(6, 4))

    color_labels = ['g', 'y', 'r', 'tab:gray']

    # data = [
    #     [0.2, 0.3, 0.35, 0.3], # highest
    #     [0.8, 0.7, 0.6, 0.5]  # lowest
    # ]
    # data = [
    #     [percent_duration[ALERT_INDEX_GRAY], percent_duration[ALERT_INDEX_GRAY], percent_duration[ALERT_INDEX_GRAY],percent_duration[ALERT_INDEX_GRAY]],
    #     [percent_duration[ALERT_INDEX_RED], percent_duration[ALERT_INDEX_RED], percent_duration[ALERT_INDEX_RED],percent_duration[ALERT_INDEX_RED]],
    #     [percent_duration[ALERT_INDEX_YELLOW], percent_duration[ALERT_INDEX_YELLOW], percent_duration[ALERT_INDEX_YELLOW],percent_duration[ALERT_INDEX_YELLOW]],
    #     [percent_duration[ALERT_INDEX_GREEN], percent_duration[ALERT_INDEX_GREEN], percent_duration[ALERT_INDEX_GREEN],percent_duration[ALERT_INDEX_GREEN]]
    # ]
    data = [
        [ble_percent_duration[Settings.ALERT_INDEX_GREEN], app_percent_duration[Settings.ALERT_INDEX_GREEN], tx_percent_duration[Settings.ALERT_INDEX_GREEN], 0],
        [ble_percent_duration[Settings.ALERT_INDEX_YELLOW], app_percent_duration[Settings.ALERT_INDEX_YELLOW], tx_percent_duration[Settings.ALERT_INDEX_YELLOW], 0],
        [ble_percent_duration[Settings.ALERT_INDEX_RED], app_percent_duration[Settings.ALERT_INDEX_RED], tx_percent_duration[Settings.ALERT_INDEX_RED], 0],
        [ble_percent_duration[Settings.ALERT_INDEX_GRAY], app_percent_duration[Settings.ALERT_INDEX_GRAY], tx_percent_duration[Settings.ALERT_INDEX_GRAY], 0]
    ]

#    category_labels = ['Cat A', 'Cat B', 'Cat C', 'Cat D']
    category_labels = ['BLE Heath', 'App Health', 'TX Health', "other"]

    stacked_bar(
        data,
        series_labels,
        color_labels,
        category_labels=category_labels,
        show_values=True,
        value_format="{:.0f}",
        y_label="Duration %"
    )
    # value_format = "{:.0f}",
    #value_format = "%.0f%%",
    # '%.0f%%'
    plt.title(title)
    # plt.savefig('bar.png')
    if filename != "": plt.savefig(filename)
    plt.show()
    return

###############################################################################
# stacked bar chart utility function
def stacked_bar(data, series_labels, color_labels, category_labels=None,
                show_values=False, value_format="{}", y_label=None,
                grid=True, reverse=False):
    """Plots a stacked bar chart with the data and labels provided.

    Keyword arguments:
    data            -- 2-dimensional numpy array or nested list
                       containing data for each series in rows
    series_labels   -- list of series labels (these appear in
                       the legend)
    color_labels   -- list of color for series labels (these map from data to
                       the legend)
    category_labels -- list of category labels (these appear
                       on the x-axis)
    show_values     -- If True then numeric value labels will
                       be shown on each bar
    value_format    -- Format string for numeric value labels
                       (default is "{}")
    y_label         -- Label for y-axis (str)
    grid            -- If True display grid
    reverse         -- If True reverse the order that the
                       series are displayed (left-to-right
                       or right-to-left)
    """

    ny = len(data[0])
    ind = list(range(ny))

    axes = []
    cum_size = np.zeros(ny)

    data = np.array(data)

    if reverse:
        data = np.flip(data, axis=1)
        category_labels = reversed(category_labels)

    for i, row_data in enumerate(data):
        axes.append(plt.bar(ind, row_data, bottom=cum_size,
                            label=series_labels[i], color=color_labels[i]))
        cum_size += row_data

    if category_labels:
        plt.xticks(ind, category_labels)

    if y_label:
        plt.ylabel(y_label)

    plt.legend()

    if grid:
        plt.grid()

    if show_values:
        for axis in axes:
            for bar in axis:
                w, h = bar.get_width(), bar.get_height()
                plt.text(bar.get_x() + w/2, bar.get_y() + h/2,
                         value_format.format(h), ha="center",
                         va="center")
###############################################################################
# plot stacked bar chart
def plotDummyStackedBar(title, percent_duration, alert_discontinuity_counter, series_labels):
    plt.figure(figsize=(6, 4))

    # timeLabel = startDate.ctime() + " to " + endDate.ctime()
    # title = 'BLE Health TX ' + txName + '\n' + timeLabel
    # # series_labels = ['Series 1', 'Series 2']
    # inactive_label = 'inactive(' + str(alert_discontinuity_counter) + ')'
    # # series_labels = [inactive_label, 'unavailable', 'degraded', 'ideal']
    # series_labels = ['ideal', 'degraded', 'unavailable', inactive_label]
    # color_labels = ['tab:gray', 'r', 'y', 'g']
    color_labels = ['g', 'y', 'r', 'tab:gray']

    # data = [
    #     [0.2, 0.3, 0.35, 0.3],
    #     [0.8, 0.7, 0.6, 0.5]
    # ]
    # data = [
    #     [percent_duration[ALERT_INDEX_GRAY], percent_duration[ALERT_INDEX_GRAY], percent_duration[ALERT_INDEX_GRAY],percent_duration[ALERT_INDEX_GRAY]],
    #     [percent_duration[ALERT_INDEX_RED], percent_duration[ALERT_INDEX_RED], percent_duration[ALERT_INDEX_RED],percent_duration[ALERT_INDEX_RED]],
    #     [percent_duration[ALERT_INDEX_YELLOW], percent_duration[ALERT_INDEX_YELLOW], percent_duration[ALERT_INDEX_YELLOW],percent_duration[ALERT_INDEX_YELLOW]],
    #     [percent_duration[ALERT_INDEX_GREEN], percent_duration[ALERT_INDEX_GREEN], percent_duration[ALERT_INDEX_GREEN],percent_duration[ALERT_INDEX_GREEN]]
    # ]
    data = [
        [percent_duration[Settings.ALERT_INDEX_GREEN], percent_duration[Settings.ALERT_INDEX_GREEN], percent_duration[Settings.ALERT_INDEX_GREEN],percent_duration[Settings.ALERT_INDEX_GREEN]],
        [percent_duration[Settings.ALERT_INDEX_YELLOW], percent_duration[Settings.ALERT_INDEX_YELLOW], percent_duration[Settings.ALERT_INDEX_YELLOW],percent_duration[Settings.ALERT_INDEX_YELLOW]],
        [percent_duration[Settings.ALERT_INDEX_RED], percent_duration[Settings.ALERT_INDEX_RED], percent_duration[Settings.ALERT_INDEX_RED],percent_duration[Settings.ALERT_INDEX_RED]],
        [percent_duration[Settings.ALERT_INDEX_GRAY], percent_duration[Settings.ALERT_INDEX_GRAY], percent_duration[Settings.ALERT_INDEX_GRAY],percent_duration[Settings.ALERT_INDEX_GRAY]]
    ]

#    category_labels = ['Cat A', 'Cat B', 'Cat C', 'Cat D']
    category_labels = ['Today', 'Yesterday', 'Last Week', 'Last Month']

    stacked_bar(
        data,
        series_labels,
        color_labels,
        category_labels=category_labels,
        show_values=True,
        value_format="{:.0f}",
        y_label="Duration %"
    )
    # value_format = "{:.0f}",
    #value_format = "%.0f%%",
    # '%.0f%%'
    plt.title(title)
    plt.savefig('bar.png')
    plt.show()
    return
###############################################################################
