
import os, sys
import numpy as np
import pdb

def read_clawfile(path,filename):
    # read ascii text file and output as string
    data_file = os.path.join(path,filename)
    with open(data_file,mode='r') as data:
        data_str = data.read()
    return data_str

def dict_strval_append(data_dict,key,val):
    if key in data_dict:
        data_dict[key] += ' ' + val
    else:
        data_dict[key] = val
    return data_dict

def dict_strval_merge(all_data_dict,new_dict):
    for key,val in new_dict.items():
        all_data_dict = dict_strval_append(all_data_dict,key,val)
    return all_data_dict


def dictionarize(data_str,claw_file):
    # dictionarize string data from clawpack output
    # if duplicate entry appears, append to end of val-string 
    #   (e.g in slices.data x,y,z redefined all rows)
    data_dict = {}
    if '=:' in data_str:
        vprint('\t(dictionarize) this must be a .data file')
        data_str_lines = data_str.split('\n')
        for line in data_str_lines:
            split_line = line.split('=:')
            if len(split_line) < 2:
                continue
            key = split_line[1].replace(' ','')
            val = split_line[0]
            dict_strval_append(data_dict,key,val)
    elif ('grid_number' in data_str) and ('AMR_level' in data_str):
        vprint('\t(dictionarize) this must be sol-state q data')
        dict_strval_append(data_dict,'q',claw_file)
    elif 'time' in data_str:
        vprint('\t(dictionarize) this must be sol-time t data')
        dict_strval_append(data_dict,'t',claw_file)
    else:
        vprint('\t(dictionarize) !! empty or unexpected file: ' + claw_file)
    return data_dict

def process_dir(path):
    # do read_clawfile + dictionarize over all files in directory
    file_list = os.listdir(path)
    all_data_dict = {}
    for claw_file in file_list:
        if not claw_file.startswith('.'):
            vprint('(process_dir) looking at: ' + claw_file)
            claw_data_str = read_clawfile(path,claw_file)
            new_dict = dictionarize(claw_data_str,claw_file)
            all_data_dict = dict_strval_merge(all_data_dict,new_dict)
    return all_data_dict

def output_time_ticks(all_data_dict):
    # returns time ticks, dep on output_style 
    if int(all_data_dict['output_style']) == 1:
        t0 = float(all_data_dict['t0'])
        tN = float(all_data_dict['tfinal'])
        num_output_times = int(all_data_dict['num_output_times'])
        output_t0 = bool('T' in all_data_dict['output_t0'])
        t_ticks = np.linspace(t0,tN,num_output_times+1)
        if not output_t0:
            t_ticks = t_ticks[1:]
    return t_ticks

def output_slices_spec(all_data_dict):
    # outputs specifications needed for slice plots
    slices_spec_dict = {}
    key_list_nslices = ['nslices_yz','nslices_xz','nslices_xy']
    for key in key_list_nslices:
        slices_spec_dict[key] = int(all_data_dict[key])
    key_list_translates = ['x','y','z']
    for key in key_list_translates:
        slice_translates = map(float,all_data_dict[key].split())
        slices_spec_dict[key] = np.array(slice_translates)
    return slices_spec_dict

def output_cube_range(all_data_dict):
    # outputs corners of the cube domain
    domain_spec_list = []
    domain_lower_list = np.array(map(float, all_data_dict['lower'].split()))
    domain_upper_list = np.array(map(float, all_data_dict['upper'].split()))
    for j in range(3):
        domain_spec_list.append((domain_lower_list[j],domain_upper_list[j]))
    return domain_spec_list

def output_slice_view(all_data_dict):
    slice_view_dict = {}
    time_view_dict = {}
    sol_file_list = all_data_dict['q'].split()
    orient_dict = {'xy':'z', 'yz':'x','xz':'z'}
    for sol_file in sol_file_list:
        normal = orient_dict[sol_file[6:8]]
        m_slice = int(sol_file[8])-1
        num_t_tick = int(sol_file[11:])
        translate = float(all_data_dict[normal].split()[m_slice])
        slice_view_dict = dict_strval_append(slice_view_dict,(normal,translate),sol_file)
        time_view_dict = dict_strval_append(time_view_dict,num_t_tick,sol_file)
    return slice_view_dict,time_view_dict

def slices_plot_spec(all_data_dict):
    plot_spec_dict = {}
    plot_spec_dict['domain'] = output_cube_range(all_data_dict)
    plot_spec_dict['t_ticks'] = output_time_ticks(all_data_dict)
    plot_spec_dict.update(output_slices_spec(all_data_dict))
    plot_spec_dict['slice_view'],plot_spec_dict['time_view'] = output_slice_view(all_data_dict)
    return plot_spec_dict

# verbose switch
verbose = True
if verbose:
    def vprint(*args):
        for arg in args:
            print(arg)
else:
    vprint = lambda *a: None


all_data_dict = process_dir('./_output')
for key,value in all_data_dict.items():
    vprint(key)
    vprint('\t' + value)

plot_specs_dict = slices_plot_spec(all_data_dict)

for key,value in plot_specs_dict['time_view'].items():
    t = plot_specs_dict['t_ticks'][key]

