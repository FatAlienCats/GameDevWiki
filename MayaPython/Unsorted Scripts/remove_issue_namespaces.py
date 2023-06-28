import maya.cmds
import logging
logging.basicConfig()
logger = logging.getLogger('m_namespace')
logger.setLevel(logging.DEBUG)


NAMESPACE_REMOVAL = ['ukelele_main:ukulele:', 'electricBass_main:electricBass:',
                     'triangle_main:triangle:', 'tuba_main:tuba:', 'flute_main:flute:']


def main():
    for namespace in NAMESPACE_REMOVAL:
        remove_namespace(namespace, mergeWithParent=True, mergeWithRoot=False)


def remove_namespace(namespace, mergeWithParent=False, mergeWithRoot=False):
    if maya.cmds.namespace(exists=namespace):
        maya.cmds.namespace(removeNamespace=namespace, mergeNamespaceWithParent=mergeWithParent,
                            mergeNamespaceWithRoot=mergeWithRoot)
        logger.info("Removing Namespace: " + namespace)
    else:
        logger.warning("Namespace: " + namespace + " doesn't exist")


if __name__ == "__main__":
    main()
