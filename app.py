import random

class Hunter:
    def __init__(self, stats, num_simulations):
        self.attack_power = stats["attack_power"]
        self.crit_chance = stats["crit_chance"] / 100 
        self.hit_chance = stats["hit"] / 100  
        
        self.min_damage = stats["min_damage"]
        self.max_damage = stats["max_damage"]
        self.weapon_speed = stats["weapon_speed"]
        self.ammo_dps = stats["ammo_dps"]

        self.miss_chance = 0.08 
        self.trueshot_bonus = 50
        self.multi_shot_bonus = 172

        self.rapid_fire_cd = 300
        self.rapid_fire_duration = 15
        self.rapid_fire_active = False
        self.rapid_fire_time_left = 0
        self.rapid_fire_last_used = -self.rapid_fire_cd

        self.multi_shot_cd = 10
        self.multi_shot_last_used = -self.multi_shot_cd
        self.trueshot_cast_time = 1.0
        self.time_until_next_auto = 0
        self.trueshot_used = False

        self.num_simulations = num_simulations

    def calculate_damage_range(self):
        min_range = (((self.min_damage) / self.weapon_speed) + (self.attack_power / 14) + self.ammo_dps) * self.weapon_speed
        max_range = (((self.max_damage) / self.weapon_speed) + (self.attack_power / 14) + self.ammo_dps) * self.weapon_speed
        min_range *= 1.05
        max_range *= 1.05

        return min_range, max_range

    def calculate_shot_damage(self, trueshot=False, multi_shot=False):
        min_range, max_range = self.calculate_damage_range()
        damage = random.uniform(min_range, max_range)

        if trueshot:
            damage += self.trueshot_bonus
        if multi_shot:
            damage += self.multi_shot_bonus

        crit = False
        if random.random() < self.crit_chance:
            damage *= 2.3
            crit = True

        return damage, crit

    def simulate(self, duration):
        total_dps = 0

        for _ in range(self.num_simulations):
            current_time = 0
            total_damage = 0
            bleed_damage = 0

            while current_time < duration:
                delta_time = 0.1  # Intervalos de simulación de 0.1s

                if self.time_until_next_auto <= 0:
                    if random.random() < self.miss_chance - self.hit_chance:
                        damage = 0
                        crit = False
                    else:
                        damage, crit = self.calculate_shot_damage()

                    total_damage += damage

                    # Bleed if crit
                    if crit:
                        bleed_damage += (damage * 0.3) / 8

                    # Extra shot
                    if random.random() < 0.06:
                        extra_damage, _ = self.calculate_shot_damage()
                        total_damage += extra_damage

                    self.time_until_next_auto = self.weapon_speed 

                    if current_time - self.rapid_fire_last_used >= self.rapid_fire_cd:
                        self.rapid_fire_active = True
                        self.rapid_fire_time_left = self.rapid_fire_duration
                        self.weapon_speed /= 1.4
                        self.time_until_next_auto /= 1.4
                        self.rapid_fire_last_used = current_time

                self.time_until_next_auto -= delta_time
                current_time += delta_time

            total_dps += (total_damage + bleed_damage) / duration

        return total_dps / self.num_simulations


stats = {
    "attack_power": 1603,
    "crit_chance": 30.57,    
    "hit": 8,              # cap: 8%
    "min_damage": 585,     
    "max_damage": 701,     
    "weapon_speed": 2.99,   
    "ammo_dps": 17.5         
}

duration = 60  #PW type fight: 120s
num_simulations = 69420  # Recommended to do over 50000 sims

hunter = Hunter(stats, num_simulations)
average_dps = hunter.simulate(duration)
print(f"Avg DPS in {num_simulations} sims: {round(average_dps, 2)}")
