#!/usr/bin/env python3

import os, shutil, difflib, glob

def get_pdb_list(ref_dir):
    mydir = os.getcwd()
    os.chdir(ref_dir)
    pdbs = glob.glob("*")
    os.chdir(mydir)
    return pdbs

def compare_topologies(refdata, pdbname, verbose):
    refdir = refdata + "/" + pdbname
    if os.path.isdir(refdir):
        os.chdir(refdir)
        reffiles = glob.glob("*")
        os.chdir("../..")
    ndifftot = 0
    for rf in reffiles:
        reffile  = refdir + "/" + rf
        testfile = "tests/" + pdbname + "/" + rf
        if not os.path.exists(testfile):
            print("Failed to create %s" % testfile)
        else:
            ndiff = 0
            with open(reffile, 'r') as ref:
                with open(testfile, 'r') as test:
                    diff = difflib.unified_diff(
                        ref.readlines(),
                        test.readlines(),
                        fromfile=reffile,
                        tofile=testfile)
            for line in diff:
                ndiff += 1
                if verbose:
                    print(line)
            if ndiff > 0:
                print("There were %d differences between reference file %s and test file" % rf)
                ndifftot += ndiff
    return ndifftot

def run_gromacs(pdb):
    # Implement running a simulation and running gmxcheck on the edr file.
    return True
    
def run_one_test(pdbname, test_dir, ref_dir, mkref, verbose):
    error_msg = ("Could not download and/or process data for %s" % pdbname)
    try:
        os.system("./nmr2gmx.py -n %s" % pdbname)
    except:
        print(error_msg)
        return
    if os.path.exists(pdb):
        target_dir = ref_dir + "/" + pdb
        if mkref:
            if not os.path.exists(target_dir):
                shutil.move(pdb, target_dir)
        else:
            shutil.move(pdb, test_dir)
            ndiff = compare_topologies(ref_dir, pdbname, verbose)
            mydir = os.getcwd()
            os.chdir(test_dir)
            os.chdir(pdb)
            gromacs_ok = run_gromacs(pdb)
            os.chdir("..")
            if ndiff == 0 and gromacs_ok:
                print("%s - Passed" % pdbname)
                shutil.rmtree(pdb)
            else:
                print("%s - %d file errors, gromacs: %r" % ( pdbname, ndiff, gromacs_ok  ) )
            os.chdir(mydir)
    else:
        print(error_msg)

# Main part of script
test_dir = "tests"
ref_dir  = "refdata"
pdbs = get_pdb_list(ref_dir)
for pdb in pdbs:
    run_one_test(pdb, test_dir, ref_dir, False, True)
