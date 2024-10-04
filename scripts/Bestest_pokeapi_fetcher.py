import pokebase as pb

class Pokemon:
    def __init__(self, name):
        self.name = name
        self.movesets = {}
        self.dex_entries = {}

    def add_moveset(self, game, moves):
        """Add or update moveset for a specific game."""
        if game not in self.movesets:
            self.movesets[game] = moves
        else:
            self.movesets[game].extend(moves)
    
    def add_dexEntry(self, game, entry):
        """Add dex entry for a specific game."""
        if game not in self.dex_entries:
            self.dex_entries[game] = entry.replace("\\", "\\\\")
            
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
        
    def get_dexEntry_for_game(self, game, games):
        """Get dex entry for a game, falling back to the oldest available dex entry."""
        # Get the dex entry for the specific game or fallback to the oldest available
        if game in self.dex_entries:
            return self.dex_entries[game]
        else:
            # Fall back to the oldest available dex entry
            for g in games:
                if g in self.dex_entries:
                    return self.dex_entries[g]
            return []

def fetch_pokemon_list(limit=1800):
    """Fetches a list of all Pokémon names."""
    return [pokemon.name for pokemon in pb.APIResourceList('pokemon', limit=limit)]

def fetch_pokemon_data(pokemon_name):
    """Fetches moves and dex entries for a specific Pokémon using PokéBase."""
    pokemon = pb.pokemon(pokemon_name)
    species = pb.pokemon_species(pokemon_name)
    return pokemon, species

def filter_level_up_moves_by_game(moves, game_name):
    """Filters level-up moves by the given game (version group)."""
    level_up_moves = []
    for move in moves:
        for version_detail in move.version_group_details:
            if version_detail.version_group.name == game_name and version_detail.move_learn_method.name == 'level-up':
                move_name = move.move.name.upper().replace('-', '_')
                level = version_detail.level_learned_at
                level_up_moves.append((move_name, level))
    return sorted(level_up_moves, key=lambda x: x[1])

def filter_dex_entries_by_game(entries, game_name):
    """Filters dex entries by the given game (version group)."""
    for entry in entries:
        if entry.language.name == "en" and entry.version.name == game_name:
            return entry.flavor_text
    return None

def fetch_version_groups():
    """Fetches the version groups information to get game names in chronological order."""
    version_groups = pb.APIResourceList('version-group').all()
    sorted_version_groups = sorted(version_groups, key=lambda vg: pb.version_group(vg.name).order)
    return [vg.name for vg in sorted_version_groups]

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
    
def write_dexEntries_to_file(pokemon_objects, games):
    """Writes dex entries to files for each game."""
    for game in games:
        filename = f"dexentryVersion{game.replace('-', '').capitalize()}.s"
        with open("new_dexEntries/"+filename, 'w') as file:
            for poke_name, poke_obj in pokemon_objects.items():
                # Get entry for the current game, falling back to the oldest available moveset
                entry = poke_obj.get_dexEntry_for_game(game, games)

                # If an entry is found, write it to the file
                if entry:
                    file.write(f"mondata SPECIES_{poke_name.upper()}, \"{poke_name}\"\n")
                    file.write(f"\tmondexentry SPECIES_{poke_name.upper()}, \"{entry}\"\n")
                else:
                    # Ensure Pokémon is included even if no entry is available for the specific game
                    file.write(f"mondata SPECIES_{poke_name.upper()}, \"{poke_name}\"\n")
                    file.write(f"\tmondexentry SPECIES_{poke_name.upper()}, \"\"\n")
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

    for pokemon_name in all_pokemon:
        print("Dealing with", pokemon_name)
        # Create a Pokemon object
        pokemon_obj = Pokemon(name=pokemon_name)

        # Fetch the Pokémon data (moves and dex entries)
        pokemon, species = fetch_pokemon_data(pokemon_name)

        # For each game, filter level-up moves and dex entries and add them to the Pokémon object
        for game in games:
            game_moves = filter_level_up_moves_by_game(pokemon.moves, game)
            if game_moves:
                pokemon_obj.add_moveset(game, game_moves)
            dex_entry = filter_dex_entries_by_game(species.flavor_text_entries, game)
            if dex_entry:
                pokemon_obj.add_dexEntry(game, dex_entry)

        # Store the Pokémon object in the dictionary
        pokemon_objects[pokemon_name] = pokemon_obj
        print("Finished with", pokemon_name)

    # Write movesets to files for each game
    write_movesets_to_file(pokemon_objects, games)
    # Write dex entries to files for each game
    write_dexEntries_to_file(pokemon_objects, games)

if __name__ == "__main__":
    main()
