from subprocess import Popen, PIPE
import subprocess
import os
from glob import glob


def run(command, env={}, ignore_errors=False):
    merged_env = os.environ
    merged_env.update(env)
    # DEBUG env triggers freesurfer to produce gigabytes of files
    merged_env.pop('DEBUG', None)
    process = Popen(command, stdout=PIPE, stderr=subprocess.STDOUT, shell=True, env=merged_env)
    while True:
        line = process.stdout.readline()
        line = str(line, 'utf-8')[:-1]
        print(line)
        if line == '' and process.poll() != None:
            break
    if process.returncode != 0 and not ignore_errors:
        raise Exception("Non zero return code: %d" % process.returncode)


def split_fs_name(fs_subject):
    if "long" in fs_subject:
        tp_sub, base_sub = fs_subject.split(".long.")
        tp_ses = tp_sub.split("ses-")[-1]
    else:
        tp_sub = fs_subject
        base_sub = ""
    ses = "ses" in fs_subject
    return tp_sub, base_sub, ses


def run_qcache(output_dir, fs_subject, n_cpus, template_names, meas=[], streams=["cross", "long"]):
    if not meas:
        meas = []
    tp_sub, base_sub, ses = split_fs_name(fs_subject)
    if not ses:
        raise NotImplementedError("no base subject found. only implemented for long data {}".format(tp_sub))

    if meas:
        meas_str = "-measure " + " -measure ".join(meas)
    else:
        meas_str = ""

    if meas:
        check_meas = meas[0]
    else:
        check_meas = "thickness"
    # cross
    if "cross" in streams:
        if not base_sub:
            for target in template_names:
                cmd = "recon-all -subjid {tp_sub} -qcache -parallel -openmp {n_cpus} -target {target} {meas_str}".format(
                    tp_sub=tp_sub,
                    n_cpus=n_cpus,
                    target=target,
                    meas_str=meas_str)
                print("Running", cmd)
                run(cmd, env={"SUBJECTS_DIR": output_dir})

                # perform simple check
                test_file = os.path.join(output_dir, fs_subject, "surf/rh.{}.fwhm0.fsaverage.mgh".format(check_meas))
                if not os.path.exists(test_file):
                    raise Exception("Something went wront. File not found after qcache {}".format(test_file))
    # long
    if "long" in streams:
        if base_sub:
            for target in template_names:
                cmd = "recon-all -long {tp_sub} {base_sub} -qcache -parallel -openmp {n_cpus} -target {target} {" \
                      "meas_str}".format(
                    tp_sub=tp_sub,
                    base_sub=base_sub,
                    n_cpus=n_cpus,
                    target=target,
                    meas_str=meas_str)
                print("Running", cmd)
                run(cmd, env={"SUBJECTS_DIR": output_dir})

                # perform simple check
                test_file = os.path.join(output_dir, fs_subject, "surf/rh.{}.fwhm0.fsaverage.mgh".format(check_meas))
                if not os.path.exists(test_file):
                    raise Exception("Something went wront. File not found after qcache {}".format(test_file))


def check_fs_subjects(sourcedata_dir, fs_dir):
    "checks that for every subject and session with T1w there is a finished cross and long fs subject"
    from bids.grabbids import BIDSLayout

    layout = BIDSLayout(sourcedata_dir)
    df = layout.as_data_frame()
    df = df[["subject", "session", "type"]].drop_duplicates().query("type=='T1w'")
    df.reset_index(inplace=True, drop=True)

    # fs
    os.chdir(fs_dir)
    df["cross"] = None
    df["long"] = None

    for r in df.itertuples(index=True):
        print(r)
        cross = True if glob("sub-{s}_ses-{ses}/scripts/recon-all.done".format(s=r.subject, ses=r.session)) else False
        long = True if glob(
            "sub-{s}_ses-{ses}.long.sub-*/scripts/recon-all.done".format(s=r.subject, ses=r.session)) else False

        df.loc[r.Index, "cross"] = cross
        df.loc[r.Index, "long"] = long

    missing = df[df.cross == False]
    raise_ex = False

    if len(missing) > 0:
        print("*** CROSS missing for {} entries".format(len(missing)))
        print(missing)
        raise_ex = True

    missing = df[df.long == False]
    if len(missing) > 0:
        print("*** LONG missing for {} entries".format(len(missing)))
        print(missing)
        raise_ex = True

    print("*** Found {} cross and {} long sessions from {} subjects".format(df.cross.sum(), df.long.sum(),
                                                                            len(df.subject.unique())))
    if raise_ex:
        raise Exception("SOME FS SUBJECTS ARE MISSING")
    else:
        print("Everything looks good")
