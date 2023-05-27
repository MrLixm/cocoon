__all__ = (
    "ChromaticAdaptationTransform",
    "DEFAULT_CAT",
)

import enum
import logging

logger = logging.getLogger(__name__)


class ChromaticAdaptationTransform(enum.Enum):
    # values can only be ones supported by ``colour``
    # >>> print("\n".join(colour.CHROMATIC_ADAPTATION_TRANSFORMS))
    bianco_2010 = "Bianco 2010"
    bianco_pc_2010 = "Bianco PC 2010"
    bradford = "Bradford"
    CAT02_Brill = "CAT02 Brill 2008"
    CAT02 = "CAT02"
    CAT16 = "CAT16"
    CMCCAT2000 = "CMCCAT2000"
    CMCCAT97 = "CMCCAT97"
    fairchild = "Fairchild"
    sharp = "Sharp"
    von_kries = "Von Kries"
    XYZ_scaling = "XYZ Scaling"

    @classmethod
    def get_default(cls):
        return DEFAULT_CAT


DEFAULT_CAT: ChromaticAdaptationTransform = ChromaticAdaptationTransform.bradford
