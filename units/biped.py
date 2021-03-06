from . import Unit

class Biped(Unit):
    unit_type = "biped battlemech"
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
        for location in [x for x in self.locations if self.no_internal not in x]:
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
