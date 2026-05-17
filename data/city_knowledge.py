"""
Pre-populated knowledge base for four cities across India and the USA.

This data seeds the ChromaDB vector store so the agent can answer
questions about Chennai, Mumbai, New Jersey, and New York without
hitting the web. Each city's text is broken into thematic chunks that
embed well — shorter, focused paragraphs retrieve more accurately than
one giant wall of text.

For any city NOT in this list, the agent's router automatically
switches to a live DuckDuckGo web search, so there is no geographic
bias — users from any country will get results.
"""

# Each entry maps a city name to a list of text chunks.
# Chunks are kept under ~200 words so the embedding model
# can capture the semantic focus of each paragraph.

CITY_KNOWLEDGE: dict[str, list[str]] = {
    "Chennai": [
        (
            "Chennai, formerly known as Madras, is the capital city of Tamil "
            "Nadu and the largest cultural, economic, and educational hub in "
            "South India. Situated on the Coromandel Coast along the Bay of "
            "Bengal, the city has a population of roughly 7.1 million in the "
            "urban area and over 11 million in the greater metropolitan region. "
            "It is one of the oldest modern cities in the Indian subcontinent, "
            "with a history stretching back to the founding of Fort St. George "
            "by the British East India Company in 1644."
        ),
        (
            "Marina Beach stretches for 13 kilometers along the Bay of Bengal "
            "and is one of the longest urban beaches in the world. At sunrise "
            "and sunset the beach comes alive with families, street food "
            "vendors selling sundal and murukku, and cricket matches on the "
            "sand. The Kapaleeshwarar Temple in Mylapore, built in the 7th "
            "century Dravidian architectural style, is dedicated to Lord Shiva "
            "and features an ornate gopuram tower covered in colorful "
            "sculptures. The San Thome Basilica, believed to be built over the "
            "tomb of the apostle St. Thomas, is one of only three churches in "
            "the world built over the tomb of an apostle."
        ),
        (
            "Chennai is widely regarded as the gateway to South Indian "
            "cuisine. Filter coffee, served in a stainless steel tumbler and "
            "davara, is a morning ritual across the city. Idli, dosa, vada, "
            "and sambar form the backbone of breakfast menus, while lunch "
            "often means a traditional banana-leaf meal with rice, rasam, "
            "kootu, poriyal, and payasam. The city's Chettinad restaurants "
            "serve fiery chicken and mutton dishes seasoned with freshly "
            "ground spice blends. Street food hubs like Sowcarpet and "
            "Mylapore offer everything from pani puri to kothu parotta at "
            "incredibly affordable prices."
        ),
        (
            "The Chennai Metro and MRTS suburban railway connect key parts "
            "of the city, complementing the extensive bus network run by MTC. "
            "Auto-rickshaws, now increasingly app-metered, remain a popular "
            "last-mile transport option. The city is also the automobile "
            "capital of India, often called the 'Detroit of Asia,' with "
            "major manufacturing plants for Hyundai, BMW, Ford, and others. "
            "Chennai International Airport at Tirusulam handles both domestic "
            "and international flights, with direct connections to Singapore, "
            "Dubai, London, and several Southeast Asian cities."
        ),
        (
            "The best time to visit Chennai is from November to February when "
            "temperatures range from 20 to 30 degrees Celsius and the humidity "
            "is lower. Summer months from April to June are extremely hot with "
            "temperatures often exceeding 40 degrees Celsius. The northeast "
            "monsoon season, from October to December, brings heavy rainfall "
            "that can occasionally cause urban flooding. Despite the heat, "
            "Chennai's cultural calendar is vibrant year-round, highlighted by "
            "the six-week Margazhi music and dance festival from December to "
            "January, which draws classical artists from across the world."
        ),
        (
            "Chennai has a thriving IT corridor in areas like Sholinganallur, "
            "OMR (Old Mahabalipuram Road), and Taramani, housing offices of "
            "TCS, Infosys, Cognizant, and numerous startups. The city is also "
            "a center for the Tamil film industry (Kollywood), producing over "
            "200 films annually. The Government Museum in Egmore, one of the "
            "oldest in India, has an extensive collection of archaeological "
            "artifacts, bronze sculptures, and botanical specimens."
        ),
    ],
    "Mumbai": [
        (
            "Mumbai, formerly Bombay, is the capital of Maharashtra and the "
            "financial capital of India. Built across seven islands on the "
            "western coast, it is the most populous city in India with over "
            "20 million residents in the metropolitan region. The city serves "
            "as headquarters for the Reserve Bank of India, the Bombay Stock "
            "Exchange (Asia's oldest), and the Securities and Exchange Board. "
            "It generates approximately 6.16 percent of India's total GDP."
        ),
        (
            "The Gateway of India, an Indo-Saracenic arch monument built in "
            "1924 to commemorate King George V's visit, stands at the tip of "
            "Apollo Bunder and overlooks Mumbai Harbour. From here, ferries "
            "depart to Elephanta Island, whose 5th-century cave temples house "
            "remarkable Shiva sculptures and are a UNESCO World Heritage Site. "
            "The Chhatrapati Shivaji Maharaj Terminus (formerly Victoria "
            "Terminus), another UNESCO site, is an extraordinary example of "
            "Victorian Gothic Revival architecture blended with traditional "
            "Indian elements."
        ),
        (
            "Mumbai street food is legendary and forms the backbone of the "
            "city's culinary identity. Vada pav — a spiced potato fritter in "
            "a bun with chutneys — is the quintessential Mumbai snack, sold "
            "by thousands of vendors for as little as 20 rupees. Pav bhaji, "
            "bhel puri, sev puri, and pani puri line the stalls at Chowpatty "
            "Beach and Juhu Beach. For sit-down meals, the city offers "
            "everything from Parsi cafés serving dhansak and berry pulao to "
            "Mughlai restaurants in Mohammed Ali Road known for seekh kebabs "
            "and malpua during Ramadan."
        ),
        (
            "Mumbai's local train network, often called the lifeline of the "
            "city, carries over 7.5 million passengers daily across three "
            "main lines: Western, Central, and Harbour. The trains run from "
            "roughly 4 AM to 1 AM and a monthly pass costs around 200-300 "
            "rupees. The Mumbai Metro has been expanding rapidly with new "
            "lines reducing congestion. Black-and-yellow taxis and auto-"
            "rickshaws (in the suburbs) complement the public transit, "
            "alongside ride-hailing apps like Ola and Uber."
        ),
        (
            "The best time to visit Mumbai is from October to March when "
            "temperatures stay between 20 and 33 degrees Celsius with low "
            "humidity. The monsoon season from June to September brings "
            "intense rainfall — the city averages about 2,400 mm annually — "
            "which can disrupt transportation but also transforms the "
            "surrounding Western Ghats into lush green landscapes. If you "
            "do not mind the rain, monsoon Mumbai has its own dramatic charm."
        ),
        (
            "Bollywood, the Hindi film industry based in Mumbai's Film City "
            "complex in Goregaon, produces over 1,500 films annually, making "
            "it the largest film industry in the world by output. The city's "
            "nightlife centers around Bandra, Lower Parel, and Colaba, with "
            "rooftop bars, live music venues, and clubs that stay open past "
            "midnight. Marine Drive, the 3.6-kilometer-long boulevard along "
            "the coast, is nicknamed the 'Queen's Necklace' for its curved "
            "line of streetlights that glow at night."
        ),
    ],
    "New Jersey": [
        (
            "New Jersey is a state in the Mid-Atlantic region of the United "
            "States, bordered by New York to the north, the Atlantic Ocean to "
            "the east, and Pennsylvania and Delaware to the west and south. "
            "Despite being the fourth-smallest state by area, it is the most "
            "densely populated state in the country with around 9.3 million "
            "residents. Its proximity to both New York City and Philadelphia "
            "makes it a major commuter hub, earning the nickname 'The Garden "
            "State' for its farms, forests, and shore communities."
        ),
        (
            "The Jersey Shore stretches 130 miles along the Atlantic Coast "
            "and includes famous beach towns like Atlantic City, Cape May, "
            "Asbury Park, and Point Pleasant. Atlantic City's Boardwalk, "
            "built in 1870 as the world's first boardwalk, features casinos, "
            "amusement rides, and saltwater taffy shops. Cape May, at the "
            "state's southern tip, is a National Historic Landmark with "
            "over 600 beautifully preserved Victorian-era buildings and "
            "is known for excellent bird watching and whale-watching tours."
        ),
        (
            "New Jersey offers remarkable culinary diversity thanks to its "
            "position as a melting pot of cultures. The state claims to have "
            "the best pizza and bagels outside of New York City — a fiercely "
            "debated but widely held local belief. Diners are a cultural "
            "institution here; New Jersey has more diners per capita than "
            "any other state, serving classic American comfort food 24 hours "
            "a day. The state is also home to significant Indian, Korean, "
            "and Latin American food communities, particularly along the "
            "Oak Tree Road corridor in Edison and Iselin."
        ),
        (
            "NJ Transit operates an extensive bus and commuter rail network "
            "that connects cities and suburbs across the state to New York "
            "Penn Station and Hoboken Terminal. The PATH train links Newark, "
            "Hoboken, and Jersey City directly to Manhattan. Newark Liberty "
            "International Airport is one of the busiest airports on the "
            "East Coast, serving as a major United Airlines hub. The New "
            "Jersey Turnpike and Garden State Parkway are the state's main "
            "highway arteries."
        ),
        (
            "The best time to visit New Jersey is from May to October when "
            "temperatures are warm enough for beach activities, typically "
            "ranging from 18 to 30 degrees Celsius. Autumn (September through "
            "November) is particularly stunning in the northwestern highlands "
            "with vibrant fall foliage. Winters can be cold, with temperatures "
            "dropping below freezing and snowfall common from December through "
            "March, especially in the northern counties."
        ),
        (
            "Princeton University, one of the world's most prestigious "
            "institutions, is located in the town of Princeton and its campus "
            "is open for guided walking tours. Liberty State Park in Jersey "
            "City provides spectacular views of the Statue of Liberty and the "
            "Manhattan skyline across the Hudson River. The Thomas Edison "
            "National Historical Park in West Orange preserves the laboratory "
            "and estate of America's most prolific inventor."
        ),
    ],
    "New York": [
        (
            "New York City is the most populous city in the United States, "
            "with approximately 8.3 million residents spread across five "
            "boroughs: Manhattan, Brooklyn, Queens, the Bronx, and Staten "
            "Island. Situated at the mouth of the Hudson River on the "
            "Atlantic coast, it serves as a global nexus of finance, media, "
            "art, fashion, and technology. The city's iconic skyline, shaped "
            "by over 7,000 high-rise buildings, is recognizable worldwide."
        ),
        (
            "The Statue of Liberty, a gift from France dedicated in 1886, "
            "stands on Liberty Island in New York Harbor and has welcomed "
            "millions of immigrants arriving by sea. Central Park, designed "
            "by Frederick Law Olmsted and Calvert Vaux, spans 843 acres of "
            "Manhattan and receives roughly 42 million visitors annually, "
            "making it the most-visited urban park in the United States. "
            "The park contains lakes, woodlands, a zoo, ice-skating rinks, "
            "and the Bethesda Terrace fountain."
        ),
        (
            "Times Square, dubbed 'The Crossroads of the World,' is a major "
            "commercial and entertainment hub in Midtown Manhattan. Its "
            "massive illuminated billboards and Broadway theater marquees "
            "draw an estimated 50 million visitors each year. The Broadway "
            "theater district hosts around 40 professional theaters staging "
            "musicals, dramas, and revivals. Iconic shows include The Phantom "
            "of the Opera, Hamilton, and The Lion King."
        ),
        (
            "New York's food scene reflects its extraordinary diversity. "
            "Classic New York foods include thin-crust pizza (folded for "
            "eating on the go), bagels with lox and cream cheese, pastrami "
            "on rye from delis like Katz's, and cheesecake from Junior's in "
            "Brooklyn. The city hosts over 27,000 restaurants representing "
            "virtually every cuisine on earth — from dim sum in Flushing's "
            "Chinatown to Ethiopian injera in Harlem to Neapolitan pizza in "
            "the West Village."
        ),
        (
            "The New York City Subway operates 24 hours a day, 7 days a "
            "week, across 472 stations — more than any other system in the "
            "world. A single MetroCard swipe costs $2.90 and provides "
            "unlimited transfers within two hours. The system carries roughly "
            "3.5 million riders on an average weekday. Yellow taxis are "
            "ubiquitous in Manhattan, while ride-share services and the Citi "
            "Bike program provide additional transit options."
        ),
        (
            "The best time to visit New York is from April to June and "
            "September to early November. Spring brings cherry blossoms in "
            "Central Park and mild temperatures around 15 to 22 degrees "
            "Celsius. Autumn offers spectacular foliage and comfortable "
            "weather. Summer (July-August) can be uncomfortably hot and "
            "humid, regularly exceeding 32 degrees Celsius, while winter "
            "brings cold temperatures, occasional snowstorms, and the "
            "magical holiday season with the Rockefeller Center Christmas "
            "tree and window displays along Fifth Avenue."
        ),
    ],
}


def get_all_chunks() -> list[tuple[str, str]]:
    """Return every chunk as (city_name, text) pairs for embedding."""
    pairs = []
    for city, chunks in CITY_KNOWLEDGE.items():
        for chunk in chunks:
            pairs.append((city, chunk))
    return pairs


def get_city_names() -> list[str]:
    """Return the list of cities we have knowledge about."""
    return list(CITY_KNOWLEDGE.keys())
