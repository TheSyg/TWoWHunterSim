from flask import Flask, render_template, request
import random

app = Flask(__name__)

class Hunter:
    def __init__(self, stats, talents, num_simulations):
        self.attack_power = stats.get("attack_power", 0)
        self.crit_chance = stats.get("crit_chance", 0) / 100  # Se ingresa como %
        self.hit_chance = stats.get("hit", 0) / 100  # Se ingresa como %
        
        self.min_damage = stats.get("min_damage", 0)
        self.max_damage = stats.get("max_damage", 0)
        self.weapon_speed = stats.get("weapon_speed", 0)
        self.ammo_dps = stats.get("ammo_dps", 0)

        self.miss_chance = 0.08  # 8% de base
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
        self.time_until_next_auto = 0
        self.trueshot_used = False

        # TALENTOS
        self.talent_5_percent_damage = True
        self.talent_extra_autoshot = True
        self.talent_bleed_on_crit = True

        self.num_simulations = num_simulations

    def calculate_damage_range(self):
        min_range = (((self.min_damage) / self.weapon_speed) + (self.attack_power / 14) + self.ammo_dps) * self.weapon_speed
        max_range = (((self.max_damage) / self.weapon_speed) + (self.attack_power / 14) + self.ammo_dps) * self.weapon_speed

        # Aplicar talento de +5% daño si está activado
        if self.talent_5_percent_damage:
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
            damage *= 2.3  # Crítico = 230% de daño
            crit = True

        return damage, crit

    def apply_quick_shots(self):
        if random.random() < self.quick_shots_chance:
            if self.quick_shots_active:
                self.quick_shots_time_left = self.quick_shots_duration
            else:
                self.quick_shots_active = True
                self.quick_shots_time_left = self.quick_shots_duration
                self.weapon_speed /= 1.3
                self.time_until_next_auto /= 1.3

    def update_quick_shots(self, delta_time):
        if self.quick_shots_active:
            self.quick_shots_time_left -= delta_time
            if self.quick_shots_time_left <= 0:
                self.quick_shots_active = False
                self.weapon_speed *= 1.3
                self.time_until_next_auto *= 1.3

    def update_rapid_fire(self, delta_time):
        if self.rapid_fire_active:
            self.rapid_fire_time_left -= delta_time
            if self.rapid_fire_time_left <= 0:
                self.rapid_fire_active = False
                self.weapon_speed *= 1.4
                self.time_until_next_auto *= 1.4

    def simulate(self, duration):
        total_dps = 0

        for _ in range(self.num_simulations):
            current_time = 0
            total_damage = 0
            bleed_damage = 0

            while current_time < duration:
                delta_time = 0.1  # Intervalos de simulación de 0.1s

                self.update_quick_shots(delta_time)
                self.update_rapid_fire(delta_time)

                if self.time_until_next_auto <= 0:
                    if random.random() < self.miss_chance - self.hit_chance:
                        damage = 0
                        crit = False
                    else:
                        damage, crit = self.calculate_shot_damage()

                    total_damage += damage

                    # Aplicar talento de sangrado si hubo crítico
                    if crit and self.talent_bleed_on_crit:
                        bleed_damage += (damage * 0.3) / 8  # Se distribuye en 8 segundos

                    # Aplicar talento de auto-shot extra (6% de chance)
                    if self.talent_extra_autoshot and random.random() < 0.06:
                        extra_damage, _ = self.calculate_shot_damage()
                        total_damage += extra_damage

                    self.apply_quick_shots()
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

@app.route("/", methods=["GET", "POST"])
def index():
    dps = None

    if request.method == "POST":
        stats = {
            "attack_power": float(request.form["attack_power"]),
            "crit_chance": float(request.form["crit_chance"]),
            "hit": float(request.form["hit"]),
            "min_damage": float(request.form["min_damage"]),
            "max_damage": float(request.form["max_damage"]),
            "weapon_speed": float(request.form["weapon_speed"]),
            "ammo_dps": float(request.form["ammo_dps"])
        }

        talents = {
            "5_percent_damage": "5_percent_damage" in request.form,
            "extra_autoshot": "extra_autoshot" in request.form,
            "bleed_on_crit": "bleed_on_crit" in request.form
        }

        duration = int(request.form["duration"])
        num_simulations = int(request.form["num_simulations"])

        hunter = Hunter(stats, talents, num_simulations)
        dps = hunter.simulate(duration)

    return render_template("index.html", dps=dps)

if __name__ == "__main__":
    app.run(debug=True)
