# cocoon

Python **co**lorspace **co(o)n**version library.

Mostly wrap [colour](https://github.com/colour-science/colour) to provide a
different interface.

> **Warning** cocoon is a personal experimental project, shared without any
> guarantee. It is not aimed to be widely used and maintained out of my personal scope.
> API can break at any time.

# What it is.

Cocoon allow to use, interract and create RGB colorspaces in the context of
building python software.

Cocoon vastly depends on [colour](https://github.com/colour-science/colour)
and wrap its existing API to provide a different way to interract with colorspaces.

## difference with colors

- Monolithic RGB_Colorspace class split in multiple classes (called ColorspaceComponent) :
  - `Whitepoint` class
  - `Gamut` class
  - `TransferFunctions` class
  - `RgbColorspace` which regroup the above
- Immutability for all ColorspaceComponents
  - you can't edit attributes of an instance once created
  - methods to edit a specirfic attribute by returning a new instance are provided
- Hashing and equality for all ColorspaceComponents
- Conversion of ColorspaceComponents instances to dict objects
- More "metadata" about RgbColorspace stored.
  - `description` and `categories`
  - mostly useful in the GUI context of listing instances
- mechanism to create "linear" variant of any colorspace
- retrieving a colorspace is done through the `get_colorspace` function instead
of using a global dict object.
- retrieving a colorspace by name is case-sensitive, though aliases and a 
"simplified representation of the name" are provided.

the cooon specific `RgbColorspace` class can be converted to and from a `colour.RGB_Colorspace` instance.

## issues

- an update on the colour library require an update on the cocoon side (example: new colorspace added)
- cocoon `RgbColorspace` class design allow multiple attributes to be `None` which usually
implied more code to interract with it (conditional checks).
- increased complexity

# demo

Basic conversion

```python
import numpy
import cocoon

some_image = numpy.array()
image_colorspace = cocoon.get_colorspace("sRGB", force_linear=True)
# linear sRGB is enough common it has a constant
image_colorspace = cocoon.sRGB_LINEAR_COLORSPACE
target_colorspace = cocoon.get_colorspace("ACEScg")

converted_image = cocoon.colorspace_to_colorspace(
  some_image,
  source_colorspace=image_colorspace,
  target_colorspace=target_colorspace,
  chromatic_adaptation_transform=cocoon.ChromaticAdaptationTransform.get_default()
)
```

Creating a frankestein sRGB colorspace with ACES whitepoint.

```python
import cocoon

acescg_colorspace = cocoon.get_colorspace("ACEScg")

new_colorspace = cocoon.sRGB_COLORSPACE.with_whitepoint(
    new_whitepoint=acescg_colorspace.whitepoint,
    matrix_to_XYZ=None,
    matrix_from_XYZ=None,
)
# recompute the matrices as the whitepoint changed
new_colorspace = new_colorspace.with_derived_matrices()
```


# roadmap

- improve package structure
- should `colour` conversion methods be moved outside classes, just simpel conversion
functions ?
- change `to_dict` to `serialize` and create its inverse `from_serialized`
- build a dataset of whitepoints