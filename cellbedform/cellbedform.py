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
import ipdb


class CellBedform():
    """Cell model for dunes
    """

    def __init__(self,
                 grid=(100, 50),
                 D=0.8,
                 Q=0.6,
                 L0=7.3,
                 b=2.0,
                 savefig=False,
                 figname=None):

        # Copy input parameters
        self._xgrid = grid[0]
        self._ygrid = grid[1]
        self.D = D
        self.Q = Q
        self.L0 = L0
        self.b = b

        self.savefig = savefig
        self.figname = figname

        # Make initial topography
        self.h = np.random.rand(self._xgrid, self._ygrid)
        self.L = np.empty(self.h.shape)
        self.dest = np.empty(self.h.shape)

        # Make array for indeces showing grid of interest and neighbor grids
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

        # Animation
        self.f = plt.figure(figsize=(8, 8))
        self.ax = self.f.add_subplot(111, projection='3d', azim=120)
        self.ax = self.f.add_subplot(111, projection='3d', azim=120)
        self.ax.set_zlim3d(-20, 150)
        self.ax.set_xlabel('Distance (X)')
        self.ax.set_ylabel('Distance (Y)')
        self.ax.set_zlabel('Elevation')
        self.surf = None
        self.ims = []

    def run(self, steps=100):
        """Run the model
        """

        for i in range(steps):
            self.run_one_step()

            # show progress
            print('', end='\r')
            print('{:.1f} % finished'.format(i / steps * 100), end='\r')

            # store animation frames
            self.plot()
            plt.savefig("bedform{:04}.png".format(i))
            self.ims.append([self.surf])

    def run_one_step(self):
        """Run the model for one step
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

        # rolling and sliding
        # Amounts of sediment transported to adjacent grids are 1/6 D \times h,
        # and those to diagonal grids are 1/12 D \times h
        self.h = self.h + D * (-self.h + 1. / 6. *
                               (self.h[xplus, y] + self.h[xminus, y] + self.
                                h[x, yplus] + self.h[x, yminus]) + 1. / 12. *
                               (self.h[xplus, yplus] + self.h[xplus, yminus] +
                                self.h[xminus, yplus] + self.h[xminus, yplus]))

        # Saltation
        L = L0 + b * self.h  # Length of saltation
        L[np.where(L < 0)] = 0  # Avoid backward saltation
        np.round(L + x, out=dest)
        np.mod(dest, self._xgrid, out=dest)  # periodic boundary condition
        self.h = self.h - Q  # Entrainment
        for j in range(self.h.shape[0]):  # Settling
            self.h[dest[j, :].astype(np.int32),
                   y[j, :]] = self.h[dest[j, :].astype(np.int32), y[j, :]] + Q

    def plot(self):
        # plt.cla()
        self.surf = self.ax.plot_surface(
            self.x, self.y, self.h, cmap='jet', vmax=5.0, vmin=-5.0)

    def imshow(self):
        plt.show()


if __name__ == "__main__":

    cb = CellBedform(grid=(100, 100))
    cb.run(10)
    ani = animation.ArtistAnimation(cb.f, cb.ims, interval=10)
    # ipdb.set_trace()
    # ani.save('anim.gif', writer="imagemagick")
    # ani.save('anim.mp4', writer="ffmpeg")
    cb.imshow()
