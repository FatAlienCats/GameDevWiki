"""
m_namespace
Tools relating to the namespace manipulation
Auther: Julian Beiboer
"""
import pymel.core
import os
import tempfile
import maya.cmds
import logging

import logging
logging.basicConfig()
logger = logging.getLogger('m_namespace')
logger.setLevel(logging.DEBUG)



def remove_namespace(namespace, mergeWithParent=False, mergeWithRoot=False):
    if maya.cmds.namespace(exists=namespace):
        maya.cmds.namespace(removeNamespace=namespace, mergeNamespaceWithParent=mergeWithParent,
                            mergeNamespaceWithRoot=mergeWithRoot)
        logger.info("Removing Namespace: " + namespace)
    else:
        logger.warning(namespace + " doesn't exist")




