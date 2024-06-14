from flask import Flask, render_template, request, jsonify
import random

app = Flask(__name__)

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
        self.quick_shots_duration = 12 # Duration of quick shots
        self.quick_shots_chance = 0.05 # chance % of quick shots proc
        self.quick_shots_active = False # checks if QS is active
        self.quick_shots_time_left = 0
        self.rapid_fire_cd = 300  # Rapid Fire CD
        self.rapid_fire_duration = 15  # Rapid Fire Duration
        self.rapid_fire_active = False # checks if RF is active
        self.rapid_fire_time_left = 0
        self.rapid_fire_last_used = -self.rapid_fire_cd 
        self.multi_shot_cd = 10  # Multi-shot CD
        self.multi_shot_last_used = -self.multi_shot_cd
        self.trueshot_cast_time = 1.0 
        self.time_until_next_auto = attack_speed  # Time until next Auto Shot (Hunter attack speed)
        self.trueshot_used = False 
        
    def calculate_damage_range(self):
        min_range = (((self.min_damage + self.scope_bonus) / self.weapon_speed) + (self.ranged_attack_power / 14) + self.ammo_dps) * self.weapon_speed
        max_range = (((self.max_damage + self.scope_bonus) / self.weapon_speed) + (self.ranged_attack_power / 14) + self.ammo_dps) * self.weapon_speed
        return min_range, max_range

    def calculate_shot_damage(self, trueshot=False, multi_shot=False):
        # Auto Shot logic
        min_range, max_range = self.calculate_damage_range()
        damage = random.uniform(min_range, max_range)
        if trueshot:
            damage += self.trueshot_bonus
        if multi_shot:
            damage += self.multi_shot_bonus
        if random.random() < self.crit_chance:
            damage *= 2.3  # Crit!
        return damage

    def apply_quick_shots(self):
        # Checks if quick shots activates (or reactivates)
        if random.random() < self.quick_shots_chance:
            self.quick_shots_active = True
            self.quick_shots_time_left = self.quick_shots_duration
            self.attack_speed *= 0.7  

    def update_quick_shots(self, elapsed_time):
        if self.quick_shots_active:
            self.quick_shots_time_left -= elapsed_time
            if self.quick_shots_time_left <= 0:
                # Quick Shots is over, reverts AS back.
                self.quick_shots_active = False
                self.attack_speed = self.base_attack_speed 
                self.time_until_next_auto = self.base_attack_speed

    def apply_rapid_fire(self, current_time):
        # Turns on RF
        if current_time - self.rapid_fire_last_used >= self.rapid_fire_cd:
            self.rapid_fire_active = True
            self.rapid_fire_time_left = self.rapid_fire_duration
            self.attack_speed *= 0.6  
            self.time_until_next_auto *= 0.6
            self.rapid_fire_last_used = current_time

    def update_rapid_fire(self, elapsed_time):
        # RF Logic
        if self.rapid_fire_active:
            self.rapid_fire_time_left -= elapsed_time
            if self.rapid_fire_time_left <= 0:
                # Means RF is over. Reverts AS
                self.rapid_fire_active = False
                self.attack_speed = self.base_attack_speed 
                self.time_until_next_auto = self.base_attack_speed

    def simulate_combat(self, duration):
        total_damage = 0
        time = 0
        while time < duration:
            # First Step is to apply Rapid Fire ASAP
            self.apply_rapid_fire(time)
            
            # Checks if quick shots triggers
            self.apply_quick_shots()

            if time - self.multi_shot_last_used >= self.multi_shot_cd and not self.trueshot_used:
                # Multi-Shot
                damage = self.calculate_shot_damage(multi_shot=True)
                total_damage += damage
                self.multi_shot_last_used = time
                elapsed_time = 0.5
                self.trueshot_used = True 
            elif self.time_until_next_auto <= 0:
                # Auto Shot
                damage = self.calculate_shot_damage()
                total_damage += damage
                elapsed_time = self.attack_speed
                self.time_until_next_auto = self.attack_speed
                self.trueshot_used = False  # Resets Trueshot usage
            elif not self.trueshot_used and not (self.quick_shots_active and self.rapid_fire_active):
                # Trueshot (checks if both buffs are active)
                damage = self.calculate_shot_damage(trueshot=True)
                total_damage += damage
                elapsed_time = self.trueshot_cast_time
                self.time_until_next_auto -= self.trueshot_cast_time
                self.trueshot_used = True 
            else:
                # Wait for Next AA
                elapsed_time = self.time_until_next_auto
                self.time_until_next_auto = 0
            
            time += elapsed_time
            
            # Updates QS
            self.update_quick_shots(elapsed_time)
            # Updates RF
            self.update_rapid_fire(elapsed_time)
        
        dps = total_damage / duration
        return dps

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/simulate', methods=['POST'])
def simulate():
    data = request.json
    hunter = Hunter(
        min_damage=data['min_damage'],
        max_damage=data['max_damage'],
        weapon_speed=data['weapon_speed'],
        attack_speed=data['attack_speed'],
        ranged_attack_power=data['ranged_attack_power'],
        scope_bonus=data['scope_bonus'],
        ammo_dps=data['ammo_dps'],
        crit_chance=data['crit_chance']
    )
    dps = hunter.simulate_combat(data['duration'])
    return jsonify({'dps': dps})

if __name__ == '__main__':
    app.run(debug=True)
