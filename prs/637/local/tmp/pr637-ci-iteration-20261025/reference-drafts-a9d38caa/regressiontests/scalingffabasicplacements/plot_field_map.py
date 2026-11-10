import glob
import os

import numpy
import matplotlib
import matplotlib.pyplot

"""
Routines to plot the field map output from DumpEMFields in ScalingFFA models

To run:
* Uncomment the FieldMapGenerator lines in the OPALX input files ScalingFFABasicPlacements.in
* Run the OPALX simulation
* Check that a field map was generated in data/map.dat
* Run this script

You might be able to get it to work for ScalingFFARealisticPlacements.in by
uncommenting the line
    plotter = realistic_plotter()
The paths are set up that you should still run it from the BasicPlacements folder

Writes output to the same folder where the data is stored (usually "data/")

Requires numpy and matplotlib installed
"""

class PlotFieldMap:
    def __init__(self):
        """
        Initialise variables
        """
        self.x_list, self.z_list, self.by_list = [], [], []
        self.beam_x_list, self.beam_y_list, self.beam_z_list, self.beam_s_list = [], [], [], []
        self.file_path = "data/"

    def load(self):
        """
        Load two files:
        * field map, in hardcoded map.dat
        * beam file, in *_DesignPath.dat
        """
        self.load_field_map()
        self.load_beam()

    def load_field_map(self):
        """
        Load the field map
        """
        filename = os.path.join(self.file_path, "map.dat")
        fin = open(filename)
        for i in range(12):
            fin.readline()
        self.x_list, self.z_list, self.by_list = [], [], []
        for line in fin.readlines():
            words = [float(x) for x in line.split()]
            self.x_list.append(words[0])
            self.z_list.append(words[2])
            self.by_list.append(words[5])

    def load_beam(self):
        """
        Load the beam
        """
        beam_path= os.path.join(self.file_path, "*_DesignPath.dat")
        beam_name = glob.glob(beam_path)[0]
        beam_file = open(beam_name)
        beam_file.readline() # header
        for line in beam_file.readlines():
            words = line.split()
            self.beam_s_list.append(float(words[0]))
            self.beam_x_list.append(float(words[1]))
            self.beam_y_list.append(float(words[2]))
            self.beam_z_list.append(float(words[3]))

    def plot_xz_field_map(self):
        """
        Plot the xz field map, i.e. looking down on the facility
        """
        figure = matplotlib.pyplot.figure()
        axes = figure.add_subplot(1, 1, 1)
        cmax = max([abs(by) for by in self.by_list])
        h = axes.hist2d(self.x_list, self.z_list, weights=self.by_list, bins=[self.x_space, self.z_space], cmap="coolwarm", vmin=-cmax, vmax=cmax)
        figure.colorbar(h[3])
        beam_h = axes.plot(self.beam_x_list, self.beam_z_list)
        axes.set_xlabel("x [m]")
        axes.set_ylabel("z [m]")
        figure.savefig(os.path.join(self.file_path, "fieldmap_xz.png"))
        print("Done xz plot")

    def plot_ys_trajectory(self):
        """
        Plot the ys beam trajectory
        """
        figure = matplotlib.pyplot.figure()
        axes = figure.add_subplot(1, 1, 1)
        axes.set_ylim([-0.01, 0.01])
        beam_h = axes.plot(self.beam_s_list, self.beam_y_list)
        axes.set_xlabel("s [m]")
        axes.set_ylabel("y [m]")
        figure.savefig(os.path.join(self.file_path, "fieldmap_ys.png"))
        print("Done ys plot")

    x_space = numpy.linspace(-10.01, 2.01, 202)
    z_space = numpy.linspace(-5.01, 5.01, 202)

def basic_placements_plotter():
    """
    Setup for ScalingFFABAsicPlacements.in
    """
    plotter = PlotFieldMap()
    plotter.x_space = numpy.linspace(-2.01, 2.01, 202)
    plotter.z_space = numpy.linspace(-1.01, 3.01, 202)
    plotter.file_path = "data/"
    return plotter

def realistic_plotter():
    """
    Setup for ScalingFFARealisticLattice.in
    """
    plotter = PlotFieldMap()
    plotter.x_space = numpy.linspace(-10.01, 2.01, 202)
    plotter.z_space = numpy.linspace(-5.01, 5.01, 202)
    plotter.file_path = "../ScalingFFARealisticLattice/data/"
    return plotter

def main():
    """
    main function
    """
    plotter = basic_placements_plotter()
    #plotter = realistic_plotter()
    plotter.load()
    plotter.plot_xz_field_map()
    plotter.plot_ys_trajectory()

if __name__ == "__main__":
    main()
    matplotlib.pyplot.show(block=False)
    input("Press <CR> to finish")
