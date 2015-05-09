import os,sys
import numpy as np
from mayavi import mlab
import slice_io


def plot_time_all(plot_specs_dict):
    # make 3d slice plot in time-sequential order
    for key,value in plot_specs_dict['time_view'].items():
        t = plot_specs_dict['t_ticks'][key]
        path = plot_specs_dict['path']
        plot_time_instance(path,t,value)
    return

def plot_time_instance(path,t,value):
    # make one plot at fixed time with multiple slices

    f = mlab.figure(size=(1000,1000))
    file_list = value.split()
    for file_name in file_list:
        plot_slice(path,file_name,f)
    save_filename = 'test_output_' + str(t) + '.png'
    mlab.title('Solution at t=' + str(t))
    mlab.savefig(save_filename)
    #mlab.show()
    return

def permute_orientation(orient_real,vector):
    new_vector = []
    new_vector.insert(orient_real[0], vector[0])
    new_vector.insert(orient_real[1], vector[1])
    new_vector.insert(orient_real[2], vector[2])
    return new_vector
    

def plot_slice(path,file_name,f):
    # plot one slice

    patch_specs_list,patch_array_list = slice_io.read_patch_list(path,file_name)
    normal,m_slice,num_t_tick,translate = slice_io.q_output_name_read(file_name,all_data_dict)
    orient_dict = {'x':[1,2,0],'y':[0,2,1], 'z':[0,1,2]}
    orient_ord = {'x':0, 'y':1, 'z':2}
    orient_real = orient_dict[normal]
    src_list = []
    vprint('\t(plot_slice) working on: ' + file_name)
    for k,patch_specs in enumerate(patch_specs_list):
        m1 = int(patch_specs[1])
        m2 = int(patch_specs[2])
        xi1lo = float(patch_specs[3])
        xi2lo = float(patch_specs[4])
        d1 = float(patch_specs[5])
        d2 = float(patch_specs[6])
        xi1lo_c = xi1lo + d1/2 # _c for "center"
        xi1hi_c = xi1lo_c + d1*m1
        xi2lo_c = xi2lo + d2/2
        xi2hi_c = xi2lo_c + d2*m2
        translate_lo = translate - 1e-4
        translate_hi = translate + 1e-4
        axis4slice = []
        xi1 = np.linspace(xi1lo_c,xi1hi_c,m1)
        xi2 = np.linspace(xi2lo_c,xi2hi_c,m2)
        tr = np.linspace(translate_lo,translate_hi,2)
        grid_side = permute_orientation(orient_real,[xi1,xi2,tr]) 
        m_real = permute_orientation(orient_real,[m1,m2,1])
        x,y,z = np.meshgrid(grid_side[0],grid_side[1],grid_side[2],indexing='ij')
        q_sol = patch_array_list[k].reshape(m_real[0],m_real[1],m_real[2],order='F')
        q_sol = q_sol.repeat(2,axis=orient_ord[normal])
        src_list.append(mlab.pipeline.scalar_field(x,y,z,q_sol))

    axis_str = normal + '_axes'
    for src in src_list:
        #yp = mlab.pipeline.scalar_cut_plane(src, plane_orientation=axis_str,opacity=0.5,colormap='hot',figure=f)
        yp = mlab.pipeline.scalar_cut_plane(src, plane_orientation=axis_str,opacity=0.5,figure=f)
        tr_vec = np.zeros(3)
        tr_vec[orient_ord[normal]] = translate
        yp.implicit_plane.origin = (tr_vec[0],tr_vec[1],tr_vec[2])
    return

def slices_plot_spec(all_data_dict):
    plot_spec_dict = {}
    plot_spec_dict['domain'] = slice_io.output_cube_range(all_data_dict)
    plot_spec_dict['t_ticks'] = slice_io.output_time_ticks(all_data_dict)
    plot_spec_dict.update(slice_io.output_slices_spec(all_data_dict))
    plot_spec_dict['slice_view'],plot_spec_dict['time_view'] = slice_io.output_slice_view(all_data_dict)
    plot_spec_dict['path'] = all_data_dict['path']
    return plot_spec_dict


# verbose switch
verbose = True
if verbose:
    def vprint(*args):
        for arg in args:
            print(arg)
else:
    vprint = lambda *a: None


all_data_dict = slice_io.process_dir('./_output')
vprint('listing all variables: ')
for key,value in all_data_dict.items():
    vprint(key)
    vprint('\t' + value)
vprint('= done')


plot_specs_dict = slices_plot_spec(all_data_dict)
plot_time_all(plot_specs_dict)

