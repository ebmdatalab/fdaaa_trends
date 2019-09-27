import numpy as np

def remove_spines(ax, sides):
    """
    Remove spines of axis.
    Parameters:
      ax: axes to operate on
      sides: list of sides: top, left, bottom, right
    Examples:
    removespines(ax, ['top'])
    removespines(ax, ['top', 'bottom', 'right', 'left'])
    """
    for side in sides:
        ax.spines[side].set_visible(False)
    return ax


def move_spines(ax, sides, dists):
    """
    Move the entire spine relative to the figure.
    Parameters:
      ax: axes to operate on
      sides: list of sides to move. Sides: top, left, bottom, right
      dists: list of float distances to move. Should match sides in length.
    Example:
    move_spines(ax, sides=['left', 'bottom'], dists=[-0.02, 0.1])
    """
    for side, dist in zip(sides, dists):
        ax.spines[side].set_position(("axes", dist))
    return ax

def is_latex_enabled():
    """
    Returns True if LaTeX is enabled in matplotlib's rcParams,
    False otherwise
    """
    import matplotlib as mpl

    return mpl.rcParams["text.usetex"]

def remove_ticks(ax, x=False, y=False):
    """
    Remove ticks from axis.
    Parameters:
      ax: axes to work on
      x: if True, remove xticks. Default False.
      y: if True, remove yticks. Default False.
    Examples:
    removeticks(ax, x=True)
    removeticks(ax, x=True, y=True)
    """
    if x:
        ax.xaxis.set_ticks_position("none")
    if y:
        ax.yaxis.set_ticks_position("none")
    return ax

def add_at_risk_counts(x, *fitters, position=-0.15, **kwargs):
    """
    Add counts showing how many individuals were at risk at each time point in
    survival/hazard plots.
    Parameters
    ----------
    fitters:
      One or several fitters, for example KaplanMeierFitter,
      NelsonAalenFitter, etc...
    Returns
    --------
      ax: The axes which was used.
    Examples
    --------
    >>> # First train some fitters and plot them
    >>> fig = plt.figure()
    >>> ax = plt.subplot(111)
    >>>
    >>> f1 = KaplanMeierFitter()
    >>> f1.fit(data)
    >>> f1.plot(ax=ax)
    >>>
    >>> f2 = KaplanMeierFitter()
    >>> f2.fit(data)
    >>> f2.plot(ax=ax)
    >>>
    >>> # There are equivalent
    >>> add_at_risk_counts(f1, f2)
    >>> add_at_risk_counts(f1, f2, ax=ax, fig=fig)
    >>>
    >>> # This overrides the labels
    >>> add_at_risk_counts(f1, f2, labels=['fitter one', 'fitter two'])
    >>>
    >>> # This hides the labels
    >>> add_at_risk_counts(f1, f2, labels=None)
    """
    from matplotlib import pyplot as plt

    # Axes and Figure can't be None
    ax = kwargs.pop("ax", None)
    if ax is None:
        ax = plt.gca()

    fig = kwargs.pop("fig", None)
    if fig is None:
        fig = plt.gcf()

    if "labels" not in kwargs:
        labels = [f._label for f in fitters]
    else:
        # Allow None, in which case no labels should be used
        labels = kwargs.pop("labels", None)
        if labels is None:
            labels = [None] * len(fitters)
    # Create another axes where we can put size ticks
    ax2 = plt.twiny(ax=ax)
    # Move the ticks below existing axes
    # Appropriate length scaled for 6 inches. Adjust for figure size.
    ax2_ypos = position * 6.0 / fig.get_figheight()
    move_spines(ax2, ["bottom"], [ax2_ypos])
    # Hide all fluff
    remove_spines(ax2, ["top", "right", "bottom", "left"])
    # Set ticks and labels on bottom
    ax2.xaxis.tick_bottom()
    # Set limit
    min_time, max_time = ax.get_xlim()
    ax2.set_xlim(min_time, max_time)
    # Set ticks to kwarg or visible ticks
    xticks = kwargs.pop("xticks", None)
    if xticks is None:
        xticks = [xtick for xtick in ax.get_xticks() if min_time <= xtick <= max_time]
    ax2.set_xticks(xticks)
    # Remove ticks, need to do this AFTER moving the ticks
    remove_ticks(ax2, x=True, y=True)
    # Add population size at times
    ticklabels = []
    for tick in ax2.get_xticks():
        lbl = ""
        # Get counts at tick
        counts = [f.durations[f.durations >= tick].shape[0] for f in fitters]
        # Create tick label
        for l, c in zip(labels, counts):
            # First tick is prepended with the label
            if tick == ax2.get_xticks()[0] and l is not None:
                # Get length of largest count
                max_length = len(str(max(counts)))
                if is_latex_enabled():
                    s = "\n{}\\quad".format(l) + "{{:>{}d}}".format(max_length)
                else:
                    s = "\n{}   ".format(l) + "{{:>{}d}}".format(max_length)
            else:
                s = "\n{}"
            lbl += s.format(c)
        ticklabels.append(lbl.strip())
    # Align labels to the right so numbers can be compared easily
    ax2.set_xticklabels(ticklabels, ha="center", **kwargs)

    # Add a descriptive headline.
    ax2.xaxis.set_label_coords(0, ax2_ypos)
    ax2.set_xlabel("At risk", fontsize = x)
    ax2.tick_params(labelsize=x)
    plt.tight_layout()
    return ax