#=========================================================================
# ProcBase_branch_test.py
#=========================================================================
# It is as simple as inheriting from FL tests and change the ProcType.

from processor.ProcBase import ProcBase
from processor.test.ProcFL_branch_test import Tests as ProcFL_branch_TestsBaseClass

#-------------------------------------------------------------------------
# Tests
#-------------------------------------------------------------------------

class Tests( ProcFL_branch_TestsBaseClass ):

  @classmethod
  def setup_class( cls ):
    cls.ProcType = ProcBase

