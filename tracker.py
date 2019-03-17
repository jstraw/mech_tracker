#!/usr/bin/env python3

import os.path
import argparse
import cmd2
import json
import readline
import time

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

    def json(self):
        out = super().json()
        out[list(out)[0]]['identifier'] = self.identifier
        return out

class MechTracker(cmd2.Cmd):
    intro = "Welcome to Mech Tracker! - Setting up Battle!"

    def __init__(self):
        self.hero = {'name': '',
                     'units': []}
        self.opfor = {'name': '',
                      'units': []}
        self.sides = {'hero': self.hero, 'opfor': self.opfor}
        self.prompt = "({} vs {}) ".format(self.hero['name'], self.opfor['name'])
        file_base = int(time.time())
        self.file = "{}.replay".format(file_base)
        self.status = "{}.json".format(file_base)
        super().__init__()


    def postcmd(self, stop, line):
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
            print("NotImplemented")
            return true
        mtf = lookup_mech(args.mech)
        if mtf is None:
            print("Can't Find Mech {}".format(args.mech))
            return
        side = self.sides[args.side]['units'].append(Mech(args.identifier, mtf))

    def do_replay(self, args):
        with open(args, 'r') as fd:
            self.cmdqueue.extend(fd.readlines())

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
