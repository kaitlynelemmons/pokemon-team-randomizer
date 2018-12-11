import random

def main():
    curr_generation = 7
    saved_list = 'first_stagers_gen' + str(curr_generation) + '.txt'
    saved_list_file = open(saved_list, 'r')

    first_stagers = []
    for pokemon in saved_list_file:
        pokemon = pokemon.rstrip()
        print pokemon
        first_stagers.append(pokemon)

    print 'Found: ' + str(len(first_stagers)) + ' first stage Pokemon'

    # Select some random Pokemon
    print "Kaitlyn: "
    kaitlyn_pokemon = generate_pokemon(12, first_stagers)
    print_pokemon(kaitlyn_pokemon)

    print "David: "
    david_pokemon = generate_pokemon(12, first_stagers)
    print_pokemon(david_pokemon)


def generate_pokemon(number, first_stagers):
    type_counter = initialize_types()
    pokemon = []
    while len(pokemon) < number:
        skip = False
        rando = random.randint(0, len(first_stagers) - 1)
        parts = first_stagers[rando].split(': ')
        name = parts[0]
        types = parts[1]
        for type in types.split(','):
            type_counter[type] += 1
            if type_counter[type] >= 3:
                print 'Skipping ' + name + ' because of ' + type
                skip = True

        if not skip:
            pokemon.append(first_stagers[rando])

    return pokemon


def print_pokemon(pokemon_list):
    i = 0
    for pokemon in pokemon_list:
        print str(i + 1) + '.\t' + pokemon
        i += 1


def initialize_types():
    types = {}
    types['Normal'] = 0
    types['Fighting'] = 0
    types['Flying'] = 0
    types['Poison'] = 0
    types['Ground'] = 0
    types['Rock'] = 0
    types['Bug'] = 0
    types['Ghost'] = 0
    types['Steel'] = 0
    types['Fire'] = 0
    types['Water'] = 0
    types['Grass'] = 0
    types['Electric'] = 0
    types['Psychic'] = 0
    types['Ice'] = 0
    types['Dragon'] = 0
    types['Dark'] = 0
    types['Fairy'] = 0
    return types


main()