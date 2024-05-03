import random

game_timer = 0
npc_state = "Idle"

enemy_health = 1
has_speed_boost = False
enemy_within_range = True

while enemy_health > 0:
    game_timer += 1
    
    print(f"Game timer: {game_timer}")
    enemy_within_range = random.choice([True, False])

    if npc_state == "Idle":
        if enemy_within_range:
            print("Watch out! Enemy spotted! Engaging...")
            npc_state = "Attack"

        elif enemy_health <= 0.3:
            print("Enemy is fleeing! Pursue the target")
            npc_state = "Walk"

    if npc_state == "Walk":
        if has_speed_boost:
            print("Speed boost activated! Increasing movement speed")
            npc_state = "Run"
        elif enemy_within_range:
            print("Enemy caught up! Initiating attack...")
            npc_state = "Attack"
        
    if npc_state == "Attack":
        print(f"Landed a hit! Enemy health: {enemy_health:.2f}")
        enemy_health -= 0.1

        if not enemy_within_range:
            print("Enemy has fled! Stand down")
            npc_state = "Idle"
        
    if npc_state == "Run":
        if not has_speed_boost:
            print("Speed boost worn off! Returning to normal speed")
            npc_state = "Walk"
        elif enemy_within_range:
            print("Enemy caught up! Initiating attack...")
            npc_state = "Attack"

    print("===========================================")

print("GAME OVER!")
