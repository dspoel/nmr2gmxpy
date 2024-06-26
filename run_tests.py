#!/usr/bin/env python3
#
#   Copyright 2020-2024 David van der Spoel
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
from nmr2gmxpy_lib.Atom_names import ForceField

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
    nfail    = 0
    for rf in reffiles:
        reffile  = refdir  + "/" + rf
        testfile = testdir + "/" + rf
        if not os.path.exists(testfile):
            print("Failed to create %s" % testfile)
            nfail += 1
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
    return ndifftot+nfail

def run_gromacs(pdb, gmx, verbose, tolerance):
    # Implement running a simulation and running gmxcheck on the edr file.
    # Make the box large enough
    redirect = ""
    if not verbose:
        redirect = ">& koko"
    outgro = "out.gro"
    os.system(gmx + (" editconf -f %s.gro -o %s -box 10 10 10 -center 5 5 5 %s" % (pdb, outgro, redirect )))
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
    os.system(gmx + (" mdrun -nt 1 -s %s -g %s -e %s -c %s %s" % (  emtpr, pdb, pdb, confout, redirect )))
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
                if rmsd == 0.0:
                    rmsd = 1e-12
    if not rmsd:
        return "RMSD"
    # Compare RMSD before and after energy minization. The structures
    # should be within a user given tolerance (default 0.02 nm).
    if rmsd > tolerance:
        print("Structure deviation after minimization %g" % rmsd)
        return "structure"
    return ""
    
def run_one_test(pdbname, force_field, gmx,  test_dir, ref_dir, verbose, tolerance):
    tmpdir    = test_dir + "/" + pdbname
    os.makedirs(tmpdir, exist_ok=True)
    mycwd     = os.getcwd()
    error_msg = ("Could not download and/or process data for %s" % pdbname)
    try:
        os.chdir(tmpdir)
        command = ("%s/nmr2gmx.py -n %s -ff %s" % ( mycwd, pdbname, force_field ))
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
                gromacs_ok = run_gromacs(pdbname, gmx, verbose, tolerance)
                os.chdir(mycwd)
        if return_value == 0 and ndiff == 0 and len(gromacs_ok) == 0:
            print("%s - Passed" % pdbname)
            shutil.rmtree(tmpdir)
        else:
            print("%s - Failed. %d file errors, gromacs: '%s'" % ( pdbname, ndiff, gromacs_ok  ) )
            print("Check output in %s" % tmpdir)
            
    else:
        print(error_msg)

def runArgumentParser():
    parser = argparse.ArgumentParser(description="""
    Run tests on a number of protein to verify that the previous results
    are reproducible. Amber will not work due to the requirement of manually
    editing terminal protein residues in the input pdb file.
    Some tests are disabled for a similar reason with charmm27 as well.
    """)
    parser.add_argument("-n", "--protein", help = "Run test for 4-symbol protein databank identifier. The files corresponding to this pdb ID will be downloaded. and output compared to pre-existing output.",
                        type=str)
    FORCE_FIELD = "charmm27"
    parser.add_argument("-ff", "--force_field", help="Force field to use. See help text of nmr2gmx.py.", default=FORCE_FIELD)
    parser.add_argument("-l", "--list", help="List the PDB files in the reference data set", action="store_true")
    parser.add_argument("-v", "--verbose", help="Print information as we go", action="store_true")
    deftoler = 0.02
    parser.add_argument("-tol", "--tolerance", help="Max RMSD between conformations before and after minimization to pass the test.", type=float, default=deftoler)

    return parser.parse_args()

#========================================
# MAIN
if __name__ == "__main__":
    args = runArgumentParser()

    ff       = ForceField.getFF(args.force_field)
    mycwd    = os.getcwd()
    test_dir = mycwd + "/tests"
    ref_dir  = mycwd + "/refdata/"
    if ff == ForceField.Amber:
        ref_dir += "/Amber"
    elif ff == ForceField.Charmm:
        ref_dir += "/Charmm"
    # These ones are disabled due to problems generating a topology in GROMACS
    # which makes it impossible to test the functioning of this script.
    disabled = [ "2KJF", "2N10" ]
    pdbs = get_pdb_list(ref_dir)
    for d in disabled:
        if d in pdbs:
            pdbs.remove(d)
            print("Pdb id %s is disabled right now" % d)
    if args.list:
        print("The following PDB files are in the reference data set:")
        string = None
        for i in range(len(pdbs)):
            if i % 15 == 0:
                if string:
                    print(string)
                string = ""
            string += " " + pdbs[i]
        if len(string) > 0:
            print(string)
    else:
        gmx = find_gmx(False)
        if not gmx:
            print("Cannot run GROMACS, please add it to your search path")
        if args.protein:
           #if args.protein in pdbs:
            run_one_test(args.protein, args.force_field, gmx, test_dir, ref_dir, args.verbose, args.tolerance)
           #else:
            #   print("No such system %s in the test set."  % args.protein)
        else:
            for pdb in pdbs:
                run_one_test(pdb, args.force_field, gmx, test_dir, ref_dir, args.verbose, args.tolerance)

