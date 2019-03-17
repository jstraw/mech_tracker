#!/usr/bin/env python3

import os.path
import argparse
import cmd2
import json
import readline
import math

import builder

def lookup_mech(mech):
    mtf = mech.replace('-','').lower()
    if os.path.isfile('mechs/{}.mtf'.format(mtf)):
        return 'mechs/{}.mtf'.format(mtf)
    else:
        return None

class Mech(builder.BattleMech):
    def __init__(self, identifier, mtf):
        self.identifier = identifier
        super().__init__()
        self.mtf_load(mtf)

class MechTracker(cmd2.Cmd):
    intro = "Welcome to Mech Tracker! - Setting up Battle!"
    prompt = '(battle) '
    file = None

    def __init__(self):
        self.hero = {'name': '',
                     'units': []}
        self.opfor = {'name': '',
                      'units': []}
        self.sides = {'hero': self.hero, 'opfor': self.opfor}
        self.prompt = "({} vs {}) ".format(self.hero['name'], self.opfor['name'])
        super().__init__()

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
            print("NotImplemented")
            return true
        mtf = lookup_mech(args.mech)
        if mtf is None:
            print("Can't Find Mech {}".format(args.mech))
            return
        side = self.sides[args.side]['units'].append(Mech(args.identifier, mtf))

    def do_show(self, args):
        print('Heroes: {}'.format(self.hero['name']))
        for x in self.hero['units']:
            jfull = x.json()
            j = jfull[list(jfull)[0]]
            print("  Hero: {}".format(x.identifier))
            print("  {} ({})".format(j['name'], j['designator']))
            print("  Weight: {}, Move: {}/{}/{}".format(
                    j['weight'],
                    j['walk'],
                    int(round(j['walk'] * 1.5, 0)),
                    j['jump']
            ))
            print("  Armor:")
            for l in [y for y in x.locations if 'Rear' not in y]:
                print("    {}: {}/{} ({}/{})".format(l,
                    (j['armor'][l] - j['damage'][l]), j['armor'][l],
                    (j['internal'][l] - j['internal_damage'][l]), j['internal'][l]
                ))
            for l in [y for y in x.locations if 'Rear' in y]:
                print("    {}: {}/{}".format(l,
                    (j['armor'][l] - j['damage'][l]), j['armor'][l]
                ))
        print('\nOpFor: {}'.format(self.opfor['name']))
        for x in self.opfor['units']:
            jfull = x.json()
            j = jfull[list(jfull)[0]]
            print("  Hero: {}".format(x.identifier))
            print("  {} ({})".format(j['name'], j['designator']))
            print("  Weight: {}, Move: {}/{}/{}".format(
                    j['weight'],
                    j['walk'],
                    int(round(j['walk'] * 1.5, 0)),
                    j['jump']
            ))
            print("  Armor:")
            for l in [y for y in x.locations if 'Rear' not in y]:
                print("    {}: {}/{} ({}/{})".format(l,
                    (j['armor'][l] - j['damage'][l]), j['armor'][l],
                    (j['internal'][l] - j['internal_damage'][l]), j['internal'][l]
                ))
            for l in [y for y in x.locations if 'Rear' in y]:
                print("    {}: {}/{}".format(l,
                    (j['armor'][l] - j['damage'][l]), j['armor'][l]
                ))




if __name__ == '__main__':
    t = MechTracker()
    t.cmdloop()
