import json

with open("tables/internals.json") as fp:
    INTERNAL_STRUCTURE = json.load(fp)

class Unit:
    locations = []
    unit_type = "unknown"
    is_lookup = {}
    no_internal = 'Rear'

    def __init__(self):
        internal_locs = [x for x in self.locations if self.no_internal not in x]
        self.armor = { key: 0 for key in self.locations}
        self.damage = { key: 0 for key in self.locations}
        self.internal = { key: 0 for key in internal_locs}
        self.internal_damage = { key: 0 for key in internal_locs}
        self.critials = { key: [] for key in internal_locs}
        self.weight = 0
        self.name = ""
        self.designator = ""
        self.walk = 0
        self.jump = 0
        self.heat = {"number": 0, "type": "Single"}
        self.weapons = { key: [] for key in self.locations}
        self.identifier = ""

    def set_armor(self):
        print("Set Armor Values for {}".format(self.name))
        for x in self.locations:
            self.armor[x] = int(raw_input("{}: ".format()))

    def set_weight(self, weight=None):
        if weight:
            self.weight = int(weight)
        else:
            self.weight = int(raw_input("Weight for {}: ".format(self.name)))
        for location in [x for x in self.locations if self.no_internal not in x]:
            self.internal[location] = INTERNAL_STRUCTURE[self.unit_type.split()[-1]] \
            [str(self.weight)][self.is_lookup[location]]

    def __repr__(self):
        return "<Unit {}: {}, Weight: {}>".format(self.unit_type, self.name, self.weight)

    def json(self):
        out = {self.unit_type: {
            "name": self.name,
            "designator": self.designator,
            "call_sign": self.identifier,
            "weight": self.weight,
            "walk": self.walk,
            "jump": self.jump,
            "weapons": self.weapons,
            "armor": self.armor,
            "damage": self.damage,
            "internal": self.internal,
            "internal_damage": self.internal_damage,
            "critials": self.critials
        }}
        return out

    def jsonstr(self):
        return json.dumps(self.json(), indent=2)

    def mtf_load(self, file_name):
        pass
