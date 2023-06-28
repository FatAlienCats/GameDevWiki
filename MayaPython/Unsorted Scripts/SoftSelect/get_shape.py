def get_points(self, data):
    """!@Brief Update shape point.
    @type data: dict
    @rtype: OpenMaya.MPointArray
    """
    data_points = data.get('points')
    if not data_points:
        raise RuntimeError('Invalid shape data.')

    output_points = OpenMaya.MPointArray(len(data_points), OpenMaya.MPoint())
    for i in range(len(data_points)):
        point = OpenMaya.MPoint(data_points[i][0], data_points[i][1], data_points[i][2])
        output_points.set(self.__orient_point(point) * self._scale_factor, i)

    return output_points

def build_curve(data, parent):
    """!@Brief Build NurbsCurve shape.
    @type data: dict
    @type parent: OpenMaya.MObject
    @rtype: OpenMaya.MObject
    """
    points = get_points(data)

    a_knots = data.get('knots')
    if a_knots is not None:
        mda_knots = OpenMaya.MDoubleArray(len(a_knots), 0.0)
        for i in range(len(a_knots)):
            mda_knots.set(a_knots[i], i)
    else:
        mda_knots = OpenMaya.MDoubleArray(points.length(), 0.0)
        for i in range(points.length()):
            mda_knots.set(float(i), i)

    shape = OpenMaya.MFnNurbsCurve().create(points, mda_knots, data.get('degree', 1),
                                            data.get('form', 1), data.get('curve2D', False),
                                            data.get('rational', True), parent)

    return shape