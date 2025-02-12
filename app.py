import random
from parameters import stats, duration, num_simulations, active_trinkets, passive_trinket1, passive_trinket2

# Trinket effects
TRINKET_EFFECTS = {
    "Devilsaur Eye": {"attack_power": 150, "duration": 20},
    "Earthstrike": {"attack_power": 280, "duration": 20},
    "Jom Gabbar": {"attack_power": 65, "stacking": 65, "duration": 20},
    "Kiss of the Spider": {"haste": 0.20, "duration": 15},
    "Slayer's Crest": {"attack_power": 260, "duration": 20}
}

class Hunter:
    def __init__(self, stats, active_trinkets, passive_trinket1, passive_trinket2, num_simulations):
        # Base stats
        self.base_attack_power = stats["attack_power"]
        self.crit_chance = stats["crit_chance"] / 100
        self.hit_chance = stats["hit"] / 100
        self.min_damage = stats["min_damage"]
        self.max_damage = stats["max_damage"]
        self.weapon_speed = stats["weapon_speed"]
        self.ammo_dps = stats["ammo_dps"]

        # Combat mechanics
        self.miss_chance = max(0.08 - self.hit_chance, 0)  # 8% base miss chance, reduced by hit
        self.trueshot_bonus = 50
        self.multi_shot_bonus = 172
        self.rapid_fire_cd = 300
        self.rapid_fire_duration = 15
        self.rapid_fire_active = False
        self.rapid_fire_last_used = -self.rapid_fire_cd
        self.time_until_next_auto = 0
        self.num_simulations = num_simulations

        # Trinket Management
        self.active_trinkets = active_trinkets.copy()
        self.passive_trinkets = [passive_trinket1, passive_trinket2]  
        self.feign_death_cd = 30
        self.feign_death_last_used = -self.feign_death_cd
        self.trinket_swaps = 0
        self.current_trinket_index = 0
        self.active_trinket_effects = {}

        self.trinket_internal_cd = 20  
        self.last_trinket_used_time = -self.trinket_internal_cd  
        self.trinket_expired_time = None  # When a trinket expired (used for delayed swap)

        # Debugs
        self.debug = False

    def activate_trinket(self, current_time):
        """Activates a trinket **only if the internal cooldown has passed**."""
        if (
            self.current_trinket_index < len(self.active_trinkets)  # Still have trinkets left
            and (current_time - self.last_trinket_used_time) >= self.trinket_internal_cd  # Internal cooldown passed
        ):
            trinket = self.active_trinkets[self.current_trinket_index]
            if trinket in TRINKET_EFFECTS:
                effect = TRINKET_EFFECTS[trinket].copy()
                effect["end_time"] = current_time + effect["duration"]
                self.active_trinket_effects[trinket] = effect
                self.last_trinket_used_time = current_time  # Reset internal cooldown
                if self.debug:
                    print(f"{trinket} activated at {current_time}s")
            self.current_trinket_index += 1  

    def apply_active_trinket_effects(self, current_time):
        """Applies and removes active trinket effects."""
        total_ap = self.base_attack_power  
        total_haste = 1.0  

        for trinket, effect in list(self.active_trinket_effects.items()):
            if current_time >= effect["end_time"]:
                del self.active_trinket_effects[trinket]
                self.trinket_expired_time = current_time  # Track when it expired
                if self.debug:
                    print(f"{trinket} expired at {current_time}s")
            else:
                if "attack_power" in effect:
                    total_ap += effect["attack_power"]
                if "haste" in effect:
                    total_haste += effect["haste"]
                if "stacking" in effect and current_time % 2 == 0:
                    total_ap += effect["stacking"]

        self.attack_power = total_ap
        self.weapon_speed = stats["weapon_speed"] / total_haste  

    def feign_death_swap(self, current_time):
        """Swaps an active trinket for a passive one **only when a trinket expires and Feign Death is ready**."""
        if (
            self.trinket_expired_time is not None  # A trinket has expired
            and self.trinket_swaps < len(self.active_trinkets)  # Still trinkets to swap
        ):
            # If Feign Death is available, swap immediately
            if current_time - self.feign_death_last_used >= self.feign_death_cd:
                self.feign_death_last_used = current_time
                passive_trinket = self.passive_trinkets[self.trinket_swaps]

                self.attack_power += passive_trinket.get("attack_power", 0)
                self.crit_chance += passive_trinket.get("crit_chance", 0) / 100
                self.hit_chance += passive_trinket.get("hit", 0) / 100
                self.miss_chance = max(0.08 - self.hit_chance, 0)  # Recalculate miss chance

                self.trinket_swaps += 1
                self.trinket_expired_time = None  # Reset expired trinket tracker
                if self.debug:
                    print(f"Feign Death at {current_time}s - Swapped trinket for passive one.")
            
            # If Feign Death is still on cooldown, wait and swap as soon as it's ready
            elif self.debug:
                print(f"Waiting for Feign Death (on cooldown) at {current_time}s")

    def calculate_damage_range(self):
        """Calculates damage range with trinket buffs applied."""
        min_range = (((self.min_damage) / self.weapon_speed) + (self.attack_power / 14) + self.ammo_dps) * self.weapon_speed
        max_range = (((self.max_damage) / self.weapon_speed) + (self.attack_power / 14) + self.ammo_dps) * self.weapon_speed
        return min_range * 1.05, max_range * 1.05  

    def calculate_shot_damage(self):
        """Determines shot damage including crits."""
        min_range, max_range = self.calculate_damage_range()
        damage = random.uniform(min_range, max_range)
        crit = random.random() < self.crit_chance
        if crit:
            damage *= 2.3
        return damage, crit

    def simulate(self, duration):
        """Runs the simulation and returns the average DPS."""
        total_dps = 0
        print("Simming...")
        for _ in range(self.num_simulations):
            current_time = 0
            total_damage = 0
            while current_time < duration:
                delta_time = 0.1
                self.apply_active_trinket_effects(current_time)

                if self.time_until_next_auto <= 0:
                    damage, _ = self.calculate_shot_damage()
                    total_damage += damage
                    self.time_until_next_auto = self.weapon_speed

                    if current_time - self.rapid_fire_last_used >= self.rapid_fire_cd:
                        self.activate_trinket(current_time)

                    self.feign_death_swap(current_time)

                self.time_until_next_auto -= delta_time
                current_time += delta_time

            total_dps += total_damage / duration
        return total_dps / self.num_simulations

# Run the simulation
hunter = Hunter(stats, active_trinkets, passive_trinket1, passive_trinket2, num_simulations)
print(f"DPS Average: {round(hunter.simulate(duration), 2)}")