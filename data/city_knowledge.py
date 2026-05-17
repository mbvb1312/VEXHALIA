"""
Pre-populated knowledge base for three cities: Paris, Tokyo, New York.

These cities match the assignment document's examples. Each city's text
is split into fine-grained, topic-specific chunks (100–300 words each)
with category metadata. This "granularity" approach ensures that
semantic retrieval returns precisely relevant passages — e.g., a query
about "Tokyo food" retrieves the food chunk, not the transport chunk.

For any city NOT in this list, the agent's router automatically
switches to a live DuckDuckGo web search, so the system handles
any destination worldwide (e.g., Snohomish, Kyoto, Chennai).
"""

# Each entry maps a city name to a list of (text, category) tuples.
# The category metadata enables filtered retrieval and makes the
# vector store significantly more useful for targeted queries.

CITY_KNOWLEDGE: dict[str, list[tuple[str, str]]] = {
    "Paris": [
        (
            "Paris is the capital city of France and one of the most visited "
            "tourist destinations in the world. The city is known for its "
            "historic architecture, museums, art galleries, luxury shopping, "
            "cafés, and cultural landmarks. The Seine River flows through the "
            "center of Paris and divides the city into the Left Bank and Right "
            "Bank. With a population of approximately 2.1 million in the city "
            "proper and over 12 million in the metropolitan area, Paris is the "
            "economic, cultural, and political heart of France. The city has "
            "been a center of art, science, and philosophy since the Middle Ages.",
            "overview",
        ),
        (
            "Major tourist attractions in Paris include the Eiffel Tower, "
            "Louvre Museum, Notre-Dame Cathedral, Arc de Triomphe, "
            "Champs-Élysées, Sacré-Cœur Basilica, and the Palace of "
            "Versailles nearby. The Eiffel Tower is especially popular for "
            "panoramic city views during sunset and nighttime — it sparkles "
            "with 20,000 light bulbs every hour after dark. The Louvre is the "
            "world's largest art museum and home to the Mona Lisa. The "
            "Musée d'Orsay houses an extraordinary collection of Impressionist "
            "and Post-Impressionist masterpieces by Monet, Renoir, and Van Gogh.",
            "attractions",
        ),
        (
            "Paris is famous for French cuisine including croissants, "
            "baguettes, macarons, escargot, crêpes, cheese, and fine dining "
            "restaurants. Popular café culture is an important part of Parisian "
            "life — sitting at a sidewalk café watching the world go by is a "
            "quintessential Parisian experience. Travelers often visit local "
            "bakeries (boulangeries) and riverside cafés. The Marais district "
            "and Saint-Germain-des-Prés are known for exceptional bistros. "
            "Paris holds more Michelin-starred restaurants than any other city "
            "in the world. Street food favorites include crêpes from stands "
            "near the Seine and falafel in Le Marais.",
            "food",
        ),
        (
            "Paris experiences mild winters and warm summers. Average "
            "temperatures range from 3°C in January to 25°C in July. "
            "Spring (April–June) and autumn (September–November) are "
            "considered ideal seasons for tourism because of comfortable "
            "temperatures and fewer crowds. Rainfall is possible throughout "
            "the year — Paris receives approximately 640 mm annually — so "
            "travelers often carry umbrellas. Summer can occasionally bring "
            "heat waves exceeding 35°C. Winter days are short but the city's "
            "Christmas markets and holiday lights create a magical atmosphere.",
            "weather",
        ),
        (
            "Public transportation in Paris includes the Paris Métro (16 lines, "
            "300+ stations), buses, regional RER trains, and trams. The Métro "
            "system is one of the fastest and most affordable ways to travel "
            "across the city — a single ticket costs €2.15. Charles de Gaulle "
            "Airport (CDG) is the primary international airport serving Paris, "
            "located 25 km northeast. Orly Airport handles many European and "
            "domestic flights. The Gare du Nord train station connects Paris "
            "to London (Eurostar), Brussels, and Amsterdam by high-speed rail.",
            "transportation",
        ),
        (
            "Popular activities in Paris include Seine River cruises, museum "
            "visits, café hopping, luxury shopping on the Champs-Élysées and "
            "Rue du Faubourg Saint-Honoré, photography tours, art exploration, "
            "and guided walking tours through Montmartre. Nighttime river "
            "cruises (Bateaux Mouches) are especially popular among tourists "
            "for seeing illuminated landmarks. Outdoor activities include "
            "picnicking in the Luxembourg Gardens or Tuileries Garden, cycling "
            "along the Seine, and exploring the flea markets at Saint-Ouen. "
            "Paris is also an excellent base for day trips to Versailles, "
            "Giverny (Monet's gardens), and the Loire Valley châteaux.",
            "activities",
        ),
    ],
    "Tokyo": [
        (
            "Tokyo is the capital city of Japan and one of the largest "
            "metropolitan areas in the world with a population exceeding "
            "37 million in the greater metropolitan region. The city combines "
            "advanced technology, modern skyscrapers, anime culture, "
            "traditional temples, and highly efficient transportation systems. "
            "Tokyo served as the host city for the 2020 Summer Olympics. "
            "The city is divided into 23 special wards, each functioning as "
            "an individual city, along with several suburban cities and towns.",
            "overview",
        ),
        (
            "Major attractions in Tokyo include Tokyo Tower, Senso-ji Temple "
            "in Asakusa (the oldest temple in Tokyo, founded in 645 AD), "
            "Shibuya Crossing (the world's busiest pedestrian intersection), "
            "Tokyo Skytree (634 meters tall), Meiji Shrine surrounded by a "
            "vast forest, Akihabara electronics district, and the Imperial "
            "Palace. Akihabara is especially known for anime, manga, gaming, "
            "and electronics culture. The Tsukiji Outer Market remains a "
            "vibrant food destination despite the inner market's move to "
            "Toyosu. Odaiba is a futuristic waterfront area with shopping, "
            "entertainment, and the life-size Gundam statue.",
            "attractions",
        ),
        (
            "Tokyo is internationally known for sushi, ramen, tempura, "
            "yakitori, udon, tonkatsu, and street food. Tsukiji Outer Market "
            "and Toyosu Market are famous for the freshest seafood in the "
            "world. Convenience stores (konbini) like 7-Eleven, Lawson, and "
            "FamilyMart are known for surprisingly high-quality ready-to-eat "
            "meals, onigiri, and bento boxes. Tokyo has more Michelin-starred "
            "restaurants than any other city on Earth. Ramen alleys in "
            "Shinjuku and Ikebukuro offer dozens of specialized ramen shops. "
            "Themed cafés — including cat cafés, owl cafés, and robot "
            "restaurants — are uniquely Tokyo experiences.",
            "food",
        ),
        (
            "Tokyo has one of the most advanced public transportation systems "
            "in the world. The city relies heavily on trains (JR lines), "
            "subways (Tokyo Metro and Toei lines), and bullet trains known as "
            "Shinkansen that can reach speeds of 320 km/h. Tokyo Station and "
            "Shinjuku Station (the world's busiest station with 3.5 million "
            "daily passengers) are major transport hubs. A Suica or Pasmo IC "
            "card is essential for seamless travel. Narita International "
            "Airport (60 km from city center) and Haneda Airport (closer, "
            "more convenient) serve international flights.",
            "transportation",
        ),
        (
            "Tokyo experiences hot and humid summers with temperatures often "
            "exceeding 35°C and mild winters averaging 5–10°C. Cherry blossom "
            "(sakura) season during late March to mid-April is one of the most "
            "popular tourist periods — parks like Ueno, Shinjuku Gyoen, and "
            "Meguro River are famous viewing spots. The rainy season (tsuyu) "
            "runs from mid-June to mid-July. Typhoons can occasionally affect "
            "the city during late summer and autumn (August–October). Autumn "
            "foliage in November is stunning at temples and gardens.",
            "weather",
        ),
        (
            "Popular activities in Tokyo include anime and manga shopping in "
            "Akihabara, visiting arcades and game centers, themed cafés, "
            "temple visits and shrine ceremonies, nightlife exploration in "
            "Shinjuku's Golden Gai and Kabukichō, cherry blossom viewing "
            "(hanami), experiencing Japanese technology and robotics "
            "exhibitions at teamLab and Miraikan, and relaxing in traditional "
            "onsen (hot spring) baths. Day trips from Tokyo include Mount Fuji, "
            "Kamakura (Great Buddha), Nikko, and Hakone. Shopping districts "
            "include Ginza (luxury), Harajuku (youth fashion), and Shimokitazawa "
            "(vintage).",
            "activities",
        ),
    ],
    "New York": [
        (
            "New York City is the largest city in the United States with "
            "approximately 8.3 million residents and a major global center "
            "for finance, entertainment, media, art, fashion, and technology. "
            "The city consists of five boroughs: Manhattan, Brooklyn, Queens, "
            "The Bronx, and Staten Island. Situated at the mouth of the "
            "Hudson River on the Atlantic coast, its iconic skyline shaped by "
            "over 7,000 high-rise buildings is recognizable worldwide. New York "
            "is often called 'The City That Never Sleeps' because of its "
            "24-hour culture of dining, entertainment, and transportation.",
            "overview",
        ),
        (
            "Major attractions in New York City include Times Square (drawing "
            "50 million visitors annually), Central Park (843 acres of green "
            "space in Manhattan), the Statue of Liberty on Liberty Island, "
            "Empire State Building, Brooklyn Bridge, Broadway theater district "
            "(40+ professional theaters), Wall Street and the Financial "
            "District, the Metropolitan Museum of Art (The Met), the Museum "
            "of Modern Art (MoMA), and the 9/11 Memorial and Museum. The "
            "High Line, an elevated park built on a former railway, offers "
            "unique views of the city's west side.",
            "attractions",
        ),
        (
            "New York City is famous for its thin-crust pizza (folded for "
            "eating on the go), bagels with lox and cream cheese, pastrami "
            "on rye from delis like Katz's, cheesecake from Junior's in "
            "Brooklyn, and hot dogs from street carts. The city hosts over "
            "27,000 restaurants representing virtually every cuisine on earth "
            "— from dim sum in Flushing's Chinatown to Ethiopian injera in "
            "Harlem to Neapolitan pizza in the West Village. Food trucks and "
            "street vendors selling halal platters, pretzels, and roasted "
            "nuts are iconic parts of the New York street scene.",
            "food",
        ),
        (
            "The New York City Subway operates 24 hours a day, 7 days a week, "
            "across 472 stations — more than any other system in the world. "
            "A single ride costs $2.90 with unlimited transfers within two "
            "hours. The system carries roughly 3.5 million riders on an "
            "average weekday. Yellow taxis are ubiquitous in Manhattan, while "
            "ride-share services (Uber, Lyft) and the Citi Bike program "
            "provide additional transit options. JFK International Airport, "
            "LaGuardia Airport, and Newark Liberty Airport serve the "
            "metropolitan area.",
            "transportation",
        ),
        (
            "New York City experiences cold winters with temperatures often "
            "dropping below freezing (average January high: 3°C) and warm, "
            "humid summers (average July high: 30°C). Snowfall is common "
            "from December through March. Spring (April–June) and autumn "
            "(September–November) are considered the most pleasant seasons "
            "for tourism and outdoor activities, with temperatures between "
            "15–25°C. Summer can be uncomfortable with heat and humidity. "
            "The holiday season (November–January) brings magical Christmas "
            "decorations, the Rockefeller Center tree, and ice skating rinks.",
            "weather",
        ),
        (
            "Popular activities in New York City include Broadway shows and "
            "musicals, rooftop dining with skyline views, museum visits (The "
            "Met, MoMA, Guggenheim, American Museum of Natural History), "
            "shopping in Manhattan (Fifth Avenue, SoHo), walking through "
            "Central Park, ferry rides to the Statue of Liberty and Ellis "
            "Island, nightlife in the Meatpacking District and Williamsburg, "
            "and attending sports events at Madison Square Garden and Yankee "
            "Stadium. Free activities include walking the Brooklyn Bridge, "
            "the Staten Island Ferry, and exploring neighborhood street art.",
            "activities",
        ),
    ],
}


def get_all_chunks() -> list[tuple[str, str, str]]:
    """Return every chunk as (city_name, text, category) triples for embedding.

    The category metadata is stored alongside each document in ChromaDB
    to enable filtered retrieval (e.g., only retrieve 'food' chunks).
    """
    triples = []
    for city, chunks in CITY_KNOWLEDGE.items():
        for text, category in chunks:
            triples.append((city, text, category))
    return triples


def get_city_names() -> list[str]:
    """Return the list of cities we have knowledge about."""
    return list(CITY_KNOWLEDGE.keys())
