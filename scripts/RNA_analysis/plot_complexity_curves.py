import sys
import os
import yaml
import  glob
import subprocess
import argparse
import pandas as pd
from matplotlib import pyplot as plt
import numpy as np
import math

def main(args):
    ccurves     = args.ccurves[0]
    x_min       = args.x_min
    x_max       = args.x_max
    if x_min < 0 or x_max <= x_min:
        sys.exit("problem with x-min or x-max ({}, {}). x-min must be equal or higher to 0 and less than x-max".format(x_min, x_max))
    output_name = args.output_name
    legend = [[],[]]
    global_x_max_ccurve_limit = 0
    global_y_max_ccurve_limit = 0
    ax = plt.subplot(111)
    #Each ccurve will get a different color
    colormap = plt.cm.gist_ncar
    plt.gca().set_color_cycle([colormap(i) for i in np.linspace(0, 0.9, len(ccurves))])
    col=math.ceil(float(len(ccurves))/30)
    for ccurve in ccurves:
        sample=ccurve.split('/')[1].split('.')[0]
        print "processing {}".format(ccurve)
        ccurve_table             = pd.io.parsers.read_csv(ccurve, sep='\t', header=0)
        ccurve_TOTAL_READS       = []
        ccurve_EXPECTED_DISTINCT = []
        if "TOTAL_READS" in ccurve_table:
            ccurve_TOTAL_READS       = ccurve_table["TOTAL_READS"].tolist()
            ccurve_EXPECTED_DISTINCT = ccurve_table["EXPECTED_DISTINCT"].tolist()
        elif "total_reads" in ccurve_table:
            ccurve_TOTAL_READS       = ccurve_table["total_reads"].tolist()
            ccurve_EXPECTED_DISTINCT = ccurve_table["distinct_reads"].tolist()
        else:
            sys.exit("Error, table {} is not in the expected format... has been generated with preseq?".format(ccurve))
        #I need to find the interpolation point to print the plots
        x_mim_ccurve_limit = computeLimit(x_min, ccurve_TOTAL_READS)
        x_max_ccurve_limit = computeLimit(x_max, ccurve_TOTAL_READS)
        if x_max_ccurve_limit > global_x_max_ccurve_limit:
            global_x_max_ccurve_limit = x_max_ccurve_limit
        if ccurve_EXPECTED_DISTINCT[x_max_ccurve_limit] > global_y_max_ccurve_limit:
            global_y_max_ccurve_limit = ccurve_EXPECTED_DISTINCT[x_max_ccurve_limit]
        p, = ax.plot(ccurve_TOTAL_READS[x_mim_ccurve_limit:x_max_ccurve_limit], ccurve_EXPECTED_DISTINCT[x_mim_ccurve_limit:x_max_ccurve_limit])
        legend[0].append(p)
        legend[1].append(sample)
    #plot perfect library as dashed line
    plt.plot([0, x_max], [0, x_max], color='black', linestyle='--', linewidth=1)
    plt.ylim(0, global_y_max_ccurve_limit + global_y_max_ccurve_limit*0.2)
    #label the axis
    plt.ylabel('EXPECTED DISTINCT READS')
    plt.xlabel('TOTAL READS')
    plt.title("Complexity curve: preseq")
    #change the font in oredr to plot a nicer picture
    font = {'size'   : 6}
    plt.rc('font', **font)
    #now resize the plot and add the legend on the right in order to avoid visualisation problems
    box = ax.get_position()
    ax.set_position([0.1, box.y0, box.width * 0.78, box.height])
    ax.legend(legend[0], legend[1],loc='center left', bbox_to_anchor=(1, 0.5),ncol=int(col))
    #ax.legend(legend[0], legend[1],loc='center left')
    #now save the plot
    plotname = output_name+".pdf"
    plt.savefig(plotname,format='pdf')
    plt.clf()
    return 0

def computeLimit(value, ccurve_TOTAL_READS):
    """This function returns the index of ccurve_TOTAL_READS containing the closest value to x_max"""
    if ccurve_TOTAL_READS[-1] < value:
        sys.exit("Attention: value is set to a value higher than the highest extrapolated point by preseq (value={}, ccurve_TOTAL_READS[-1]={}). Please specify a lower m-max.".format(value, ccurve_TOTAL_READS[-1]))
    first_point = 0
    last_point  = len(ccurve_TOTAL_READS)
    while first_point != last_point:
        middle_point = (first_point + last_point)/2
        middle_value = ccurve_TOTAL_READS[middle_point]
        if middle_value == value:
            return middle_point
        elif middle_value > value:
            last_point = middle_point -1
        else:
            first_point = middle_point +1
    return first_point


if __name__ == '__main__':
    parser = argparse.ArgumentParser("This script plots the complexity curves generated for one or several libraries. The script is designed to work using"
	" the output produced by preseq (http://smithlabresearch.org/software/preseq/). preseq version 1.0.0 is currenlty "
	"supported by this script (the script is compatible also with version 0.1.0). Preseq is a tool used to estimate the "
	"library complexity and/or to predict the library complexity. In the first case \"preseq c_curve\" should be use. In "
	"the second case \"preseq lc_extrap\" should be usued. Please, refer to preseq manual available at "
	"http://smithlabresearch.org/wp-content/uploads/manual.pdf for examples (pages 12 to 14 are the most informatives ones)")
    parser.add_argument('--ccurves'        , type=str, required=True, action='append', nargs='+', help="ccurves generated by preseq (http://smithlabresearch.org/software/preseq/)")
    parser.add_argument('--x-min'          , type=int, default=0        , help="lower x-limit (default 0)")
    parser.add_argument('--x-max'          , type=int, default=500000000, help="upper x-limit (default 500M)")
    parser.add_argument('--output-name'    , type=str, default='complexity_curves', help="output file name")
    args = parser.parse_args()
    main(args)

