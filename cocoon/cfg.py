"""
Config file.
Variable can be modified during runtime.
"""

colorspaces_use_derived_transformation_matrices = True
"""
Compute the conversion matrice from the primaries and whitepoint, instead of using the
one describe in the colorspace specs.

This offer more precision at the cost of not following the spec.

Require a restart of the intepreter.

References:
    - [1] https://github.com/colour-science/colour/discussions/1116#discussioncomment-5208706
    - [2] https://colour.readthedocs.io/en/develop/generated/colour.RGB_Colourspace.html#colour.RGB_Colourspace
"""
