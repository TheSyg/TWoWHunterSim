# slots

class Equipment:
    def __init__(self, name, attack_power=0, agility=0, crit_chance=0, haste=0, hit=0, t1=False, ZG_set=False, RAQ_set=False, t2=False, TAQ_set=False, t3=False):
        self.name = name
        self.attack_power = attack_power
        self.agility = agility
        self.crit_chance = crit_chance
        self.haste = haste
        self.hit = hit
        self.t1 = t1
        self.ZG_set = ZG_set
        self.RAQ_set = RAQ_set
        self.t2 = t2
        self.TAQ_set = TAQ_set
        self.t3 = t3

    def get_stats(self):
        return {
            'attack_power': self.attack_power,
            'agility': self.agility,
            'crit_chance': self.crit_chance,
            'haste': self.haste,
            'hit': self.hit,
            't1': self.t1,
            'ZG_set': self.ZG_set,
            'RAQ_set': self.RAQ_set,
            't2': self.t2,
            'TAQ_set': self.TAQ_set,
            't3': self.t3
        }

class head(Equipment):
    pass

class neck(Equipment):
    pass

class shoulder(Equipment):
    pass

class back(Equipment):
    pass

class chest(Equipment): 
    pass

class hand(Equipment):
    pass

class wrist(Equipment):
    pass

class waist(Equipment):
    pass

class legs(Equipment):
    pass

class feet(Equipment):
    pass

class finger(Equipment):
    pass

class trinket(Equipment):
    pass

class melee(Equipment):
    pass

class ranged(Equipment):
    pass

class Ammo(Equipment):
    def __init__(self, name, ammo_dps):
        super().__init__(name)
        self.ammo_dps = ammo_dps

    def get_stats(self):
        stats = super().get_stats()
        stats['ammo_dps'] = self.ammo_dps
        return stats

