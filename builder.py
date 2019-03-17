import json

with open("tables/internals.json") as fp:
    INTERNAL_STRUCTURE = json.load(fp)

class Unit:
    locations = []
    unit_type = "unknown"
    is_lookup = {}

    def __init__(self):
        internal_locs = [x for x in self.locations if 'Rear' not in x]
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

    def set_armor(self):
        print("Set Armor Values for {}".format(self.name))
        for x in self.locations:
            self.armor[x] = int(raw_input("{}: ".format()))

    def set_weight(self, weight=None):
        if weight:
            self.weight = int(weight)
        else:
            self.weight = int(raw_input("Weight for {}: ".format(self.name)))
        for location in [x for x in self.locations if 'Rear' not in x]:
            self.internal[location] = INTERNAL_STRUCTURE[self.unit_type] \
            [str(self.weight)][self.is_lookup[location]]

    def __repr__(self):
        return "<Unit: {}, Weight: {}>".format(self.name, self.weight)

    def json(self):
        out = {self.unit_type: {
            "name": self.name,
            "designator": self.designator,
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

class BattleMech(Unit):
    unit_type = "battlemech"
    locations = [
        "Head",
        "Left Torso",
        "Right Torso",
        "Center Torso",
        "Right Arm",
        "Left Arm",
        "Right Leg",
        "Left Leg",
        "Left Torso, Rear",
        "Right Torso, Rear",
        "Center Torso, Rear"
    ]
    is_lookup = {
        "Head": "head",
        "Left Torso": "side torso",
        "Right Torso": "side torso",
        "Center Torso": "center torso",
        "Right Arm": "arm",
        "Left Arm": "arm",
        "Right Leg": "leg",
        "Left Leg": "leg"
    }

    location_lookup = {
        "HD Armor": "Head",
        "LT Armor": "Left Torso",
        "RT Armor": "Right Torso",
        "CT Armor": "Center Torso",
        "RA Armor": "Right Arm",
        "LA Armor": "Left Arm",
        "RL Armor": "Right Leg",
        "LL Armor": "Left Leg",
        "RTL Armor": "Left Torso, Rear",
        "RTR Armor": "Right Torso, Rear",
        "RTC Armor": "Center Torso, Rear"
    }

    def __repr__(self):
        return "<BattleMech: {}, Weight: {}>".format(self.name, self.weight)

    def mtf_load(self, file_name):
        with open(file_name, 'r') as mtf:
            lines = mtf.readlines()
        data = [x.strip() for x in lines]
        lo = [x.lower() for x in data]
        keys = {}
        for index, line in enumerate(data):
            if ':' in line:
                key, value = line.split(':')
                keys[key] = value
        self.name = data[1]
        self.designator = data[2]
        self.set_weight(keys['Mass'])
        self.walk = int(keys['Walk MP'])
        self.jump = int(keys['Jump MP'])
        self.heat['number'], self.heat['type'] = keys['Heat Sinks'].split()
        for key, value in self.location_lookup.items():
            self.armor[value] = int(keys[key])
        for location in [x for x in self.locations if 'Rear' not in x]:
            crits = self.critials[location]
            start = False
            for line in data:
                if start and line != "":
                    if '-Empty-' in line:
                        crits.append(None)
                    else:
                        crits.append(line)
                elif start and line == "":
                    break
                if "{}:".format(location) in line:
                    start = True
        # Find weapons
        start = False
        for line in data:
            if start and line != "":
                name, loc = line.split(', ')
                self.weapons[loc].append(name)
            elif start and line == "":
                break
            if "Weapons:" in line:
                start = True

if __name__ == '__main__':
    ghr5j = BattleMech("Grasshopper", "GHR-5J")
    ghr5j.mtf_load("mechs/ghr5j.mtf")
    bnc53 = BattleMech("Banshee", "BNC-3E")
    bnc53.mtf_load("mechs/bnc3e.mtf")
    print(ghr5j.jsonstr())
    print(bnc53.jsonstr())
