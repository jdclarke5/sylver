"""
Defines a object model for interaction with mongo
""""

from pymodm import (
    EmbeddedMongoModel,
    MongoModel, 
)
from pymodm.fields import (
    BooleanField,
    CharField,
    EmbeddedDocumentListField,
    IntegerField,
    ListField,
    ReferenceField,
)

class Semigroup(MongoModel):
    generators = ListField(IntegerField())
    multiplicity = IntegerField()
    gaps = ListField(IntegerField())
    frobenius = IntegerField()
    genus = IntegerField()
    is_irreducible = BooleanField()
    # '', 's', or 'p'
    irreducible_type = CharField()
    # Possible others:
    # antisymm_fails = ListField(IntegerField())
    # coordinates = ListField(IntegerField())
    # special_gaps = ListField(IntegerField())
    # lonely_gaps = ListField(IntegerField())
    # ender_gaps = ListField(IntegerField())
    # '', 'N', or 'P'
    winner = CharField()
    moves = EmbeddedDocumentListField(
        EmbeddedMongoModel(
            gap = IntegerField(),
            semigroup = ReferenceField(Semigroup)
        )
    )