from flask import Flask, request, jsonify
from equipment import equipment_options
import random

app = Flask(__name__)

class Hunter:
    def __init__(self, race, weapon_skill, equipment):
        self.equipment = equipment
        self.base_agility = self.get_base_agility(race)
        self.base_attack_power = 110
        self.base_crit_chance = 0.05  # 5% base crit chance
        self.hit_chance = 0
        self.weapon_skill = weapon_skill
        self.miss_chance = 0.09 if not weapon_skill else 0.06
        self.scope_bonus = 0
        self.ammo_dps = 0
        self.trueshot_bonus = 50
        self.multi_shot_bonus = 172
        self.quick_shots_duration = 12
        self.quick_shots_chance = 0.05
        self.quick_shots_active = False
        self.quick_shots_time_left = 0
        self.rapid_fire_cd = 300  # Cooldown RF
        self.rapid_fire_duration = 15  # Duración RF
        self.rapid_fire_active = False
        self.rapid_fire_time_left = 0
        self.rapid_fire_last_used = -self.rapid_fire_cd  # Iniciar como si no se hubiera usado aún
        self.multi_shot_cd = 10  # CD de Multi-Shot
        self.multi_shot_last_used = -self.multi_shot_cd
        self.trueshot_cast_time = 1.0  # Tiempo de casteo de Trueshot
        self.time_until_next_auto = 0  # Tiempo hasta el próximo auto disparo
        self.trueshot_used = False  # Indica si Trueshot ya fue usado entre auto disparos

        self.process_equipment()

    def get_base_agility(self, race):
        base_agility = {
            'night_elf': 130,
            'dwarf': 121,
            'gnome': 128,
            'human': 125,
            'high_elf': 122,
            'troll': 127,
            'orc': 122,
            'tauren': 120,
            'undead': 123,
            'goblin': 122
        }
        return base_agility.get(race.lower(), 0)

    def process_equipment(self):
        self.attack_power = self.base_attack_power
        self.agility = self.base_agility
        self.crit_chance = self.base_crit_chance
        self.hit_chance = 0
        self.haste = 0

        for item in self.equipment.values():
            self.agility += item.get('agility', 0)
            self.attack_power += item.get('attack_power', 0)
            self.crit_chance += item.get('crit_chance', 0) / 100
            self.hit_chance += item.get('hit', 0) / 100
            self.haste += item.get('haste', 0) / 100

            # If the item is a ranged weapon, set weapon stats
            if item.get('slot') == 'ranged':
                self.min_damage = item.get('min_damage', 0)
                self.max_damage = item.get('max_damage', 0)
                self.weapon_speed = item.get('weapon_speed', 0)

            # If the item is ammo, set ammo DPS
            if item.get('slot') == 'ammo':
                self.ammo_dps = item.get('ammo_dps', 0)
            
            # If the item is ammo bag, set haste bonus
            if item.get('slot') == 'ammo_bag':
                self.haste += item.get('haste', 0) / 100

        self.attack_power += self.agility * 2
        self.crit_chance += self.agility / 53

    def calculate_damage_range(self):
        min_range = (((self.min_damage + self.scope_bonus) / self.weapon_speed) + (self.attack_power / 14) + self.ammo_dps) * self.weapon_speed
        max_range = (((self.max_damage + self.scope_bonus) / self.weapon_speed) + (self.attack_power / 14) + self.ammo_dps) * self.weapon_speed
        return min_range, max_range

    def calculate_shot_damage(self, trueshot=False, multi_shot=False):
        min_range, max_range = self.calculate_damage_range()
        damage = random.uniform(min_range, max_range)
        if trueshot:
            damage += self.trueshot_bonus
        if multi_shot:
            damage += self.multi_shot_bonus
        if random.random() < self.crit_chance:
            damage *= 2.3  # Doble daño en crítico
        return damage

    def apply_quick_shots(self):
        if random.random() < self.quick_shots_chance:
            if self.quick_shots_active:
                self.quick_shots_time_left = self.quick_shots_duration
            else:
                self.quick_shots_active = True
                self.quick_shots_time_left = self.quick_shots_duration
                self.attack_speed /= 1.3
                self.time_until_next_auto /= 1.3

    def update_quick_shots(self, delta_time):
        if self.quick_shots_active:
            self.quick_shots_time_left -= delta_time
            if self.quick_shots_time_left <= 0:
                self.quick_shots_active = False
                self.attack_speed *= 1.3
                self.time_until_next_auto *= 1.3

    def update_rapid_fire(self, delta_time):
        if self.rapid_fire_active:
            self.rapid_fire_time_left -= delta_time
            if self.rapid_fire_time_left <= 0:
                self.rapid_fire_active = False
                self.attack_speed *= 1.4
                self.time_until_next_auto *= 1.4

    def simulate(self, duration):
        current_time = 0
        total_damage = 0

        while current_time < duration:
            delta_time = 0.1  # Simulate in 0.1s intervals

            # Apply buffs
            self.update_quick_shots(delta_time)
            self.update_rapid_fire(delta_time)

            # Check if it's time to auto-shot
            if self.time_until_next_auto <= 0:
                if random.random() < self.miss_chance - self.hit_chance:
                    damage = 0
                else:
                    damage = self.calculate_shot_damage()
                total_damage += damage
                self.apply_quick_shots()
                self.time_until_next_auto = self.weapon_speed / (1 + self.haste)

                # If rapid fire is off cooldown, activate it
                if current_time - self.rapid_fire_last_used >= self.rapid_fire_cd:
                    self.rapid_fire_active = True
                    self.rapid_fire_time_left = self.rapid_fire_duration
                    self.attack_speed /= 1.4
                    self.time_until_next_auto /= 1.4
                    self.rapid_fire_last_used = current_time

            self.time_until_next_auto -= delta_time
            current_time += delta_time

        dps = total_damage / duration
        return dps

@app.route('/simulate', methods=['POST'])
def simulate():
    data = request.json
    race = data.get('race')
    weapon_skill = data.get('weapon_skill')
    duration = int(data.get('duration'))
    equipment = data.get('equipment', {})

    hunter = Hunter(race, weapon_skill, equipment)
    dps = hunter.simulate(duration)
    
    return jsonify({'dps': dps})

if __name__ == '__main__':
    app.run(debug=True)
