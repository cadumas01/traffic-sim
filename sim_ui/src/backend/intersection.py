
# intersection between way segments, based on a single node
class Intersection:
    def __init__(self, noderef, way_segment_refs):
        self.ref = noderef
        self.way_segment_refs = way_segment_refs # list of way segments attached to this intersection

    def __str__(self):
        return f"Intersection: ref = {self.ref} , {len(self.way_segment_refs)} way segments"