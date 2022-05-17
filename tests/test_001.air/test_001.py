# -*- encoding=utf8 -*-
__author__ = "Isaev Rustam"
__title__ = "Device wake"
__desc__ = "Description test"

from airtest.core.api import *

auto_setup(__file__)

print("start test_001")
wake()
print("end test_001")
