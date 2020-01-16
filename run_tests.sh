#!/bin/bash

# This awkward invocation is to get around the case where no tests are
# found, which has exit code of 5 in pytest

py.test --nbval notebooks; ret=$?; [ $ret = 5 ] && exit 0 || exit $ret
