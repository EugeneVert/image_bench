import matplotlib.patheffects as plte
import matplotlib.pyplot as plt
import pandas as pd
from numpy import linspace
from scipy.interpolate import interp1d

# from matplotlib.ticker import ScalarFormatter


def add_q_reader(readers, dir, ext):
    csv_file = open(dir + '/average.csv', 'r', newline='')
    csv_reader = pd.read_csv(csv_file, sep='\t')
    args = " ".join(csv_reader["Method"][0].split(" ")[3:])
    quality = csv_reader["Method"].map(lambda x: x.split(" ")[2])

    csv_reader["Method"].update(quality)
    csv_reader.drop_duplicates(subset=["Res bpp"], inplace=True, ignore_index=True)
    if ext == "jxl":
        readers["cjxl -q N " + args] = csv_reader
    if ext == "webp":
        readers["cwebp -q N " + args] = csv_reader
    if ext == "avif":
        readers["cavif -q N " + args] = csv_reader


def add_cq_reader(readers, dir):
    csv_file = open(dir + '/average.csv', 'r', newline='')
    csv_reader = pd.read_csv(csv_file, sep='\t')
    # avifenc -a cq-level="${q}"
    args = " ".join(csv_reader["Method"][0].split(" ")[3:])
    quality = csv_reader["Method"].map(lambda x: x.split(" ")[2].split("cq-level=")[1])

    csv_reader["Method"].update(quality)
    csv_reader.drop_duplicates(subset=["Res bpp"], inplace=True, ignore_index=True)
    readers["avifenc -a cq-level=N " + args] = csv_reader


def add_avif_reader(readers, dir):
    csv_file = open(dir + '/average.csv', 'r', newline='')
    csv_reader = pd.read_csv(csv_file, sep='\t')

    args = " ".join(csv_reader["Method"][0].split("--max ")[1].split(" ")[1:])
    quality = csv_reader["Method"].map(lambda x: x.split("--max ")[1].split(" ")[0])
    csv_reader["Method"].update(quality)
    csv_reader.drop_duplicates(subset=["Res bpp"], inplace=True, ignore_index=True)
    readers["avifenc --min (N-2) --max N " + args] = csv_reader


def plot_init():
    fig = plt.figure(figsize=(16, 9), dpi=150)
    grid = plt.GridSpec(4, 4, hspace=0.4, wspace=0.1)
    ax_main = fig.add_subplot(grid[:-1, :-1])
    ax_bottom = fig.add_subplot(grid[-1, 0:-1], xticklabels=[])
    ax_main.set_xscale('log')
    ax_bottom.set_xscale('log')
    # ax_main.xaxis.set_major_formatter(ScalarFormatter())
    return ax_main, ax_bottom


def plot_data(x, y, z, ax_main, ax_bottom, metric, n=0):
    f_y = interp1d(x, y, kind="cubic")
    f_z = interp1d(x, z, kind="cubic")
    x_new = linspace(min(x), max(x), num=len(x)*10)
    y_new = f_y(x_new)
    z_new = f_z(x_new)
    plot_2d(ax_main, ax_bottom, x, y, x_new, y_new, z_new, label=n)
    # add text markers -- quality
    for i, txt in enumerate(z):
        j = ax_main.annotate(str(txt), (x[i], y[i]), color="black")
        j.set_fontsize(5)
        j.set_path_effects([plte.Stroke(linewidth=0.5, foreground='white'),
                            plte.Normal()])


def plot_2d(ax_main, ax_bottom, x, y, x_new, y_new, z_new, label=''):
    ax_main.plot(x_new, y_new, label=label)
    ax_main.scatter(x, y,
                    linewidths=1, alpha=.7,
                    marker='o',
                    edgecolor='k',
                    s=20,
                    c='None')
    ax_bottom.plot(x_new, z_new)


def plot_config(ax_main, ax_bottom, metric):
    ax_main.grid(True, color='gray')
    ax_main.minorticks_on()
    ax_main.grid(True, which='minor', color='lightgray')
    # ax_main.set_xticks(np.arange(min(x_new), max(x_new)+1, 0.5))
    ax_main.set_xlabel("BPP")
    ax_main.set_ylabel(metric)
    # ax_main.set_ylabel("butteraugli pnorm")

    ax_main.legend()

    ax_bottom.grid(True, color='gray')
    ax_bottom.minorticks_on()
    ax_bottom.grid(True, which='minor', color='lightgray')
    # ax_bottom.set_xticks(np.arange(min(x_new), max(x_new)+1, 0.5))
    ax_bottom.set_ylim(0, 105)
    ax_bottom.set_ylabel("settings")
