#!/usr/bin/env python3
import argparse
import os
from glob import glob

from utils import run_qcache, run


__version__ = open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'version')).read()

parser = argparse.ArgumentParser(description='FreeSurfer utils')
parser.add_argument('bids_dir', help='The directory with the input dataset '
                                     'formatted according to the BIDS standard.')
parser.add_argument('output_dir', help='The directory where the output files '
                                       'should be stored. If you are running group level analysis '
                                       'this folder should be prepopulated with the results of the'
                                       'participant level analysis.')
parser.add_argument('analysis_level', help='Level of the analysis that will be performed. '
                                           'Multiple participant level analyses can be run independently '
                                           '(in parallel) using the same output_dir. '
                                           '"group"',
                    choices=['participant', 'group'])
parser.add_argument('--participant_label', help='The label of the participant that should be analyzed. The label '
                                                'corresponds to sub-<participant_label> from the BIDS spec '
                                                '(so it does not include "sub-"). If this parameter is not '
                                                'provided all subjects should be analyzed. Multiple '
                                                'participants can be specified with a space separated list.',
                    nargs="+")
parser.add_argument('--n_cpus', help='Number of CPUs/cores available to use.',
                    default=1, type=int)
parser.add_argument('--workflow', help='Workflow run.'
                                       'qcache: run qcache for cross and long session folders. opt arg: --measurements',
                    choices=["qcache"],
                    nargs="+")
parser.add_argument('--streams', help='apply workflow to cross, base, long subjects',
                    choices=["cross", "base", "long"],
                    nargs="+")
parser.add_argument('--template_names', help='Name for templates used for qcache. E.g. fsaverage fsaverage4'
                                             '(piped through to -target)',
                    default=["fsaverage"], nargs="+")
parser.add_argument('--license_key',
                    help='FreeSurfer license key - letters and numbers after "*" in the email you received after registration. To register (for free) visit https://surfer.nmr.mgh.harvard.edu/registration.html',
                    required=True)
# parser.add_argument('--parcellations', help='Group2 option: cortical parcellation(s) to extract stats from.',
#                     choices=["aparc", "aparc.a2009s"],
#                     default=["aparc"],
#                     nargs="+")
parser.add_argument('--measurements', help='measurements for qcache',
                    nargs="+")

parser.add_argument('-v', '--version', action='version',
                    version='BIDS-App example version {}'.format(__version__))

args = parser.parse_args()
# workaround for https://mail.nmr.mgh.harvard.edu/pipermail//freesurfer/2016-July/046538.html
output_dir = os.path.abspath(args.output_dir)

# get session subjects
os.chdir(output_dir)
fs_subjects = []
if args.participant_label:
    for s in args.participant_label:
        fs_subjects.extend(sorted(glob("sub-" + s + "_ses-*")))
# for all subjects
else:
    fs_subjects = sorted(glob("sub-*_ses-*"))

print("Running ", fs_subjects)
# running participant level
if args.analysis_level == "participant":
    for t in args.template_names:
        if not os.path.exists(os.path.join(output_dir, t)):
            run("cp -rf " + os.path.join(os.environ["SUBJECTS_DIR"], t) + " " + os.path.join(output_dir,t),
                ignore_errors=False)
    if not os.path.exists(os.path.join(output_dir, "lh.EC_average")):
        run("cp -rf " + os.path.join(os.environ["SUBJECTS_DIR"], "lh.EC_average") + " " + os.path.join(output_dir,
                                                                                                       "lh.EC_average"),
            ignore_errors=False)
    if not os.path.exists(os.path.join(output_dir, "rh.EC_average")):
        run("cp -rf " + os.path.join(os.environ["SUBJECTS_DIR"], "rh.EC_average") + " " + os.path.join(output_dir,
                                                                                                       "rh.EC_average"),
            ignore_errors=False)


    good_ses = []
    bad_ses = []
    if "qcache" in args.workflow:
        if args.streams is None:
            streams = ["cross", "long"]
        else:
            streams = args.streams
        for fs_subject in fs_subjects:
            print("Running qcache for {}".format(fs_subject))
            try:
                run_qcache(output_dir, fs_subject, args.n_cpus, args.template_names, args.measurements, streams)
                good_ses.append(fs_subject)
            except:
                bad_ses.append(fs_subject)
        print("Qcache finished. OK subjects: {}".format(good_ses))
        if bad_ses:
            raise Exception("Some subjects failed: {}".format(bad_ses))