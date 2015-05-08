from mayavi import mlab
import numpy as np
from clawpack.pyclaw import Solution

#sol = Solution(
z_pos1=-0.4
z_pos2=0.4
x, y, z = np.mgrid[-1:1:20j,-1:1:20j,z_pos1:z_pos2:2j]
src = mlab.pipeline.scalar_field(x, y, z, x*x + y*y + z*z)
yp = mlab.pipeline.scalar_cut_plane(src, plane_orientation='z_axes',opacity=0.5,colormap='hot')
yp.implicit_plane.origin = (0,0,z_pos1+1e-12)
yp = mlab.pipeline.scalar_cut_plane(src, plane_orientation='z_axes',opacity=0.5,colormap='hot')
yp.implicit_plane.origin = (0,0,z_pos2)

#x, y, z = np.mgrid[-1:1:2j,-1:1:20j,-1:1:20j]
#src = mlab.pipeline.scalar_field(x, y, z, x*x + y*y + z*z)
#yp = mlab.pipeline.scalar_cut_plane(src, plane_orientation='x_axes',opacity=0.5,colormap='hot')
#yp.implicit_plane.origin = (1-1e-10,0,0)
#yp = mlab.pipeline.scalar_cut_plane(src, plane_orientation='x_axes',opacity=0.5,colormap='hot')
#yp.implicit_plane.origin = (-(1-1e-10),0,0)
mlab.show()
