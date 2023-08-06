import time

import numpy

import cocoon
import colour


ARRAY = numpy.full([1080, 1920, 3], [0.1, 0.2, 0.3], dtype=numpy.float32)


def eotf_inverse_sRGB(L):
    L = colour.utilities.array.to_domain_1(L)
    V = numpy.where(
        L <= 0.0031308, L * 12.92, 1.055 * colour.algebra.spow(L, 1 / 2.4) - 0.055
    )
    return colour.utilities.array.as_float(colour.utilities.array.from_range_1(V))


def eotf_sRGB(V):
    V = V
    L = numpy.where(
        V <= eotf_inverse_sRGB(0.0031308),
        V / 12.92,
        colour.algebra.spow((V + 0.055) / 1.055, 2.4),
    )
    return L


def profiling_1():
    result = cocoon.colorspace_to_colorspace(
        ARRAY,
        cocoon.sRGB_COLORSPACE.as_linear_copy(),
        cocoon.sRGB_COLORSPACE,
        cocoon.ChromaticAdaptationTransform.get_default(),
    )


def profiling_2():
    # now test with a lighter version of the transfer function
    result = eotf_sRGB(ARRAY)


if __name__ == "__main__":
    time.sleep(0.25)
    profiling_1()
    time.sleep(0.25)
    profiling_2()
