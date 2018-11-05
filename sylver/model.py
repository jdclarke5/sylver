"""
Defines a object model for interaction with mongo
"""

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

class Position(MongoModel):
    # The following can all be calculated from the generators
    generators = ListField(IntegerField(), primary_key=True)
    frobenius = IntegerField()
    is_irreducible = BooleanField()
    irreducible_type = CharField()
    multiplicity = IntegerField()
    genus = IntegerField()
    gaps = ListField(IntegerField())
    # Possible others:
    # antisymm_fails = ListField(IntegerField())
    # coordinates = ListField(IntegerField())
    # special_gaps = ListField(IntegerField())
    # lonely_gaps = ListField(IntegerField())
    # ender_gaps = ListField(IntegerField())

    winner = CharField()

    class Child(EmbeddedMongoModel):
        generators = ReferenceField(Position)
        gap = IntegerField()
    children = EmbeddedDocumentListField(Child())

