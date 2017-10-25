# Copyright 2013 The Servo Project Developers. See the COPYRIGHT
# file at the top-level directory of this distribution.
#
# Licensed under the Apache License, Version 2.0 <LICENSE-APACHE or
# http://www.apache.org/licenses/LICENSE-2.0> or the MIT license
# <LICENSE-MIT or http://opensource.org/licenses/MIT>, at your
# option. This file may not be copied, modified, or distributed
# except according to those terms.

import fileinput
import re
import subprocess
import sys


def mutate_line(file_name, line_number):
    lines = open(file_name, 'r').readlines()
    lines[line_number - 1] = re.sub(r'\s&&\s', ' || ', lines[line_number - 1])
    out = open(file_name, 'w')
    out.writelines(lines)
    out.close()


def mutation_test(file_name, tests):
    lineNumbers = []
    for line in fileinput.input(file_name):
        if re.search(r'\s&&\s', line):
            lineNumbers.append(fileinput.lineno())

    for lineToMutate in lineNumbers:
        print "Mutating {0} at line {1}".format(file_name, lineToMutate)
        mutate_line(file_name, lineToMutate)
        print "compling mutant {0}-{1}".format(file_name, lineToMutate)
        sys.stdout.flush()
        subprocess.call('python mach build --release', shell=True)
        print "running tests for mutant {0}-{1}".format(file_name, lineToMutate)
        sys.stdout.flush()
        for test in tests:
            testStatus = subprocess.call("python mach test-wpt {0} --release".format(test.encode('utf-8')), shell=True)
            if testStatus != 0:
                print('Failed in while running `python mach test-wpt {0} --release`'.format(test.encode('utf-8')))
                print "mutated file {0} diff".format(file_name)
                sys.stdout.flush()
                subprocess.call('git --no-pager diff {0}'.format(file_name), shell=True)
        print "reverting mutant {0}-{1}".format(file_name, lineToMutate)
        sys.stdout.flush()
        subprocess.call('git checkout {0}'.format(file_name), shell=True)
