import requests

class Pokemon:
    def __init__(self, name):
        self.name = name
        self.movesets = {}

    def add_moveset(self, game, moves):
        """Add or update moveset for a specific game."""
        if game not in self.movesets:
            self.movesets[game] = moves
        else:
            self.movesets[game].extend(moves)
            
    def get_moveset_for_game(self, game, games):
        """Get moveset for a game, falling back to the oldest available moveset."""
        # Get the moveset for the specific game or fallback to the oldest available
        if game in self.movesets:
            return self.movesets[game]
        else:
            # Fall back to the oldest available moveset
            for g in games:
                if g in self.movesets:
                    return self.movesets[g]
            return []



def fetch_pokemon_list(limit=1800):
    """Fetches a list of all Pokémon names and their URLs."""
    url = "https://pokeapi.co/api/v2/pokemon/"
    response = requests.get(url, params={'limit': limit})
    if response.status_code == 200:
        return response.json()['results']
    else:
        print(f"Failed to fetch Pokémon list. Status code: {response.status_code}")
        return []

def fetch_pokemon_moves(pokemon_url):
    """Fetches moves for a specific Pokémon using its URL."""
    response = requests.get(pokemon_url)
    if response.status_code == 200:
        return response.json().get('moves', [])
    else:
        print(f"Failed to fetch moves for {pokemon_url}. Status code: {response.status_code}")
        return []

def filter_level_up_moves_by_game(moves, game_name):
    """Filters level-up moves by the given game (version group)."""
    level_up_moves = []
    for move in moves:
        for version_detail in move['version_group_details']:
            if version_detail['version_group']['name'] == game_name and version_detail['move_learn_method']['name'] == 'level-up':
                move_name = move['move']['name'].upper().replace('-', '_')
                level = version_detail['level_learned_at']
                level_up_moves.append((move_name, level))
    return sorted(level_up_moves, key=lambda x: x[1])

def fetch_version_groups():
    """Fetches the version groups information to get game names in chronological order."""
    url = "https://pokeapi.co/api/v2/version-group/"
    response = requests.get(url)
    if response.status_code == 200:
        version_groups = response.json()['results']

        # Fetch details for each version group to access the 'order' field
        version_groups_detailed = []
        for vg in version_groups:
            vg_response = requests.get(vg['url'])
            if vg_response.status_code == 200:
                version_groups_detailed.append(vg_response.json())
            else:
                print(f"Failed to fetch details for version group {vg['name']}. Status code: {vg_response.status_code}")
        
        # Sort version groups by their 'order' field
        version_groups_sorted = sorted(version_groups_detailed, key=lambda x: x['order'])
        return [vg['name'] for vg in version_groups_sorted]
    else:
        print(f"Failed to fetch version groups info. Status code: {response.status_code}")
        return []



def write_movesets_to_file(pokemon_objects, games):
    """Writes movesets to files for each game."""
    for game in games:
        filename = f"levelupdataVersion{game.replace('-', '').capitalize()}.s"
        with open("new_learnsets/"+filename, 'w') as file:
            for poke_name, poke_obj in pokemon_objects.items():
                # Get moveset for the current game, falling back to the oldest available moveset
                moveset = poke_obj.get_moveset_for_game(game, games)

                # If a moveset is found, write it to the file
                if moveset:
                    file.write(f"levelup SPECIES_{poke_name.upper()}\n")
                    for move, level in moveset:
                        file.write(f"    learnset MOVE_{move}, {level}\n")
                    file.write("    terminatelearnset\n\n")
                else:
                    # Ensure Pokémon is included even if no moveset is available for the specific game
                    file.write(f"levelup SPECIES_{poke_name.upper()}\n")
                    file.write("    terminatelearnset\n\n")
    print("Files have been successfully generated.")

def main():
    # Fetch version group (game) information
    print("Fetching generations")
    games = fetch_version_groups()
    print("Finished with generations")
    
    # Fetch all Pokémon
    print("Fetching pokemon data")
    all_pokemon = fetch_pokemon_list()
    print("Finished with pokemon data")

    # Create a dictionary to store all Pokémon objects
    pokemon_objects = {}

    for pokemon in all_pokemon:
        print("Dealing with", pokemon["name"])
        # Create a Pokemon object
        pokemon_obj = Pokemon(name=pokemon['name'])

        # Fetch the moves for this Pokémon
        moves = fetch_pokemon_moves(pokemon['url'])

        # For each game, filter level-up moves and add to the Pokémon object
        for game in games:
            print("\tHandling", game)
            game_moves = filter_level_up_moves_by_game(moves, game)
            if game_moves:
                pokemon_obj.add_moveset(game, game_moves)
            print("\tFinsihed with", game)

        # Store the Pokemon object in the dictionary
        pokemon_objects[pokemon['name']] = pokemon_obj
        print("Finished with", pokemon["name"])

    # Write movesets to files for each game
    write_movesets_to_file(pokemon_objects, games)

if __name__ == "__main__":
    main()
