"""A component that simulates a bedform formation
 using the cell model of Nishimori and Ouchi (1993)

Reference:
Nishimori, H., & Ouchi, N. (1993). Formation of ripple
 patterns and dunes by wind-blown sand. Physical Review
 Letters, 71(1), 197.

.. codeauthor:: Hajime Naruse

"""

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.animation as animation


class CellBedform():
    """Cell model for dunes. This model calculate sediment transport on the
       basis of simplified laws. This model assumes that bedload transport
       of sediment particles occurs in two modes: (1) rolling and sliding,
       and (2) saltation.
    """

    def __init__(self, grid=(100, 50), D=0.8, Q=0.6, L0=7.3, b=2.0):
        """
        Parameters
        -----------------

        grid : list(int, int), optional
            Size of computation grids. Grid sizes of X and Y coordinates
            need to be specified. Default values are 100x100.

        D : float, optional
            Diffusion coefficient for rolling and sliding transport.
            Larger values prescribes larger rates of tranport. Default
            value is 0.8.

        Q : float, optional
            Entrainment rate of saltation transport. Larger values prescribes
            the larger rate of sediment pick-up by flows. Default value is 0.6.

        L0 : float, optional
            Minimum length of saltation transport length. Default is 7.3.

        b : float, optional
            A coefficient to determine saltation length. Larger value
            prescribes longer transport length Default is 2.0.
        """

        # Copy input parameters
        self._xgrid = grid[0]
        self._ygrid = grid[1]
        self.D = D
        self.Q = Q
        self.L0 = L0
        self.b = b

        # Make initial topography
        self.h = np.random.rand(self._xgrid, self._ygrid)
        self.L = np.empty(self.h.shape)
        self.dest = np.empty(self.h.shape)

        # Make arrays for indeces showing grid of interest and neighbor grids
        self.y, self.x = np.meshgrid(
            np.arange(self._ygrid), np.arange(self._xgrid))
        self.xminus = self.x - 1
        self.xplus = self.x + 1
        self.yminus = self.y - 1
        self.yplus = self.y + 1

        # Periodic boundary condition
        self.xminus[0, :] = self._xgrid - 1
        self.xplus[-1, :] = 0
        self.yminus[:, 0] = self._ygrid - 1
        self.yplus[:, -1] = 0

        # Variables for visualization
        self.f = plt.figure(figsize=(8, 8))
        self.ax = self.f.add_subplot(111, projection='3d', azim=120)
        self.surf = None
        self.ims = []

    def run(self, steps=100):
        """Run the model for specified steps.

        Parameters
        ----------------------

        steps: integer, optional
            Number of steps for calculation. Default value is 100.

        """

        for i in range(steps):
            self.run_one_step()

            # show progress
            print('', end='\r')
            print('{:.1f} % finished'.format(i / steps * 100), end='\r')

            # store animation frames
            self._plot()
            self.ims.append([self.surf])

        # show progress
        print('', end='\r')
        print('100.0 % finished')

    def run_one_step(self):
        """Calculate one step of the model
        """

        x = self.x
        y = self.y
        xplus = self.xplus
        yplus = self.yplus
        xminus = self.xminus
        yminus = self.yminus
        D = self.D
        Q = self.Q
        L0 = self.L0
        b = self.b
        L = self.L
        dest = self.dest

        # Rolling and sliding
        # Amounts of sediment transported to/from adjacent grids are 1/6 D h,
        # and those to/from diagonal grids are 1/12 D h
        self.h = self.h + D * (-self.h + 1. / 6. *
                               (self.h[xplus, y] + self.h[xminus, y] + self.
                                h[x, yplus] + self.h[x, yminus]) + 1. / 12. *
                               (self.h[xplus, yplus] + self.h[xplus, yminus] +
                                self.h[xminus, yplus] + self.h[xminus, yplus]))

        # Saltation
        # Length of saltation is determined as:
        # L = L0 + b h
        # Thus, particles at higher elevation travel longer
        L = L0 + b * self.h  # Length of saltation
        L[np.where(L < 0)] = 0  # Avoid backward saltation
        np.round(L + x, out=dest)  # Grid number must be integer
        np.mod(dest, self._xgrid, out=dest)  # periodic boundary condition
        self.h = self.h - Q  # Entrainment
        for j in range(self.h.shape[0]):  # Settling
            self.h[dest[j, :].astype(np.int32),
                   y[j, :]] = self.h[dest[j, :].astype(np.int32), y[j, :]] + Q

    def _plot(self):
        """plot results on the figure.

        This is only to use inside of this module.

        """
        self.ax.set_zlim3d(-20, 150)
        self.ax.set_xlabel('Distance (X)')
        self.ax.set_ylabel('Distance (Y)')
        self.ax.set_zlabel('Elevation')
        self.surf = self.ax.plot_surface(
            self.x,
            self.y,
            self.h,
            cmap='jet',
            vmax=5.0,
            vmin=-5.0,
            antialiased=True)

    def show(self):
        """Show a figure to illustrate result of calculation
        """
        self._plot()
        plt.show()

    def save_images(self, filename='bed'):
        """Save image sequence

        Parameters
        --------------
        filename : str, optional
            file header of image sequence.

        """

        print('Saving an image sequence...')

        try:
            if len(self.ims) == 0:
                raise Exception('Run the model before saving images.')

            for i in range(len(self.ims)):
                plt.cla()
                self.ax.add_collection3d(self.ims[i][0])
                self.ax.autoscale_view()
                self.ax.set_zlim3d(-20, 150)
                self.ax.set_xlabel('Distance (X)')
                self.ax.set_ylabel('Distance (Y)')
                self.ax.set_zlabel('Elevation')
                plt.savefig(filename + '{:04d}.png'.format(i))

        except FileNotFoundError:
            print('cannot find directory/files')
        except Exception as error:
            print('Unexpected error occurred.')
            print(error)

    def animation(self, filename='anim.mp4', format='mp4'):
        """Show and save an animation to exhibit results of simulation.

        Parameters
        -----------------------
        filename: Str, optional
            A file name to store the animation movie.
            The default file name is 'anim.mp4'.

        format: Str, optional
            File format of the movie file. The format 'mp4' or 'gif' can be
            chosen. The softwares ffmpeg and imagemagick are required
            respectively.
        """
        try:
            ani = animation.ArtistAnimation(self.f, self.ims, interval=100)
            print("Saving a movie file. It may take several minutes...")

            # Check the file format
            if format == 'mp4':
                ani.save(filename, writer="ffmpeg")
            elif format == 'gif':
                ani.save(filename, writer="imagemagick")
            else:
                raise ValueError('Format not supported')

            print("A movie file was created.")

        except ValueError:
            print('Movie format is not supported in this environment. \
                Install ffmpeg or imagemagick for mp4 or gif formats.')


if __name__ == "__main__":

    cb = CellBedform(grid=(100, 100))
    cb.run(steps=10)
    # cb.animation(filename='anim.gif', format='gif')
    # cb.show()
    cb.save_images()
