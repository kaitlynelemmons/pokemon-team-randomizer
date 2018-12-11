#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib2
import time
import logging
from HTMLParser import HTMLParser
import sys

class PokemonListHTMLParser(HTMLParser):
    def __init__(self):
        # initialize the base class
        HTMLParser.__init__(self)
        self.current_tag = ''
        self.in_content = False
        self.pokemon_list = []
        self.td_count = 0
        self.found_pokemon = False

    def handle_starttag(self, tag, attrs):
        current_tag_set = False

        if tag == 'h2':
            self.in_content = False

        if self.current_tag == 'h2' and tag == 'span':
            self.current_tag = 'h2'
            current_tag_set = True

        # Once we've found the content, we want to do other stuff
        if self.in_content:
            if self.current_tag == 'td':
                self.td_count += 1

            # This many tds happen before the Pokemon
            if self.td_count == 2 and tag == 'a':
                # We found a Pokemon!
                self.found_pokemon = True
                # Prevent this from happening again
                self.td_count += 1

        # Set current tag
        if not current_tag_set:
            self.current_tag = tag

    def handle_endtag(self, tag):
        self.current_tag = ''
        if tag == 'tr':
            self.td_count = 0

        # Reset found_pokemon
        self.found_pokemon = False

    def handle_data(self, data):
        if self.current_tag == 'h2':
            if data == 'List of Pokémon by National Pokédex number':
                print "Content found!"
                self.in_content = True

        if self.in_content:
            if self.found_pokemon:
                print "Pokemon (" + self.current_tag + "): " + data
                if not data in self.pokemon_list:
                    self.pokemon_list.append(data)
                else:
                    # This happens with Pokes with multiple forms (i.e. Darmanitan or Rattata)
                    print "Found duplicate Pokemon: " + data


class PokemonIndividualHTMLParser(HTMLParser):
    def __init__(self, generation):
        # initialize the base class
        HTMLParser.__init__(self)
        self.generation = generation
        self.current_tag = '' # in starttag = previous tag; else = current tag
        self.state = ''
        self.description = ''
        self.types = []
        self.locations = []

    def handle_starttag(self, tag, attrs):
        # change state based on what we've seen
        if self.state == 'found_game_locations' and tag == 'small':
            print 'checking small'
            self.state = 'check_th'
        elif self.state == 'found_correct_gen' and tag == 'td':
            print 'checking gen'
            self.state = 'check_location'
        elif self.state == 'found_types' and tag == 'a':
            print 'checking type'
            self.state = 'check_type'
        elif self.state == 'look_for_description' and tag == 'p':
            print 'found description'
            self.state = 'found_description'
        elif self.state == 'found_description':
            if tag == 'div' and ('id', 'toc') in attrs:
                print 'found TOC; end description'
                self.state = ''
            else:
                self.description += ' '
        elif self.state == '':
            if self.current_tag == 'h3' and tag == 'span':
                print 'checking h3'
                self.state = 'check_h3'
            elif len(self.types) == 0 and self.current_tag == 'td' and tag == 'a':
                print 'checking link'
                self.state = 'check_link'

        self.current_tag = tag

    def handle_endtag(self, tag):
        if self.state == 'check_type' and tag == 'table':
            print('found all types; setting state to look for description')
            self.state = 'look_for_description'
        elif self.state == 'check_location' and tag == 'h4':
            print('checked locations and restoring state to empty')
            self.state = ''
        elif self.state == 'found_description':
            self.description += ' '

    def handle_data(self, data):
        if self.state == 'check_h3' and data == 'Game locations':
            self.state = 'found_game_locations'
        elif self.state == 'check_link' and (data == 'Type' or data == 'Types'):
            print 'found type'
            self.state = 'found_types'
        elif self.state == 'check_type':
            data = data.strip()
            if len(data) != 0 and data != 'Unknown':
                print 'type: ' + data
                self.types.append(data)
        elif self.state == 'check_th' and data == self.generation:
            self.state = 'found_correct_gen'
        elif self.state == 'check_location' and self.current_tag == 'span':
            data = data.strip()
            if len(data) != 0:
                if "Let's Go" in data:
                    print("Ending check_location early; found Let's Go game")
                    self.state = ''
        elif self.state == 'check_location' and (self.current_tag == 'td' or self.current_tag == 'a'):
            data = data.strip()
            if len(data) != 0:
                self.locations.append(data)
        elif self.state == 'found_description':
            data = data.strip()
            self.description += data


def convert_generation(generation):
    gen = 'Generation '
    if generation == 7:
        gen += 'VII'
    elif generation == 6:
        gen += 'VI'
    elif generation == 5:
        gen += 'V'
    return gen

def main():
    # Set up to use UTF-8
    reload(sys)
    sys.setdefaultencoding('utf8')

    # Load the Pokemon list
    http_list = "http://bulbapedia.bulbagarden.net/wiki/List_of_Pok%C3%A9mon_by_National_Pok%C3%A9dex_number"
    req = urllib2.Request(http_list, headers={'User-Agent': "Magic Browser"})
    f = urllib2.urlopen(req)
    contents = f.read()
    f.close()

    parser = PokemonListHTMLParser()
    parser.feed(contents)

    # This is 802 (correct)
    print "Found " + str(len(parser.pokemon_list)) + " pokemon"

    # Generation setup
    generations = [151, 251, 386, 493, 649, 721, 802]
    curr_generation = 7
    gen = convert_generation(curr_generation)
    print gen

    # Generate the list
    #saved_list = 'first_stagers_gen' + str(curr_generation) + '.txt'
    saved_list = 'last_stagers_gen' + str(curr_generation) + '.txt'
    first_stagers = []
    print "Generating new first_stagers.txt"
    print "Will go until: " + str(generations[curr_generation - 1])
    for i in range(0, generations[curr_generation - 1]):
        #pokemon = parser.pokemon_list[27] # Sandslash, for testing purposes
        #pokemon = parser.pokemon_list[5] # Charizard, for testing purposes
        #pokemon = parser.pokemon_list[465] # Electivire, for testing purposes
        #pokemon = parser.pokemon_list[511] # Simisage, for testing purposes
        pokemon = parser.pokemon_list[i]
        print(pokemon)
        pokemon_url = 'http://bulbapedia.bulbagarden.net/wiki/' + pokemon.replace(' ', '_') + '_(Pokémon)'
        req = urllib2.Request(pokemon_url, headers={'User-Agent': "Magic Browser"})
        timeout = -1
        for timeouts in range(0, 5):
            timeout = timeouts
            try:
                pokemon_website = urllib2.urlopen(req)
                pokemon_contents = pokemon_website.read()
                pokemon_website.close()
                break
            except urllib2.HTTPError:
                print ('error connecting; will sleep and then retry')
                time.sleep(5) # 5 seconds

        # exit if we reach max timeouts
        if timeout == 4:
            print('error connecting and reached max retries. Please check connection.')
            exit()

        # If does not evolve
        #if not '<a href="/wiki/Evolution" title="Evolution">evolves</a> from' in pokemon_contents:
        #if not 'evolves into' in pokemon_contents and not '<a href="/wiki/Evolution" title="Evolution">evolves</a> into' in pokemon_contents:
            # And is not a Legendar
            #if not '<a href="/wiki/Mythical_Pok%C3%A9mon" title="Mythical Pokémon">Mythical Pokémon</a>' in pokemon_contents:
                # And is not an Ultra Beast
                #if not '<a href="/wiki/Ultra_Beast" title="Ultra Beast">Ultra Beasts</a>' in pokemon_contents:
                    # And is not a Guardian Deity
                    #if not '<a href="/wiki/Guardian_deities" title="Guardian deities">guardian deity</a>' in pokemon_contents:
                        #print "First stage Pokemon: " + pokemon

        # find out if it is available in games for this generation
        individual_parser = PokemonIndividualHTMLParser(gen)
        individual_parser.feed(pokemon_contents)

        print(individual_parser.description)
        print(individual_parser.locations)

        # If it does not evolve
        if not 'evolves into' in individual_parser.description and not '<a href="/wiki/Evolution" title="Evolution">evolves</a> into' in individual_parser.description:
            # And is not a Legendar
            if not '<a href="/wiki/Mythical_Pok%C3%A9mon" title="Mythical Pokémon">Mythical Pokémon</a>' in individual_parser.description:
                # And is not an Ultra Beast
                if not '<a href="/wiki/Ultra_Beast" title="Ultra Beast">Ultra Beasts</a>' in individual_parser.description:
                    # And is not a Guardian Deity
                    if not '<a href="/wiki/Guardian_deities" title="Guardian deities">guardian deity</a>' in individual_parser.description:
                        print ('Final stage Pokemon: ' + pokemon)
                        # only add to list if it's accessible
                        available = False
                        for location in individual_parser.locations:
                            print 'Location: ' + location
                            if 'Pokémon Bank' in location:
                                continue
                            elif 'Event' in location:
                                continue
                            elif 'Trade' in location:
                                continue
                            available = True
                        if available:
                            print pokemon + ' is available in generation ' + str(curr_generation)
                            types = individual_parser.types[0]
                            if len(individual_parser.types) > 1:
                                types += ',' + individual_parser.types[1]
                            print pokemon + ' ' + types
                            first_stagers.append(pokemon + ': ' + types)
                        else:
                            print pokemon + ' is not available in generation ' + str(curr_generation)
                    else:
                        print('Skipping guardian deity')
                else:
                    print('Skipping ultra beast')
            else:
                print('Mythical Pokemon')
        else:
            print('Skipping Pokemon that evolves')

    # outside lookup loop
    out = open(saved_list, 'w')
    for first_stager in first_stagers:
        out.write(first_stager + '\n')
    out.close()

    #print 'Found: ' + str(len(first_stagers)) + ' first stage Pokemon'
    print 'Found: ' + str(len(first_stagers)) + ' final stage Pokemon'

main()