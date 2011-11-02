#!/usr/bin/env python
#
# python -m cpa.util.median_profiles -o treatment_profiles_mean.txt ~/src/az/properties/supplement.properties well_profiles_mean.txt Well CompoundConcentration

import itertools
import sys
from optparse import OptionParser
import numpy as np
import cpa
from .profiles import Profiles

def parse_arguments():
    parser = OptionParser("usage: %prog [-o OUTPUT-FILENAME] PROPERTIES-FILE INPUT-FILENAME INPUT-GROUP OUTPUT-GROUP")
    parser.add_option('-o', dest='output_filename', help='file to store the profiles in')
    options, args = parser.parse_args()
    if len(args) != 4:
        parser.error('Incorrect number of arguments')
    return options, args

if __name__ == '__main__':
    options, (properties_file, input_filename, input_group_name, output_group_name) = parse_arguments()
    cpa.properties.LoadFile(properties_file)

    input_group_r, input_colnames = cpa.db.group_map(input_group_name, reverse=True)
    output_group, output_colnames = cpa.db.group_map(output_group_name)
    input_profiles = Profiles.load(input_filename)
    input_profiles.assert_not_isnan()

    d = {}
    for key, vector in input_profiles.items():
        images = input_group_r[key]
        groups = [output_group[image] for image in images]
        if groups.count(groups[0]) != len(groups):
            print >>sys.stderr, 'Error: Input group %r contains images in %d output groups' % (key, len(set(groups)))
            sys.exit(1)
        d.setdefault(groups[0], []).append(vector)

    keys = d.keys()
    output_profiles = Profiles(keys, [np.median(np.vstack(d[key]), 0)
                                      for key in keys], input_profiles.variables)
    output_profiles.save(options.output_filename)
