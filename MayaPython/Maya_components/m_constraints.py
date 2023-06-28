"""
m_select
Tools relating to the constraints systems in maya
Auther: Julian Beiboer
"""

import pymel.core
import os
import tempfile
import maya.cmds
import logging

import logging
logging.basicConfig()
logger = logging.getLogger('m_joints')
logger.setLevel(logging.DEBUG)


def constraint_selection_to_last():
    sel = pymel.core.selected()
    last = sel.pop()

    for s in sel:
        pymel.core.parentConstraint(last, s, mo=1, )
