from subprocess import Popen, PIPE
import subprocess
import os

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


def run_qcache(output_dir, fs_subject, n_cpus, meas=[], streams=["cross", "long"]):
    if not meas:
        meas = []
    tp_sub, base_sub, ses = split_fs_name(fs_subject)
    if not ses:
        raise NotImplementedError("no base subject found. only implemented for long data {}".format(tp_sub))

    if meas:
        meas_str = "-measure " + " -measure ".join(meas)
    else:
        meas_str = ""

    # cross
    if "cross" in streams:
        if not base_sub:
            cmd = "recon-all -subjid {tp_sub} -qcache -parallel -openmp {n_cpus} {meas_str}".format(tp_sub=tp_sub,
                                                                                                n_cpus=n_cpus,
                                                                                                meas_str=meas_str)
            print("Running", cmd)
            run(cmd, env={"SUBJECTS_DIR": output_dir})

    # long
    if "long" in streams:
        if base_sub:
            cmd = "recon-all -long {tp_sub} {base_sub} -qcache -parallel -openmp {n_cpus} {meas_str}".format(tp_sub=tp_sub,
                                                                                                             base_sub=base_sub,
                                                                                                             n_cpus=n_cpus,
                                                                                                             meas_str=meas_str)
            print("Running", cmd)
            run(cmd, env={"SUBJECTS_DIR": output_dir})