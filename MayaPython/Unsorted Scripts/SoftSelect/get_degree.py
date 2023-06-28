from maya import OpenMaya


def normalize_points(points):
        f_max = max([item for sublist in points for item in sublist])
        return [[x[0] / f_max, x[1] / f_max, x[2] / f_max] for x in points]

def get_curve_shape(src, normalize=True):
    """!@Brief Get NurbsCurve shape data.
    @type src: OpenMaya.MObject
    @type normalize: bool
    @rtype: dict
    """
    if isinstance(src, str):
        src = api.get_object(src)
    if not src.hasFn(OpenMaya.MFn.kNurbsCurve):
        raise TypeError('Node must be a mesh not "{0}"'.format(src.apiTypeStr()))

    mfn = OpenMaya.MFnNurbsCurve(src)
    maya_points = OpenMaya.MPointArray()
    mfn.getCVs(maya_points, OpenMaya.MSpace.kObject)
    points = [[maya_points[i].x, maya_points[i].y, maya_points[i].z] for i in range(maya_points.length())]

    knots = OpenMaya.MDoubleArray()
    mfn.getKnots(knots)

    d = collections.OrderedDict()
    d['type'] = 'nursCurve'
    d['points'] = normalize_points(points) if normalize else points
    d['knots'] = [knots[i] for i in range(knots.length())]
    d['form'] = mfn.form()
    d['degree'] = mfn.degree()

    return d