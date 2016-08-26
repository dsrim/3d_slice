import os,sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
from mayavi import mlab
import slice_io
from tvtk.api import tvtk


def plot_time_all(plot_specs_dict,var_num = 0):
    # make 3d slice plot in time-sequential order

    num_eqn = int(plot_specs_dict['num_eqn'])
    minval = - 1e-14
    maxval =   1e-14
    for key,value in plot_specs_dict['time_view'].items():
        t = plot_specs_dict['t_ticks'][key]
        path = plot_specs_dict['path']
        minvaln,maxvaln = compute_minmax(path,t,value,var_num,plot_specs_dict)
        minval = np.minimum(minval,minvaln)
        maxval = np.maximum(maxval,maxvaln)

    plot_specs_dict['minval'] = np.zeros((num_eqn,1))
    plot_specs_dict['maxval'] = np.zeros((num_eqn,1))
    plot_specs_dict['minval'][var_num] = minval
    plot_specs_dict['maxval'][var_num] = maxval

    f_list = []

    for key,value in plot_specs_dict['time_view'].items():
        t = plot_specs_dict['t_ticks'][key]
        path = plot_specs_dict['path']
        f_list.append(plot_time_instance(path,t,value,var_num,plot_specs_dict))

    return f_list

def compute_minmax(path,t,value,var_num,plot_specs_dict):
    num_eqn = int(plot_specs_dict['num_eqn'])
    file_list = value.split()
    maxval = 1e-14
    minval = -1e-14
    for file_name in file_list:
        patch_specs_list,patch_array_list = \
            slice_io.read_patch_list(path,file_name)
        for j in range(len(patch_array_list)):
            max_patch = patch_array_list[j][var_num::num_eqn].max()
            min_patch = patch_array_list[j][var_num::num_eqn].min()
            maxval = max(maxval,max_patch)
            minval = min(minval,min_patch)
    return minval,maxval

def plot_time_instance(path,t,value,var_num,plot_specs_dict):
    # make one plot at fixed time with multiple slices

    f = mlab.figure(size=(2000,1500))
    file_list = value.split()
    num_eqn = int(plot_specs_dict['num_eqn'])
    
    minval = plot_specs_dict['minval'][var_num]
    maxval = plot_specs_dict['maxval'][var_num]
    for file_name in file_list:
        plot_slice(path,file_name,f,var_num,num_eqn,minval,maxval)
    save_filename = 'test_output_' + str(t) + '.png'
    mlab.title('Solution at t=' + str(t) + '\n q ' + str(var_num+1),\
                size=0.25)
    cube_range = [plot_specs_dict['domain'][0][0],  
                  plot_specs_dict['domain'][0][1],  
                  plot_specs_dict['domain'][1][0],  
                  plot_specs_dict['domain'][1][1],  
                  plot_specs_dict['domain'][2][0],  
                  plot_specs_dict['domain'][2][1]]
    mlab.axes(extent = cube_range, line_width=3.0)
    ax = mlab.colorbar(orientation='vertical')
    mlab.outline(line_width=0.02)
    #f.scene.x_minus_view()

    #f.scene._update_view(1, -1, 1, 0, 0, 0)
    mlab.savefig(save_filename)
    f.scene.close()
    return None

def permute_orientation(orient_real,vector):
    new_vector = []
    new_vector.insert(orient_real[0], vector[0])
    new_vector.insert(orient_real[1], vector[1])
    new_vector.insert(orient_real[2], vector[2])
    return new_vector
    

def plot_slice(path,file_name,f,var_num,num_eqn,minval,maxval):
    # plot one slice

    patch_specs_list,patch_array_list = slice_io.read_patch_list(path,file_name)
    normal,m_slice,num_t_tick,translate = slice_io.q_output_name_read(file_name,all_data_dict)
    orient_dict = {'x':[1,2,0],'y':[0,2,1], 'z':[0,1,2]}
    orient_ord = {'x':0, 'y':1, 'z':2}
    orient_plane = {'x':'yz', 'y':'xz', 'z':'xy'}
    orient_real = orient_dict[normal]
    src_list = []
    pts_list = []
    vprint('\t(plot_slice) working on: ' + file_name)
    npatches = len(patch_specs_list)
    
    for k,patch_specs in enumerate(patch_specs_list):
        # load patch specs
        m1 = int(patch_specs[1])
        m2 = int(patch_specs[2])
        ulo = float(patch_specs[3])
        vlo = float(patch_specs[4])
        d1 = float(patch_specs[5])
        d2 = float(patch_specs[6])

        # debugging outputs
        vprint('\t(plot_slice) patch number ' + str(k))
        vprint('\t(plot_slice) ' + str(ulo)  + ', ' + str(vlo) + '---' \
                + str(ulo + d1*m1) + ', ' + str(vlo + d2*m2))
        vprint('\t(plot_slice) ' + str(d1) + 'x ' + str(d2))

        # center cells
        #xi1lo_c = xi1lo #+ d1/2 # _c for "center"
        #xi1hi_c = xi1lo_c + d1*m1
        #xi2lo_c = xi2lo #+ d2/2
        #xi2hi_c = xi2lo_c + d2*m2

        translate_lo = translate - 5e-5
        translate_hi = translate + 5e-5

        translate_lo2 = translate - 8e-5
        translate_hi2 = translate + 8e-5

        u = np.linspace(ulo,ulo + m1*d1,m1)
        v = np.linspace(vlo,vlo + m2*d2,m2)
        tr = np.linspace(translate_lo,translate_hi,2)

        grids = permute_orientation(orient_real,[u,v,tr]) 
        m_real = permute_orientation(orient_real,[m1,m2,1])
        x,y,z = np.meshgrid(grids[0],grids[1],grids[2],indexing='ij')

        q_sol = patch_array_list[k][var_num::num_eqn].reshape(m_real[0],m_real[1],m_real[2],order='F')
        q_sol = q_sol.repeat(2,axis=orient_ord[normal])

        objname = orient_plane[normal] + '_' + str(translate) + '_' + str(k) 
        src_list.append(mlab.pipeline.scalar_field(x,y,z,q_sol,name = objname))

        #sg = tvtk.StructuredGrid(dimensions=x.shape, points=pts_list[k])
        #tr2 = np.linspace(translate_lo2,translate_hi2,2)
        for tr2val in [translate_lo2, translate_hi2]:
            tr2 = np.array(tr2val)
            grids = permute_orientation(orient_real,[u,v,tr2]) 
            m_real = permute_orientation(orient_real,[m1,m2,1])
            x,y,z = np.meshgrid(grids[0],grids[1],grids[2],indexing='ij')
        
            pts = np.empty(z.shape + (3,), dtype=float)
            pts[..., 0] = x
            pts[..., 1] = y
            pts[..., 2] = z
            pts = pts.transpose(2, 1, 0, 3).copy()
            pts.shape = pts.size / 3, 3
        
            sg = tvtk.StructuredGrid(dimensions=x.shape, points=pts)
            d = mlab.pipeline.add_dataset(sg)
            g1 = mlab.pipeline.grid_plane(d, line_width=0.25)
            g1.grid_plane.axis = normal




    color_choice = 'Spectral'
    axis_str = normal + '_axes'
    for k,src in enumerate(src_list):
        # plot two slices according to adaptive mesh level
        # patch one
        yp = mlab.pipeline.scalar_cut_plane(src, plane_orientation=axis_str,opacity=1.0,figure=f,vmin=minval,vmax=maxval,colormap=color_choice)

        #yp = mlab.pipeline.image_plane_widget(src, plane_orientation=axis_str,opacity=0.5,figure=f,vmin=minval,vmax=maxval,colormap=color_choice)


        tr_vec = np.zeros(3)
        tr_vec[orient_ord[normal]] = translate - 5e-5*k/npatches
        yp.implicit_plane.origin = (tr_vec[0],tr_vec[1],tr_vec[2])
        yp.implicit_plane.visible = False
        mlab.outline(line_width=0.025)

        
        # patch two
        yp = mlab.pipeline.scalar_cut_plane(src, plane_orientation=axis_str,opacity=1.0,figure=f,vmin=minval,vmax=maxval,colormap=color_choice)
        #yp = mlab.pipeline.image_plane_widget(src, plane_orientation=axis_str,opacity=1.0,figure=f,vmin=minval,vmax=maxval,colormap=color_choice)
        tr_vec[orient_ord[normal]] = translate + 5e-5*k/npatches
        yp.implicit_plane.origin = (tr_vec[0],tr_vec[1],tr_vec[2])
        yp.implicit_plane.visible = False
        mlab.outline(line_width=0.025)

    
    return 

def slices_plot_spec(all_data_dict):
    plot_spec_dict = {}
    plot_spec_dict['domain'] = slice_io.output_cube_range(all_data_dict)
    plot_spec_dict['t_ticks'] = slice_io.output_time_ticks(all_data_dict)
    plot_spec_dict.update(slice_io.output_slices_spec(all_data_dict))
    plot_spec_dict['slice_view'],plot_spec_dict['time_view'] = slice_io.output_slice_view(all_data_dict)
    plot_spec_dict['path'] = all_data_dict['path']
    plot_spec_dict['num_eqn'] = all_data_dict['num_eqn']
    domain_spec_list = slice_io.output_cube_range(all_data_dict)
    plot_spec_dict['xrange'] = [domain_spec_list[0][0], domain_spec_list[0][1]]
    plot_spec_dict['yrange'] = [domain_spec_list[1][0], domain_spec_list[1][1]]
    plot_spec_dict['zrange'] = [domain_spec_list[2][0], domain_spec_list[2][1]]
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
ax_list = plot_time_all(plot_specs_dict,0)


