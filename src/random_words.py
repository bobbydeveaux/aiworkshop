#!/usr/bin/env python3
"""
Random Words Generator

A simple utility script that outputs 100 random words.
"""

import random


def get_word_list():
    """
    Returns a list of common English words for random selection.
    """
    words = [
        "apple", "banana", "cherry", "date", "elderberry", "fig", "grape", "honeydew",
        "kiwi", "lemon", "mango", "nectarine", "orange", "papaya", "quince", "raspberry",
        "strawberry", "tangerine", "watermelon", "blueberry", "cantaloupe", "dragonfruit",
        "grapefruit", "jackfruit", "kumquat", "lime", "mulberry", "peach", "pear", "plum",
        "pomegranate", "apricot", "avocado", "blackberry", "coconut", "cranberry", "guava",
        "lychee", "mandarin", "olive", "passionfruit", "persimmon", "pineapple", "rhubarb",
        "starfruit", "tomato", "zucchini", "cucumber", "eggplant", "pepper", "potato",
        "carrot", "broccoli", "cauliflower", "spinach", "lettuce", "kale", "cabbage",
        "celery", "radish", "turnip", "beetroot", "onion", "garlic", "ginger", "mushroom",
        "pumpkin", "squash", "corn", "peas", "beans", "lentils", "rice", "wheat",
        "oats", "barley", "rye", "quinoa", "couscous", "pasta", "bread", "cake",
        "cookie", "pie", "tart", "muffin", "scone", "croissant", "bagel", "donut",
        "pancake", "waffle", "crepe", "pudding", "custard", "ice", "cream", "yogurt",
        "cheese", "butter", "milk", "coffee", "tea", "water", "juice", "soda",
        "wine", "beer", "cider", "cocktail", "smoothie", "milkshake", "latte", "espresso",
        "cappuccino", "mocha", "americano", "macchiato", "frappuccino", "chai", "matcha",
        "chocolate", "vanilla", "caramel", "hazelnut", "almond", "peanut", "cashew", "walnut",
        "pecan", "pistachio", "macadamia", "chestnut", "sunflower", "pumpkin", "sesame", "flax",
        "chia", "hemp", "poppy", "mustard", "coriander", "cumin", "turmeric", "paprika",
        "cinnamon", "nutmeg", "clove", "cardamom", "saffron", "vanilla", "mint", "basil",
        "oregano", "thyme", "rosemary", "sage", "parsley", "cilantro", "dill", "tarragon",
        "chives", "fennel", "anise", "bay", "lavender", "chamomile", "hibiscus", "jasmine",
        "rose", "violet", "daisy", "lily", "tulip", "orchid", "sunflower", "marigold",
        "carnation", "peony", "iris", "hyacinth", "daffodil", "crocus", "poppy", "lotus",
        "magnolia", "azalea", "rhododendron", "gardenia", "jasmine", "wisteria", "honeysuckle",
        "morning", "glory", "pansy", "primrose", "snapdragon", "sweet", "pea", "zinnia",
        "cosmos", "dahlia", "geranium", "begonia", "impatiens", "petunia", "salvia", "verbena",
        "aster", "chrysanthemum", "delphinium", "foxglove", "hollyhock", "larkspur", "lupine",
        "river", "mountain", "ocean", "forest", "desert", "valley", "canyon", "plateau",
        "island", "peninsula", "coast", "beach", "cliff", "cave", "waterfall", "lake",
        "pond", "stream", "creek", "brook", "spring", "marsh", "swamp", "delta",
        "glacier", "volcano", "geyser", "crater", "ridge", "peak", "summit", "slope",
        "meadow", "prairie", "savanna", "tundra", "taiga", "jungle", "rainforest", "woodland",
        "cloud", "rain", "snow", "hail", "sleet", "fog", "mist", "dew",
        "frost", "ice", "thunder", "lightning", "wind", "breeze", "gale", "hurricane",
        "tornado", "cyclone", "typhoon", "storm", "tempest", "drizzle", "shower", "downpour",
        "sun", "moon", "star", "planet", "comet", "asteroid", "meteor", "galaxy",
        "nebula", "constellation", "orbit", "eclipse", "equinox", "solstice", "aurora", "cosmos"
    ]
    return words


def generate_random_words(count=100):
    """
    Generate and return a list of random words.

    Args:
        count (int): Number of random words to generate (default: 100)

    Returns:
        list: A list of randomly selected words
    """
    words = get_word_list()
    return random.choices(words, k=count)


def main():
    """
    Main function to generate and print 100 random words.
    """
    random_words = generate_random_words(100)

    print("100 Random Words:")
    print("-" * 40)
    for i, word in enumerate(random_words, 1):
        print(f"{i:2d}. {word}")


if __name__ == "__main__":
    main()
