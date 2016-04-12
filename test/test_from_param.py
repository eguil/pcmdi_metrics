import unittest
import shlex
import subprocess
import os
import sys
import glob
import difflib
import numpy


class TestFromParam(unittest.TestCase):

    def __init__(self, parameter_file=None, good_files=[]):
        super(TestFromParam, self).__init__("test_from_parameter_file")
        self.param = parameter_file
        self.good_files = good_files

    def setUp(self):
        subprocess.call(
            shlex.split(
                "pcmdi_metrics_driver.py -p %s" %
                self.param))
        pass

    def test_from_parameter_file(self):
        # Ok at that point we we can start testing things
        pth, fnm = os.path.split(self.param)
        if pth != "":
            sys.path.append(pth)
        if fnm.lower()[-3:] == ".py":
            fnm = fnm[:-3]
        parameters = ""  # so flake8 doesn't complain
        exec("import %s as parameters" % fnm)
        # Ok now let's figure out where the results have been dumped
        pthout = os.path.join(
            parameters.metrics_output_path,
            parameters.case_id,
            "*.json")
        files = glob.glob(pthout)
        for fnm in files:
            nm = os.path.basename(fnm)
            # Ok now we are trying to find the same file
            if self.good_files == []:
                self.good_files = glob.glob(
                    os.path.dirname(__file__) +
                    "/pcmdi/%s/*.json" %
                    parameters.case_id)
            ok = True
            if len(self.good_files) == 0:
                ok = False
                print "could not find good files",\
                    __file__, os.path.dirname(__file__) +\
                    "/pcmdi/%s/*.json" % parameters.case_id
            for gnm in self.good_files:
                if os.path.basename(gnm) == nm:
                    print "comparing:", fnm, gnm
                    u = difflib.unified_diff(
                        open(gnm).readlines(),
                        open(fnm).readlines())
                    prev = None
                    for l in u:
                        if l[:2] == "+ ":
                            if l.find("metrics_git_sha1") > -1:
                                continue
                            if l.find("uvcdat_version") > -1:
                                continue
                            else:
                                good = float(l.split()[-1][1:-2])
                                bad = float(prev.split()[-1][1:-2])
                                if not numpy.allclose(good,bad,1.E-3):
                                    print "Failing line:", prev.strip(),"instead of",good
                                    ok = False
                        prev = l
            self.assertTrue(ok)
        # shutil.rmtree(os.path.join(parameters.metrics_output_path,parameters.case_id))
