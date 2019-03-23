#!/usr/bin/env python3

import os.path
import argparse
import json
import readline
import time

import cmd2
import colorama

import units.biped
import units.quad

colorama.init()

def lookup_mech(mech):
    mtf = mech.replace('-','').lower()
    if os.path.isfile('mechs/{}.mtf'.format(mtf)):
        return 'mechs/{}.mtf'.format(mtf)
    else:
        return None


class MechTracker(cmd2.Cmd):
    quiet = True
    intro = "Welcome to Mech Tracker! - Setting up Battle!"
    damage_lookup = {
        "h": "Head",
        "tl": "Left Torso",
        "tr": "Right Torso",
        "tc": "Center Torso",
        "rtl": "Left Torso, Rear",
        "rtr": "Right Torso, Rear",
        "rtc": "Center Torso, Rear",
        "rll": "Left Leg, Rear",
        "rlr": "Right Leg, Rear",
        "fll": "Left Leg, Front",
        "flr": "Right Leg, Front",
        "ar": "Right Arm",
        "al": "Left Arm",
        "lr": "Right Leg",
        "ll": "Left Leg"
    }

    def __init__(self):
        self.hero = {'name': '',
                     'units': []}
        self.opfor = {'name': '',
                      'units': []}
        self.sides = {'hero': self.hero, 'opfor': self.opfor}
        self.mechs.choices = []
        self.prompt = "({} vs {}) ".format(self.hero['name'], self.opfor['name'])
        file_base = int(time.time())
        self.file = "{}.replay".format(file_base)
        self.status = "{}.json".format(file_base)
        super().__init__()

    def find_mechs(self, identifier):
        item = [x for x in self.hero['units'] if x.identifier == identifier]
        if item and len(item) == 1:
            return ('hero', item[0])
        elif item:
            self.perror("Found multiple units")
        item = [x for x in self.opfor['units'] if x.identifier == identifier]
        if item and len(item) == 1:
            return ('opfor', item[0])
        elif item:
            self.perror("Found multiple units")
        return (None, None)

    def postcmd(self, stop, line):
        self.mechs.choices = [x.identifier for x in
                      self.hero['units'] + self.opfor['units']]
        readline.write_history_file(self.file)
        status = {  "battle": {
                        "heroes": {
                            "name": self.hero['name'],
                        },
                        "opfor": {
                            "name": self.opfor['name'],
                        }
                    }}
        status['battle']['heroes']['units'] = [x.json() for x in self.hero['units']]
        status['battle']['opfor']['units'] = [x.json() for x in self.opfor['units']]
        with open(self.status, 'w+') as fd:
            json.dump(status, fd, indent=2)
        return stop

    ap_ident = argparse.ArgumentParser()
    ap_ident.add_argument("hero_id", help="Hero Lance Identity")
    ap_ident.add_argument("opfor_id", help="OpFor Lance Identity")
    @cmd2.with_argparser(ap_ident)
    def do_ident(self, args):
        "Configure the Identity of the 2 sides"
        self.hero['name'] = args.hero_id
        self.opfor['name'] = args.opfor_id
        self.prompt = "({} vs {}) ".format(self.hero['name'], self.opfor['name'])


    ap_config = argparse.ArgumentParser()
    ap_config.add_argument("action", choices=('add', 'del'))
    ap_config.add_argument("side", choices=('hero', 'opfor'),
                           help="Which Side are we adding to?")
    ap_config.add_argument("mech", help="Mech designator (ex GHR-5J)")
    ap_config.add_argument("identifier", help="What do we call this unit?")
    @cmd2.with_argparser(ap_config)
    def do_config(self, args):
        if args.action != 'add':
            self.perror("NotImplemented")
            return true
        mtf = lookup_mech(args.mech)
        self.pfeedback(mtf)
        if mtf is None:
            self.perror("Can't Find Mech {}".format(args.mech))
            return
        with open(mtf, 'r') as fd:
            data = [x.strip() for x in fd.readlines()]
            if "Config:Quad" in data:
                unit_type = units.quad.Quad
            else:
                unit_type = units.biped.Biped
        newmech = unit_type()
        newmech.identifier = args.identifier
        self.pfeedback(newmech)
        newmech.mtf_load(mtf)
        side = self.sides[args.side]['units'].append(newmech)

    def do_replay(self, args):
        with open(args, 'r') as fd:
            self.cmdqueue.extend(fd.readlines())

    def do_show(self, args):
        def show_unit(x):
            jfull = x.json()
            j = jfull[list(jfull)[0]]
            self.poutput("  {} ({})".format(j['name'], j['designator']))
            self.poutput("  Weight: {}, Move: {}/{}/{}".format(
                    j['weight'],
                    j['walk'],
                    int(round(j['walk'] * 1.5, 0)),
                    j['jump']
            ))
            self.poutput("  Armor:")
            for l in [y for y in x.locations if x.no_internal not in y]:
                c = ''
                if j['internal_damage'][l]:
                    c = colorama.Fore.RED
                elif j['damage'][l]:
                    c = colorama.Fore.YELLOW
                self.poutput("    {}: {}/{} ({}/{})".format(l,
                    (j['armor'][l] - j['damage'][l]), j['armor'][l],
                    (j['internal'][l] - j['internal_damage'][l]), j['internal'][l]
                ),color=c)
            for l in [y for y in x.locations if x.no_internal in y]:
                c = ''
                if j['damage'][l]:
                    c = colorama.Fore.YELLOW
                self.poutput("    {}: {}/{}".format(l,
                    (j['armor'][l] - j['damage'][l]), j['armor'][l]
                ))
        self.poutput('Heroes: {}'.format(self.hero['name']))
        for x in self.hero['units']:
            self.poutput("  Hero: {}".format(x.identifier))
            show_unit(x)
        self.poutput('\nOpFor: {}'.format(self.opfor['name']))
        for x in self.opfor['units']:
            self.poutput("  OpFor: {}".format(x.identifier))
            show_unit(x)


    ap_damage = argparse.ArgumentParser()
    mechs = ap_damage.add_argument("mech", choices=[])
    ap_damage.add_argument("target", choices=list(damage_lookup.keys()),
                           help="Where to apply damage?")
    ap_damage.add_argument("damage", type=int, help="Amount of damage to add")
    @cmd2.with_argparser(ap_damage)
    def do_damage(self, args):
        side, mech = self.find_mechs(args.mech)
        t = self.damage_lookup[args.target]
        if args.target[0] == 'r':
            it = self.damage_lookup[args.target[1:]]
        else:
            it = t
        if args.damage > 0:
            mech.damage[t] += args.damage
            diff = mech.damage[t] - mech.armor[t]
            if diff > 0:
                self.poutput("{}Hit Went Internal on {}{}".format(
                    colorama.Fore.WHITE+colorama.Back.RED,
                    t,
                    colorama.Style.RESET_ALL
                    ))
                mech.damage[t] -= diff
                mech.internal_damage[t] += diff
                internal_diff = mech.internal_damage[it] - mech.internal[it]
                if internal_diff > 0:
                    self.poutput("{}DESTROYED {}, Overflow is {}{}".format(
                        colorama.Fore.WHITE+colorama.Back.RED,
                        it,
                        internal_diff,
                        colorama.Style.RESET_ALL
                        ))
                    mech.internal_damage[it] -= internal_diff
        elif args.damage < 0:
            if mech.internal_damage[it] > 0:
                if args.damage + mech.internal_damage[it] >= 0:
                    mech.internal_damage[it] += args.damage
                    return
                d = mech.internal_damage[it] + args.damage
                mech.internal_damage[it] = 0
                mech.damage[t] += d
            else:
                mech.damage[t] += args.damage
                if mech.damage[t] < 0:
                    mech.damage[t] = 0






if __name__ == '__main__':
    t = MechTracker()
    t.cmdloop()
