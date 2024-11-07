import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


def make_data():
    print("Making data")
    normal = np.random.normal(0, 500, 10_000_000)
    num = np.random.randint(0, 100)
    data_file = Path(f"data_{num}.dat")
    normal.tofile(data_file)
    print(f"Made: {data_file}")


def plot_data():
    if len(sys.argv) < 2:
        print("Error no file given", file=sys.stderr)
        exit(2)
    data_file = Path(sys.argv[-1])
    normal = np.fromfile(data_file)
    plt.hist(normal, bins=500)
    plt.savefig(f"{data_file.stem}.png")


if __name__ == "__main__":
    plot_data()
