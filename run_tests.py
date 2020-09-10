#!/usr/bin/env python3
#
#   Copyright 2020 David van der Spoel
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import os, shutil, difflib, glob, argparse
from nmr2gmx import find_gmx

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

def run_gromacs(pdb, gmx, verbose):
    # Implement running a simulation and running gmxcheck on the edr file.
    # Make the box large enough
    redirect = ""
    if not verbose:
        redirect = ">& koko"
    outgro = "out.gro"
    os.system(gmx + (" editconf -f %s.gro -o %s -d 1  %s" % (pdb, outgro, redirect )))
    if not os.path.exists(outgro):
        return "editconf"

    #  Run the gromacs preprocessor
    mdp   = "../../MDP/em.mdp"
    emtpr = pdb + "_em.tpr"
    os.system(gmx + (" grompp -p %s.top -c %s -o %s -f %s  %s" % (pdb, outgro, emtpr, mdp, redirect )))
    if not os.path.exists(emtpr):
        return "grompp"

    # Do an energy minimization
    confout = ( "%s_confout.gro" % pdb )
    os.system(gmx + (" mdrun -s %s -g %s -e %s -c %s %s" % (  emtpr, pdb, pdb, confout, redirect )))
    if not os.path.exists(confout):
        return "mdrun"

    # Compare the structure before and after
    fitpdb = pdb + "_fit.pdb"
    fitlog = pdb + "_fit.log"
    # First make another tpr file in order to have correct masses
    outtpr = pdb + "_confout.tpr"
    os.system(gmx + (" grompp -f %s -p %s -c %s -o %s %s" % ( mdp, pdb, confout, outtpr, redirect )))
    if not os.path.exists(outtpr):
        return "grompp 2"
    os.system("echo 0 0 | %s confrms -f1 %s -f2 %s -o %s >& %s" % ( gmx, emtpr, outtpr, fitpdb, fitlog ))
    
    if not os.path.exists(fitlog):
        return "confrms"
    rmsd = None
    with open(fitlog, "r") as inf:
        for line in  inf:
            if line.find("Root mean square deviation") >= 0:
                rmsd =  float(line.split()[8])
    if not rmsd:
        return "RMSD"
    # Compare RMSD before and after energy minization to 0.02 nm. 
    if rmsd > 0.02:
        print("Structure deviation after minimization %g" % rmsd)
        return "structure"
    return ""
    
def run_one_test(pdbname, gmx,  test_dir, ref_dir, verbose):
    tmpdir    = test_dir + "/" + pdbname
    os.makedirs(tmpdir, exist_ok=True)
    mycwd     = os.getcwd()
    error_msg = ("Could not download and/or process data for %s" % pdbname)
    try:
        os.chdir(tmpdir)
        command = ("%s/nmr2gmx.py -n %s" % (mycwd, pdbname))
        if verbose:
            command += " -v"
        return_value = os.WEXITSTATUS(os.system(command))
        os.chdir(mycwd)
    except:
        print(error_msg)
        return
    if os.path.exists(tmpdir):
        ndiff      = 0
        gromacs_ok = True
        if return_value == 0:
            myrefdir = ref_dir + "/" + pdbname
            ndiff    = compare_topologies(myrefdir, tmpdir, verbose)
            if gmx:
                os.chdir(tmpdir)
                gromacs_ok = run_gromacs(pdbname, gmx, verbose)
                os.chdir(mycwd)
        if return_value == 0 and ndiff == 0 and len(gromacs_ok) == 0:
            print("%s - Passed" % pdbname)
#            shutil.rmtree(tmpdir)
        else:
            print("%s - Failed. %d file errors, gromacs: '%s'" % ( pdbname, ndiff, gromacs_ok  ) )
            print("Check output in %s" % tmpdir)
            
    else:
        print(error_msg)

def runArgumentParser():
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--protein", help = "Run test for 4-symbol protein databank identifier. The files corresponding to this pdb ID will be downloaded. and output compared to pre-existing output.",
                        type=str)
    parser.add_argument("-l", "--list", help="List the PDB files in the reference data set", action="store_true")
    parser.add_argument("-v", "--verbose", help="Print information as we go", action="store_true")

    return parser.parse_args()

#========================================
# MAIN
if __name__ == "__main__":
    args = runArgumentParser()

    mycwd    = os.getcwd()
    test_dir = mycwd + "/tests"
    ref_dir  = mycwd + "/refdata"
    pdbs = get_pdb_list(ref_dir)
    if args.list:
        print("The following PDB files are in the reference data set:")
        string = None
        for i in range(len(pdbs)):
            if i % 15 == 0:
                if string:
                    print(string)
                string = ""
            string += " " + pdbs[i][:-1]
        if len(string) > 0:
            print(string)
    else:
        gmx = find_gmx(False)
        if not gmx:
            print("Cannot run GROMACS, please add it to your search path")
        if args.protein and args.protein in pdbs:
            run_one_test(args.protein, gmx, test_dir, ref_dir, args.verbose)
        else:
            for pdb in pdbs:
                run_one_test(pdb, gmx, test_dir, ref_dir, args.verbose)
