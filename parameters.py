#################################
#########Only Modify Here########
#################################
stats = {
    "attack_power": 1603,
    "crit_chance": 30.57,
    "hit": 8,              # cap: 8%
    "min_damage": 585,
    "max_damage": 701,
    "weapon_speed": 2.99,
    "ammo_dps": 17.5
}
#################################
# Discord: @syg_##################
#################################

# Does not support Badge of the Swarmguard (yet)
active_trinkets = []
# Examples
# active_trinkets = ["Earthstrike", "Jom Gabbar"]
# active_trinkets = ["Devilsaur Eye"]  # Example: One activatable trinket
# active_trinkets = []  # Example: No activatable trinkets
# List of supported trinkets: Devilsaur Eye, Earthstrike, Jom Gabbar, Kiss of the Spider, Slayer's Crest


#################################
# Ignore if no active trinkets are set up. Make sure to input the correct stats above.
passive_trinket1 = {
    "attack_power": 0,
    "agility": 0,
    "crit_chance": 2,
    "hit": 0
}

passive_trinket2 = {
    "attack_power": 0,  
    "agility": 0,       
    "crit_chance": 2,   
    "hit": 0            
}
#################################


def convert_agility_to_stats(trinket):
    agility = trinket.get("agility", 0)
    trinket["attack_power"] += agility * 2  # 1 Agi = 2 AP
    trinket["crit_chance"] += agility / 53  # 53 Agi = 1% Crit
    del trinket["agility"]
    return trinket

# Apply conversions
passive_trinket1 = convert_agility_to_stats(passive_trinket1)
passive_trinket2 = convert_agility_to_stats(passive_trinket2)

duration = 120  # PW type fight: 120s
num_simulations = 25000  # Recommended to do over 10000 sims
