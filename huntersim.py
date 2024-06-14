import random

##################
# TWoW Hunter Sim. WIP.
# Discord: syg_
# Feedback is welcomed.
##################

class Hunter:
    def __init__(self, min_damage, max_damage, weapon_speed, attack_speed, ranged_attack_power, scope_bonus, ammo_dps, crit_chance):
        self.min_damage = min_damage
        self.max_damage = max_damage
        self.weapon_speed = weapon_speed
        self.base_attack_speed = attack_speed
        self.attack_speed = attack_speed
        self.ranged_attack_power = ranged_attack_power
        self.scope_bonus = scope_bonus
        self.ammo_dps = ammo_dps
        self.crit_chance = crit_chance / 100
        self.trueshot_bonus = 50
        self.multi_shot_bonus = 172
        self.quick_shots_duration = 12
        self.quick_shots_chance = 0.05
        self.quick_shots_active = False
        self.quick_shots_time_left = 0
        self.rapid_fire_cd = 300  
        self.rapid_fire_duration = 15 
        self.rapid_fire_active = False
        self.rapid_fire_time_left = 0
        self.rapid_fire_last_used = -self.rapid_fire_cd 
        self.multi_shot_cd = 10  
        self.multi_shot_last_used = -self.multi_shot_cd
        self.trueshot_cast_time = 1.0  
        self.time_until_next_auto = attack_speed 
        self.skill_used = False # checks if either multi-shot or trueshot was used

    def calculate_damage_range(self):
        min_range = (((self.min_damage + self.scope_bonus) / self.weapon_speed) + (self.ranged_attack_power / 14) + self.ammo_dps) * self.weapon_speed
        max_range = (((self.max_damage + self.scope_bonus) / self.weapon_speed) + (self.ranged_attack_power / 14) + self.ammo_dps) * self.weapon_speed
        return min_range, max_range

    def calculate_shot_damage(self, trueshot=False, multi_shot=False):
        # AA logic
        min_range, max_range = self.calculate_damage_range()
        damage = random.uniform(min_range, max_range)
        if trueshot:
            damage += self.trueshot_bonus
        if multi_shot:
            damage += self.multi_shot_bonus
        if random.random() < self.crit_chance:
            damage *= 2.3 # Crits!
        return damage

    def apply_quick_shots(self):
        # QS Proc logic
        if random.random() < self.quick_shots_chance:
            print("QS Triggered!")
            if self.quick_shots_active == True:
                # QS already active, refreshes duration
                self.quick_shots_active = True
                self.quick_shots_time_left = self.quick_shots_duration
            else:
                # QS was not active. Buffs Attack Speed, adds duration.
                self.quick_shots_active = True
                self.quick_shots_time_left = self.quick_shots_duration
                self.attack_speed *= 0.7
                self.time_until_next_auto *= 0.7

    def update_quick_shots(self, elapsed_time):
        if self.quick_shots_active:
            self.quick_shots_time_left -= elapsed_time
            if self.quick_shots_time_left <= 0:
                # QS is over
                self.quick_shots_active = False
                self.attack_speed = self.attack_speed / 0.7 # reverts Attack Speed
                self.time_until_next_auto = self.attack_speed

    def apply_rapid_fire(self, current_time):
        # Activates RF
        if current_time - self.rapid_fire_last_used >= self.rapid_fire_cd:
            self.rapid_fire_active = True
            self.rapid_fire_time_left = self.rapid_fire_duration
            self.attack_speed *= 0.6 
            self.time_until_next_auto *= 0.6
            self.rapid_fire_last_used = current_time

    def update_rapid_fire(self, elapsed_time):
        if self.rapid_fire_active:
            self.rapid_fire_time_left -= elapsed_time
            if self.rapid_fire_time_left <= 0:
                # RF is over
                self.rapid_fire_active = False
                self.attack_speed = self.attack_speed / 0.6 # reverts Attack Speed
                self.time_until_next_auto = self.attack_speed

    def simulate_combat(self, duration):
        total_damage = 0
        time = 0
        while time < duration:
            # Turns on RF Asap
            self.apply_rapid_fire(time)
    
            if time - self.multi_shot_last_used >= self.multi_shot_cd and not self.skill_used:
                # Multi-Shot
                damage = self.calculate_shot_damage(multi_shot=True)
                total_damage += damage
                self.multi_shot_last_used = time
                elapsed_time = 0.5
                self.skill_used = True  # Used Trueshot or Multi-Shot
                self.apply_quick_shots()
                print(f"Time: {time:.2f}s - Multi-Shot - Damage: {damage:.2f}")
            elif self.time_until_next_auto <= 0:
                # Auto-Shot
                damage = self.calculate_shot_damage()
                total_damage += damage
                elapsed_time = self.attack_speed
                self.time_until_next_auto = self.attack_speed
                self.skill_used = False  # Resets Skill
                self.apply_quick_shots()
                print(f"Time: {time:.2f}s - Auto Shot - Damage: {damage:.2f}")
            elif not self.skill_used and not (self.quick_shots_active and self.rapid_fire_active):
                # Trueshot (won't trigger if both QS and RF are active)
                damage = self.calculate_shot_damage(trueshot=True)
                total_damage += damage
                elapsed_time = self.trueshot_cast_time
                self.time_until_next_auto -= self.trueshot_cast_time
                self.skill_used = True  # Used Trueshot or Multi-Shot
                self.apply_quick_shots()
                print(f"Time: {time:.2f}s - Trueshot - Damage: {damage:.2f}")
            else:
                # Waits for the next Auto-Shot
                elapsed_time = self.time_until_next_auto
                self.time_until_next_auto = 0
            
            time += elapsed_time
            
            # Updates QS
            self.update_quick_shots(elapsed_time)
            # Updates RF
            self.update_rapid_fire(elapsed_time)
        
        dps = total_damage / duration
        return dps

########################
# Sim parameters
# Only modify this
########################
min_damage = 103 # Weapon's min damage
max_damage = 192 # Weapon's max damage
weapon_speed = 3 # Weapon's Attack Speed
attack_speed = 2.61  # Hunter Attack Speed
ranged_attack_power = 1524 # Hunter Attack Power
scope_bonus = 7 # Weapon's enchant. Type 0 if using Biznick's.
ammo_dps = 17.5 # Ammo DPS
crit_chance = 24.87  # Crit Chance
fight_duration = 120 # Fight Duration
########################
# Discord: syg_
########################

hunter = Hunter(min_damage, max_damage, weapon_speed, attack_speed, ranged_attack_power, scope_bonus, ammo_dps, crit_chance)

dps = hunter.simulate_combat(fight_duration)
print(f"DPS: {dps:.2f}")
