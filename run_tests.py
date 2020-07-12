#!/usr/bin/env python3

import os, shutil, difflib, glob

def get_pdb_list(ref_dir):
    mydir = os.getcwd()
    os.chdir(ref_dir)
    pdbs = glob.glob("*")
    os.chdir(mydir)
    return pdbs

def compare_topologies(refdir, testdir, verbose):
    mycwd = os.getcwd()
    if os.path.isdir(refdir):
        os.chdir(refdir)
        reffiles = glob.glob("*")
        os.chdir(mycwd)
    ndifftot = 0
    for rf in reffiles:
        reffile  = refdir  + "/" + rf
        testfile = testdir + "/" + rf
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
                print("There were %d differences between reference file %s and test file" % (ndiff, rf) )
                ndifftot += ndiff
    return ndifftot

def run_gromacs(pdb):
    # Implement running a simulation and running gmxcheck on the edr file.
    return True
    
def run_one_test(pdbname, test_dir, ref_dir, verbose):
    tmpdir    = test_dir + "/" + pdbname
    os.makedirs(tmpdir, exist_ok=True)
    mycwd     = os.getcwd()
    error_msg = ("Could not download and/or process data for %s" % pdbname)
    try:
        os.chdir(tmpdir)
        os.system("%s/nmr2gmx.py -n %s" % (mycwd, pdbname))
        os.chdir(mycwd)
    except:
        print(error_msg)
        return
    if os.path.exists(tmpdir):
        myrefdir = ref_dir + "/" + pdb
        ndiff    = compare_topologies(myrefdir, tmpdir, verbose)
        os.chdir(tmpdir)
        gromacs_ok = run_gromacs(pdb)
        os.chdir(mycwd)
        if ndiff == 0 and gromacs_ok:
            print("%s - Passed" % pdbname)
            shutil.rmtree(tmpdir)
        else:
            print("%s - %d file errors, gromacs: %r" % ( pdbname, ndiff, gromacs_ok  ) )
            exit(1)
    else:
        print(error_msg)

# Main part of script
mycwd    = os.getcwd()
test_dir = mycwd + "/tests"
ref_dir  = mycwd + "/refdata"
pdbs = get_pdb_list(ref_dir)
for pdb in pdbs:
    run_one_test(pdb, test_dir, ref_dir, False)
