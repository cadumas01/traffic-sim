
# intersection between way segments, based on a single node
class Intersection:
    def __init__(self, noderef, outgoing_way_segment_refs, incoming_way_segment_refs):
        self.ref = noderef
        self.outgoing_way_segment_refs = outgoing_way_segment_refs # list of way segments leaving this intersection
        self.incoming_way_segment_refs = incoming_way_segment_refs # list of way segments incoming to intersection

        # dictionary indexed by destination node where each value is the next way_segment necessary on the journey
        # May only need the 
        self.next_way_segment = {} 

    def __str__(self):
        return f"Intersection: ref = {self.ref}, {len(self.outgoing_way_segment_refs)} outgoing way segments, {len(self.incoming_way_segment_refs)} incoming way segments"