
import os, sys
import numpy as np


def read_clawfile(path,filename):
    # read ascii text file and output as string
    data_file = os.path.join(path,filename)
    with open(data_file,mode='r') as data:
        data_str = data.read()
    return data_str

def dictionarize(data_str):
    # dictionarize string data from clawpack output
    data_dict = {}
    if '=:' in data_str:
        vprint('\t(dictionarize) this must be a .data file')
        data_str_lines = data_str.split('\n')
        for line in data_str_lines:
            split_line = line.split('=:')
            if len(split_line) < 2:
                continue
            attr = split_line[1].replace(' ','')
            val = split_line[0]
            data_dict[attr] = val
    return data_dict

def process_dir(path):
    # do read_clawfile + dictionarize over all files in directory
    file_list = os.listdir(path)
    all_data_dict = {}
    for claw_file in file_list:
        if not claw_file.startswith('.'):
            vprint('(process_dir) looking at: ' + claw_file)
            claw_data_str = read_clawfile(path,claw_file)
            new_dict = dictionarize(claw_data_str)
            all_data_dict.update(new_dict)
    return all_data_dict

def output_time_ticks(all_data_dict):
    # returns time ticks
    # depending on output_style chosen
    if int(all_data_dict['output_style']) == 1:
        t0 = float(all_data_dict['t0'])
        tN = float(all_data_dict['tfinal'])
        num_output_times = int(all_data_dict['num_output_times'])
        output_t0 = bool('T' in all_data_dict['output_t0'])
        t_ticks = np.linspace(t0,tN,num_output_times)
        if not output_t0:
            t_ticks = t_ticks[1:]
    return t_ticks


def slices_plot_specs(all_data_dict):
    plot_specs_dict = {}
    plot_specs_dict['t_ticks'] = output_time_ticks(all_data_dict)
    return plot_specs_dict

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

plot_specs_dict = slices_plot_specs(all_data_dict)
