import random

def generate_random_string(length):
  characters = []
  for i in range(length):
    character = random.choice([str(i) for i in range(10)] + [chr(i) for i in range(ord('a'), ord('z') + 1)])
    characters.append(character)

  random.shuffle(characters)
  random_string = ''.join(characters)

  return random_string
