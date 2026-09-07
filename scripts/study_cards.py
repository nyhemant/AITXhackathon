"""Per-card study decks (Easy + Hard + Zoologist).

Facts for african-lion are Wikipedia-backed:
https://en.wikipedia.org/wiki/Lion
Do not invent stats. Soften contested numbers. Roar distance may cite
“about 8 km / 5 miles (Wikipedia).”

Facts for reticulated-giraffe Junior Ranger + Park Ranger + Zoologist
(easy + hard + zoologist) are Wikipedia-backed:
https://en.wikipedia.org/wiki/Giraffe
https://en.wikipedia.org/wiki/Reticulated_giraffe
Soften tongue length (no cm) and Kenya-only range. Home is African
savannah / open woodland. Hard softens sprint speed, sleep hours,
newborn height, and IUCN letters amid the species split. Zoologist
softens exact mmHg and treats multi-species recognition as debate,
not a forever rule.

Facts for african-elephant Junior Ranger + Park Ranger + Zoologist
(easy + hard + zoologist) are Wikipedia-backed:
https://en.wikipedia.org/wiki/African_elephant
https://en.wikipedia.org/wiki/Elephant
The largest/heaviest living-land-animal fact may use African elephant
wording (bush-elephant size). Soften the jump myth: elephants cannot
jump — do not say “only mammal on Earth.” Hard softens trunk-muscle
counts (tens of thousands, no single 40k–60k lock). Zoologist holds
bush vs forest / Loxodonta, softens TP53 copy counts, and does not
lock Endangered vs Critically Endangered letters. Park Ranger
vs-Asian is ear size / back shape only.

Facts for african-penguin Junior Ranger + Park Ranger + Zoologist
(easy + hard + zoologist) are Wikipedia-backed:
https://en.wikipedia.org/wiki/African_penguin
Home is southern African coasts, not Antarctica. Soften IUCN
Critically Endangered / exact status letters and pair counts. JR
does not lock brittle status letters. Hard prefers threats and
mechanisms (prey-fish shortage, guano loss) over status letters.
Zoologist deepens genus, osmoregulation, named countershading,
patch blood-flow, decline drivers, fisheries, no-take zones, and
pursuit diving — without locking IUCN letters, exact % decline,
or max dive depth/time.

Facts for caribbean-flamingo Junior Ranger (easy) are Wikipedia-backed:
https://en.wikipedia.org/wiki/American_flamingo
Also known as the Caribbean flamingo (Phoenicopterus ruber).
Adults are reddish-pink; chicks start greyish. Pink comes from food
(carotenoids), not paint. They stand on one leg, feed in shallow
water, nest on a mud mound, and are strong fliers. JR uses flock
(Wikipedia’s common word), not “flamboyance” as the required
group name. Soften IUCN letters and exact heights.

Slot numbers stay 1–10. Hard and Zoologist deepen different themes
(not a redo of Easy or of each other). Internal keys stay easy / hard /
zoologist. Visible copy uses LEVEL_DISPLAY_NAMES only — no age badges,
no plain Easy / Hard labels.
"""

from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
FIELD = REPO / "static" / "field-pack"
STUDY_JSON = FIELD / "data" / "study-cards.json"
STUDY_DATA_JS = FIELD / "js" / "study-cards-data.js"

# https://en.wikipedia.org/wiki/Lion — source for Easy facts (not invented).
WIKI_LION = "https://en.wikipedia.org/wiki/Lion"
WIKI_GIRAFFE = "https://en.wikipedia.org/wiki/Giraffe"
WIKI_RETICULATED_GIRAFFE = "https://en.wikipedia.org/wiki/Reticulated_giraffe"
WIKI_AFRICAN_ELEPHANT = "https://en.wikipedia.org/wiki/African_elephant"
WIKI_ELEPHANT = "https://en.wikipedia.org/wiki/Elephant"
WIKI_AFRICAN_PENGUIN = "https://en.wikipedia.org/wiki/African_penguin"
WIKI_AMERICAN_FLAMINGO = "https://en.wikipedia.org/wiki/American_flamingo"

LETTERS = ("A", "B", "C")
STUDY_SLOTS = 10
DEFAULT_LEVEL = "easy"

# Product display names — one map for screen, print, and later pickers.
LEVEL_DISPLAY_NAMES = {
    "easy": "Junior Ranger",
    "hard": "Park Ranger",
    "zoologist": "Zoologist",
}

# Shipped picker order. A card only shows keys it actually defines.
# Lion, reticulated-giraffe, African elephant, and African penguin
# ship Junior Ranger + Park Ranger + Zoologist. Caribbean flamingo
# ships Junior Ranger only.
SHIPPED_LEVELS = ("easy", "hard", "zoologist")
ANSWER_LIGHT_LEVELS = frozenset({"hard", "zoologist"})

# Shared answers-side deepen (Claude sample). Not scored. Future animals reuse keys.
TALK_ABOUT_LION = (
    "Why is it useful for lions to live in a family instead of alone?",
    "If you could hear something 5 miles away, what would you listen for?",
    "Which other animal at the zoo lives in a family group?",
)
PUSH_FURTHER_LION = (
    "A mane makes a male slower, hotter and more visible. Why hasn’t evolution removed it?",
    "Lions and cheetahs share the same plains. How do they avoid competing directly?",
    "Find one more animal on your zoo map that lives in a group. What does the group give it?",
)
TALK_ABOUT_GIRAFFE = (
    "Why might a long neck help a giraffe besides reaching high leaves?",
    "If you stood as tall as a giraffe, what would you notice first at the zoo?",
    "Which other animal at the zoo has a special tongue or a long neck?",
)
PUSH_FURTHER_GIRAFFE = (
    "A giraffe must spread its front legs to drink. What risk could that pose in the wild?",
    "Each giraffe’s spots are unique. How could that help a keeper tell them apart?",
    "Find one more animal on your zoo map that eats leaves from trees. How does it reach them?",
)
TALK_ABOUT_ELEPHANT = (
    "Why might a trunk be more useful than hands at the zoo?",
    "If you had ears as big as an elephant’s, how would you stay cool?",
    "Which other animal at the zoo lives in a family group?",
)
PUSH_FURTHER_ELEPHANT = (
    "An elephant’s trunk can grab, drink, and smell. What job would you give it first?",
    "A herd follows the oldest female. Why might the oldest be a good leader?",
    "Find one more big animal on your zoo map. How does it move if it cannot jump?",
)
TALK_ABOUT_PENGUIN = (
    "Why might living in a colony help a penguin?",
    "If you could “fly” underwater with flippers, what would you look for?",
    "Which other animal at the zoo lives near the water?",
)
PUSH_FURTHER_PENGUIN = (
    "A penguin’s coat is dark on top and pale below. How could that hide it from hunters?",
    "African penguins nest on warm shores, not ice. Why might people think all penguins live somewhere cold?",
    "Find one more bird on your zoo map that swims. How does it move in the water?",
)
TALK_ABOUT_FLAMINGO = (
    "Why might standing on one leg help a flamingo?",
    "If you had a long, bendy neck, what would you look at first at the zoo?",
    "Which other animal at the zoo lives near the water?",
)
PUSH_FURTHER_FLAMINGO = (
    "A flamingo’s pink colour comes from its food. What would happen if it ate different food?",
    "Flamingos can fly, even though people often see them only wading. Why might people miss that?",
    "Find one more bird on your zoo map that stands in water. How does it use its legs or beak?",
)

# Easy + Hard + Zoologist ship on the same african-lion card.
STUDY_CARDS: dict[str, dict] = {
    "african-lion": {
        "id": "african-lion",
        "source": WIKI_LION,
        "source_note": "Facts from Wikipedia, Lion.",
        "talk_about": list(TALK_ABOUT_LION),
        "push_further": list(PUSH_FURTHER_LION),
        "levels": {
            "easy": {
                # Teaching-first: same front as the quiz. Hard later may hide these.
                "teach": [
                    "A group of lions is a pride.",
                    "A baby is a cub.",
                    "They live on grasslands / savannah, not jungle.",
                    "Their famous sound is a roar.",
                    "Male lions often grow a big mane.",
                ],
                "questions": [
                    {
                        "slot": 1,
                        "id": "family",
                        "title": "Family",
                        "stem": "What do you call a group of lions?",
                        "choices": ["A pack", "A pride", "A herd"],
                        "correct": "B",
                        "why": "Lions live together in a pride — a social group that shares space and raises cubs.",
                    },
                    {
                        "slot": 2,
                        "id": "food",
                        "title": "Food",
                        "stem": "What do lions mostly eat?",
                        "choices": ["Grass", "Fruit", "Meat"],
                        "correct": "C",
                        "why": "Lions eat meat. They mostly hunt hooved animals such as zebra, wildebeest, and antelope.",
                    },
                    {
                        "slot": 3,
                        "id": "voice",
                        "title": "Voice",
                        "stem": "What sound is a lion famous for?",
                        "choices": ["A moo", "A roar", "A squeak"],
                        "correct": "B",
                        "why": "A lion’s roar can travel a long way — about 8 km / 5 miles (Wikipedia).",
                    },
                    {
                        "slot": 4,
                        "id": "mane",
                        "title": "Body",
                        "stem": "Which lion usually grows a big fluffy mane?",
                        "choices": ["The male", "The female", "Both"],
                        "correct": "A",
                        "why": "Male lions often grow a big mane around the head and neck.",
                    },
                    {
                        "slot": 5,
                        "id": "young",
                        "title": "Young",
                        "stem": "What is a baby lion called?",
                        "choices": ["A calf", "A chick", "A cub"],
                        "correct": "C",
                        "why": "A baby lion is a cub. Many cubs have faint spots that fade as they grow.",
                    },
                    {
                        "slot": 6,
                        "id": "home",
                        "title": "Home",
                        "stem": "Where do wild lions mostly live?",
                        "choices": ["Thick jungle", "Grassland / savannah", "Deep ocean"],
                        "correct": "B",
                        "why": "Wild lions mostly live on grassland, savannah, and shrubland — rarely in closed forest.",
                    },
                    {
                        "slot": 7,
                        "id": "rest",
                        "title": "Rest",
                        "stem": "How much of the day do lions often spend resting?",
                        "choices": ["About 2 hours", "About 8 hours", "About 20 hours"],
                        "correct": "C",
                        "why": "Lions often rest or stay inactive for about 20 hours a day.",
                    },
                    {
                        "slot": 8,
                        "id": "hunting",
                        "title": "Hunting",
                        "stem": "In a pride, who usually does most of the hunting?",
                        "choices": ["The dads", "The moms (lionesses)", "The cubs"],
                        "correct": "B",
                        "why": "In a pride, lionesses usually do most of the hunting, often together.",
                    },
                    {
                        "slot": 9,
                        "id": "tail",
                        "title": "Body",
                        "stem": "What special tip does a lion’s tail have?",
                        "choices": ["Feathers", "A dark hairy tuft", "A shell"],
                        "correct": "B",
                        "why": "A lion’s tail ends in a dark hairy tuft.",
                    },
                    {
                        "slot": 10,
                        "id": "myth",
                        "title": "Myth buster",
                        "stem": "Do lions really live in a jungle like in some cartoons?",
                        "choices": ["Yes, always", "No — mostly open grassland", "Only in snow"],
                        "correct": "B",
                        "why": "Cartoons show jungle lions, but wild lions mostly live on open grassland.",
                    },
                ],
            },
            "hard": {
                # Answer-light: no Learn-first strip. Facts from Wikipedia, Lion.
                "teach": [],
                "questions": [
                    {
                        "slot": 1,
                        "id": "name",
                        "title": "Name",
                        "stem": "What is the lion’s scientific name?",
                        "choices": ["Felis catus", "Panthera leo", "Canis lupus"],
                        "correct": "B",
                        "why": "The lion is a large cat in the genus Panthera. Its scientific name is Panthera leo.",
                    },
                    {
                        "slot": 2,
                        "id": "pride-core",
                        "title": "Pride",
                        "stem": "In a typical pride, who forms the stable core?",
                        "choices": [
                            "A pack of unrelated males",
                            "Related females and their cubs",
                            "Only cubs with no adults",
                        ],
                        "correct": "B",
                        "why": "A pride’s stable core is related females and cubs. Adult males are usually unrelated to those females.",
                    },
                    {
                        "slot": 3,
                        "id": "prey",
                        "title": "Prey",
                        "stem": "What do wild lions mostly hunt?",
                        "choices": [
                            "Tiny prey like hares and monkeys",
                            "Medium and large hooved mammals",
                            "Only fish",
                        ],
                        "correct": "B",
                        "why": "Lions mostly hunt medium-sized and large hooved mammals such as zebra, wildebeest, and buffalo — not tiny prey as their main diet.",
                    },
                    {
                        "slot": 4,
                        "id": "speed",
                        "title": "Speed",
                        "stem": "How do lions usually chase prey?",
                        "choices": [
                            "Long stamina runs for many miles",
                            "Short fast bursts of about 30–37 mph",
                            "They never run",
                        ],
                        "correct": "B",
                        "why": "Lions have quick burst speed of about 48–59 km/h (30–37 mph) but little stamina, so they do not run long chases.",
                    },
                    {
                        "slot": 5,
                        "id": "status",
                        "title": "Status",
                        "stem": "How does the IUCN list wild lions today?",
                        "choices": ["Least Concern", "Vulnerable", "Extinct in the wild"],
                        "correct": "B",
                        "why": "Lions have been listed as Vulnerable on the IUCN Red List. African populations have declined sharply in recent decades.",
                    },
                    {
                        "slot": 6,
                        "id": "asia",
                        "title": "Range",
                        "stem": "Where do wild Asiatic lions live today?",
                        "choices": [
                            "All across Asia",
                            "Mainly Gir National Park in western India",
                            "Only in zoos",
                        ],
                        "correct": "B",
                        "why": "Wild Asiatic lions today survive mainly in and around Gir National Park in Gujarat, western India.",
                    },
                    {
                        "slot": 7,
                        "id": "cub-senses",
                        "title": "Cubs",
                        "stem": "When can a newborn lion cub see?",
                        "choices": [
                            "It is born with eyes already open",
                            "Eyes open around a week after birth",
                            "Eyes stay closed for a year",
                        ],
                        "correct": "B",
                        "why": "Lion cubs are born blind. Their eyes open around seven days after birth.",
                    },
                    {
                        "slot": 8,
                        "id": "gestation",
                        "title": "Birth",
                        "stem": "About how long is a lioness’s pregnancy, and how many cubs are usual?",
                        "choices": [
                            "About 110 days; often 1–4 cubs",
                            "About 30 days; often 12 cubs",
                            "About two years; one cub only",
                        ],
                        "correct": "A",
                        "why": "Gestation is about 110 days. A litter is often between one and four cubs.",
                    },
                    {
                        "slot": 9,
                        "id": "takeover",
                        "title": "Takeover",
                        "stem": "What often happens to young cubs when new males take over a pride?",
                        "choices": [
                            "The new males adopt every cub",
                            "The new males often kill existing young cubs",
                            "Cubs immediately leave to hunt alone",
                        ],
                        "correct": "B",
                        "why": "When new males oust the previous males, they often kill existing young cubs. Females then become ready to mate sooner.",
                    },
                    {
                        "slot": 10,
                        "id": "white-lion",
                        "title": "Color",
                        "stem": "What makes a white lion white?",
                        "choices": [
                            "It is a true albino with pink eyes",
                            "A rare pale morph from leucism, with normal eye and skin pigment",
                            "It is painted by keepers",
                        ],
                        "correct": "B",
                        "why": "White lions are a rare pale morph caused by leucism, not true albinism. They still have normal pigmentation in the eyes and skin.",
                    },
                ],
            },
            "zoologist": {
                # Answer-light: no Learn-first strip. Facts from Wikipedia, Lion.
                "teach": [],
                "questions": [
                    {
                        "slot": 1,
                        "id": "roar-anatomy",
                        "title": "Roar",
                        "stem": "What helps a lion roar, unlike a house cat’s continuous purr?",
                        "choices": [
                            "A fully stiff hyoid bone like a house cat",
                            "A stretchy hyoid ligament (not a fully stiff bone)",
                            "Hollow horns that amplify sound",
                        ],
                        "correct": "B",
                        "why": "One reason lions can roar is a stretchy hyoid ligament in the throat — not a fully stiff bone like a house cat. They do not make a house cat’s continuous purr.",
                    },
                    {
                        "slot": 2,
                        "id": "flehmen",
                        "title": "Scent",
                        "stem": "When a lion curls its lips in a flehmen grimace, where does the scent go?",
                        "choices": [
                            "Straight into the lungs only",
                            "Toward the vomeronasal organ",
                            "Into the ear canal",
                        ],
                        "correct": "B",
                        "why": "The flehmen face (open mouth, wrinkled nose) helps a lion sniff chemical signals. The lip-curl routes scent toward the vomeronasal organ, a special smell sensor.",
                    },
                    {
                        "slot": 3,
                        "id": "carnassials",
                        "title": "Teeth",
                        "stem": "What are a lion’s carnassial teeth built to do?",
                        "choices": [
                            "Grind grass like a cow",
                            "Shear meat with blade-like cheek teeth (upper P4 / lower m1)",
                            "Hold water",
                        ],
                        "correct": "B",
                        "why": "Carnassials are blade-like cheek teeth — the upper fourth premolar and lower first molar — that shear meat.",
                    },
                    {
                        "slot": 4,
                        "id": "subspecies",
                        "title": "Species",
                        "stem": "Which two living lion subspecies do scientists recognize today?",
                        "choices": [
                            "Cave lion and American lion",
                            "Panthera leo leo and Panthera leo melanochaita",
                            "Only the Barbary lion",
                        ],
                        "correct": "B",
                        "why": "In 2017 the Cat Specialist Group recognized two living subspecies: P. l. leo and P. l. melanochaita. Cave lions and American lions are extinct relatives, not living subspecies.",
                    },
                    {
                        "slot": 5,
                        "id": "tail-spur",
                        "title": "Tail",
                        "stem": "What can hide inside a lion’s dark tail tuft?",
                        "choices": [
                            "A venom stinger",
                            "A small hard spur; its function is unknown",
                            "A second claw used for climbing",
                        ],
                        "correct": "B",
                        "why": "In some lions the dark tail tuft hides a small hard spur. Wikipedia notes its function is unknown.",
                    },
                    {
                        "slot": 6,
                        "id": "takeover-estrus",
                        "title": "Takeover",
                        "stem": "Why do new males often kill young cubs after taking over a pride?",
                        "choices": [
                            "So females return to estrus and can mate sooner",
                            "To teach cubs to hunt",
                            "Because cubs eat only plants",
                        ],
                        "correct": "A",
                        "why": "Females usually do not become ready to mate again until their cubs grow up or die. Killing young cubs often brings females back into estrus sooner.",
                    },
                    {
                        "slot": 7,
                        "id": "most-social",
                        "title": "Society",
                        "stem": "How do lions compare with other wild cats?",
                        "choices": [
                            "They are the most social of wild cats, living in prides",
                            "They are the only cats that never meet",
                            "They are less social than typical solitary big cats",
                        ],
                        "correct": "A",
                        "why": "The lion is the most social of all wild felid species. Related females and cubs form a pride — unlike typical solitary big cats.",
                    },
                    {
                        "slot": 8,
                        "id": "decline-drivers",
                        "title": "Decline",
                        "stem": "What are the greatest causes for concern in the lion’s decline?",
                        "choices": [
                            "Too much rain only",
                            "Habitat loss and conflict with people",
                            "Lions moving to the deep ocean",
                        ],
                        "correct": "B",
                        "why": "The exact drop is not fully understood, but habitat loss and conflicts with people are the greatest concerns. Lions are still listed as Vulnerable.",
                    },
                    {
                        "slot": 9,
                        "id": "burst-muscle",
                        "title": "Muscle",
                        "stem": "Why do lions hunt with short rushes instead of long chases?",
                        "choices": [
                            "They have a high share of fast-twitch muscle and little stamina",
                            "They have no leg muscles",
                            "They prefer to fly",
                        ],
                        "correct": "A",
                        "why": "Lion muscle has a high concentration of fast-twitch fibers, so they can sprint in short bursts but have little stamina.",
                    },
                    {
                        "slot": 10,
                        "id": "hyena-contest",
                        "title": "Rivals",
                        "stem": "How do lions and spotted hyenas treat each other’s kills?",
                        "choices": [
                            "They never notice each other",
                            "They steal kills from each other (kleptoparasitism both ways)",
                            "Hyenas only eat plants",
                        ],
                        "correct": "B",
                        "why": "Lions and spotted hyenas compete for prey and carrion. Each species may steal the other’s kills — kleptoparasitism goes both ways.",
                    },
                ],
            },
        },
    },
    "reticulated-giraffe": {
        "id": "reticulated-giraffe",
        "source": WIKI_GIRAFFE,
        "source_note": "Facts from Wikipedia, Giraffe / Reticulated giraffe.",
        "talk_about": list(TALK_ABOUT_GIRAFFE),
        "push_further": list(PUSH_FURTHER_GIRAFFE),
        "levels": {
            "easy": {
                # Teaching-first: pride-of-place facts. Do not spoiler every quiz slot.
                "teach": [
                    "The giraffe is the tallest living land animal.",
                    "It eats leaves and shoots from tall trees.",
                    "A very long neck helps it reach high foliage.",
                    "A baby giraffe is a calf.",
                    "Wild giraffes live on African savannah and open woodland.",
                ],
                "questions": [
                    {
                        "slot": 1,
                        "id": "tallest",
                        "title": "Tallest",
                        "stem": "What record does a giraffe hold among living land animals?",
                        "choices": ["Fastest runner", "Tallest living land animal", "Smallest mammal"],
                        "correct": "B",
                        "why": "The giraffe is the tallest living land animal — taller than any other animal that lives on land today.",
                    },
                    {
                        "slot": 2,
                        "id": "food",
                        "title": "Food",
                        "stem": "What do giraffes mostly eat?",
                        "choices": ["Meat", "Leaves and shoots from tall trees", "Fish"],
                        "correct": "B",
                        "why": "Giraffes eat leaves and shoots from tall trees, especially acacia. They are not meat-eaters.",
                    },
                    {
                        "slot": 3,
                        "id": "neck",
                        "title": "Neck",
                        "stem": "Why does a giraffe have such a long neck?",
                        "choices": ["To store water like a camel", "To reach high leaves", "To fly"],
                        "correct": "B",
                        "why": "A giraffe’s extremely long neck helps it reach high foliage that shorter animals cannot.",
                    },
                    {
                        "slot": 4,
                        "id": "tongue",
                        "title": "Tongue",
                        "stem": "What is special about a giraffe’s tongue?",
                        "choices": [
                            "It is very long and dark, for stripping leaves",
                            "It is forked like a snake",
                            "It is short and used only to drink",
                        ],
                        "correct": "A",
                        "why": "A giraffe uses a very long, dark tongue to pull and strip leaves from thorny branches.",
                    },
                    {
                        "slot": 5,
                        "id": "young",
                        "title": "Young",
                        "stem": "What is a baby giraffe called, and what can it do soon after birth?",
                        "choices": [
                            "A cub — it stays lying down for weeks",
                            "A calf — it can stand soon after birth",
                            "A chick — it hatches from an egg",
                        ],
                        "correct": "B",
                        "why": "A baby giraffe is a calf. Newborns can stand soon after they are born.",
                    },
                    {
                        "slot": 6,
                        "id": "home",
                        "title": "Home",
                        "stem": "Where do wild giraffes mostly live?",
                        "choices": [
                            "African savannah and open woodland",
                            "Deep ocean",
                            "Thick polar ice",
                        ],
                        "correct": "A",
                        "why": "Wild giraffes live on African savannah and open woodland — not only one country.",
                    },
                    {
                        "slot": 7,
                        "id": "drink",
                        "title": "Drink",
                        "stem": "How does a giraffe drink water?",
                        "choices": [
                            "It uses a trunk",
                            "It spreads its front legs or bends its knees",
                            "It never drinks water",
                        ],
                        "correct": "B",
                        "why": "A giraffe’s neck and legs are so long that it spreads its front legs or bends its knees to reach the water.",
                    },
                    {
                        "slot": 8,
                        "id": "ossicones",
                        "title": "Ossicones",
                        "stem": "What are the horn-like bumps on a giraffe’s head?",
                        "choices": [
                            "Antlers that fall off each year",
                            "Skin-covered ossicones",
                            "Ears that folded up",
                        ],
                        "correct": "B",
                        "why": "Those bumps are ossicones — skin-covered, horn-like knobs. They are not antlers that shed.",
                    },
                    {
                        "slot": 9,
                        "id": "coat",
                        "title": "Coat",
                        "stem": "What is special about a giraffe’s coat?",
                        "choices": [
                            "Every giraffe has the same spots",
                            "Dark patches in a net-like pattern; each giraffe’s spots are unique",
                            "It is bright blue with stripes",
                        ],
                        "correct": "B",
                        "why": "A reticulated giraffe’s dark patches look like a net. Each giraffe’s spot pattern is unique.",
                    },
                    {
                        "slot": 10,
                        "id": "myth",
                        "title": "Myth buster",
                        "stem": "Does a giraffe have extra neck bones compared with most mammals?",
                        "choices": [
                            "Yes — dozens of extra bones",
                            "No — still seven vertebrae, just much longer",
                            "It has no neck bones",
                        ],
                        "correct": "B",
                        "why": "Like most mammals, a giraffe has seven neck vertebrae. Each bone is just much longer.",
                    },
                ],
            },
            "hard": {
                # Answer-light: no Learn-first strip. Facts from Wikipedia, Giraffe.
                "teach": [],
                "questions": [
                    {
                        "slot": 1,
                        "id": "relative",
                        "title": "Relatives",
                        "stem": "What is the giraffe’s closest living relative?",
                        "choices": [
                            "The camel",
                            "The okapi (both are Giraffidae)",
                            "The elephant",
                        ],
                        "correct": "B",
                        "why": "Giraffes and the okapi are the only living members of family Giraffidae. The okapi is the giraffe’s closest living relative.",
                    },
                    {
                        "slot": 2,
                        "id": "name",
                        "title": "Name",
                        "stem": "What does the old English name “camelopard” mean?",
                        "choices": [
                            "A desert camel only",
                            "Camel-like shape plus leopard-like spots",
                            "A spotted leopard from Asia",
                        ],
                        "correct": "B",
                        "why": "“Camelopard” comes from Greek words for camel and leopard — a camel-like shape with leopard-like colouration.",
                    },
                    {
                        "slot": 3,
                        "id": "ossicones-deeper",
                        "title": "Ossicones",
                        "stem": "What are a giraffe’s ossicones made of?",
                        "choices": [
                            "Antlers that shed each year",
                            "Ossified cartilage covered in skin and fused to the skull",
                            "Hollow horns that fall off",
                        ],
                        "correct": "B",
                        "why": "Ossicones form from ossified cartilage, stay covered in skin, and fuse to the skull. They are not antlers that shed.",
                    },
                    {
                        "slot": 4,
                        "id": "necking",
                        "title": "Necking",
                        "stem": "How do male giraffes usually fight to establish dominance?",
                        "choices": [
                            "They roar at each other",
                            "They swing their necks and land blows with ossicones",
                            "They lock antlers and push",
                        ],
                        "correct": "B",
                        "why": "Males “neck” — swinging their necks and trying to land blows with their ossicones to decide who is dominant.",
                    },
                    {
                        "slot": 5,
                        "id": "speed",
                        "title": "Speed",
                        "stem": "How fast can a giraffe gallop in a short burst?",
                        "choices": [
                            "It cannot run at all",
                            "Roughly 30–37 mph in short bursts",
                            "Faster than a cheetah for hours",
                        ],
                        "correct": "B",
                        "why": "Giraffes can gallop roughly 30–37 mph in short bursts. They are not built for long, all-day chases.",
                    },
                    {
                        "slot": 6,
                        "id": "ruminate",
                        "title": "Ruminate",
                        "stem": "How does a giraffe chew its food a second time?",
                        "choices": [
                            "It never chews again after the first swallow",
                            "It has a four-chambered stomach and brings cud back up the long neck",
                            "It stores food in its ossicones",
                        ],
                        "correct": "B",
                        "why": "Giraffes are ruminants with a four-chambered stomach. Strong oesophageal muscles send cud back up the long neck to be chewed again.",
                    },
                    {
                        "slot": 7,
                        "id": "sleep",
                        "title": "Sleep",
                        "stem": "How do giraffes usually sleep?",
                        "choices": [
                            "They sleep about 20 hours a day like lions",
                            "In short bouts that add up to only a few hours a day",
                            "They never sleep",
                        ],
                        "correct": "B",
                        "why": "Giraffes sleep in short, interrupted bouts that total only a few hours a day — not one long night of sleep.",
                    },
                    {
                        "slot": 8,
                        "id": "calf-size",
                        "title": "Calves",
                        "stem": "How tall is a newborn giraffe, and how soon can it run?",
                        "choices": [
                            "Mouse-sized; it cannot walk for months",
                            "Already about as tall as a person, and it can run within hours",
                            "Taller than an adult giraffe on day one",
                        ],
                        "correct": "B",
                        "why": "A newborn calf is already about as tall as a person. Within a few hours it can run, though it still hides a lot in the first weeks.",
                    },
                    {
                        "slot": 9,
                        "id": "threats",
                        "title": "Threats",
                        "stem": "What are the main threats to wild giraffes today?",
                        "choices": [
                            "Too much rain only",
                            "Habitat loss and hunting for bushmeat",
                            "Giraffes moving to the deep ocean",
                        ],
                        "correct": "B",
                        "why": "The biggest concerns are habitat loss and killing for bushmeat. Exact IUCN labels have shifted as giraffe species were split.",
                    },
                    {
                        "slot": 10,
                        "id": "tongue-why",
                        "title": "Tongue",
                        "stem": "Why might a giraffe’s tongue be dark?",
                        "choices": [
                            "To taste only meat",
                            "The dark colour may help protect it from sunburn while browsing",
                            "To scare other giraffes",
                        ],
                        "correct": "B",
                        "why": "A giraffe’s tongue is dark — Wikipedia notes it is black, perhaps to protect against sunburn while the animal browses in the sun.",
                    },
                ],
            },
            "zoologist": {
                # Answer-light: no Learn-first strip. Facts from Wikipedia, Giraffe.
                "teach": [],
                "questions": [
                    {
                        "slot": 1,
                        "id": "species-split",
                        "title": "Species",
                        "stem": "How do many scientists treat living giraffes today?",
                        "choices": [
                            "Always one species forever, with no debate",
                            "Often as several species (often four); the reticulated giraffe is Giraffa reticulata",
                            "Only as two extinct fossil species",
                        ],
                        "correct": "B",
                        "why": "Giraffes were long treated as one species. Many researchers now recognize several living species — often four — and the reticulated giraffe as Giraffa reticulata. Wikipedia treats that recognition as ongoing debate, not a forever rule.",
                    },
                    {
                        "slot": 2,
                        "id": "blood-pressure",
                        "title": "Heart",
                        "stem": "Why must a giraffe’s heart work so hard to supply the brain?",
                        "choices": [
                            "The heart is tiny and barely beats",
                            "It must generate roughly double typical human blood pressure to push blood up the long neck",
                            "Giraffes have no blood vessels in the neck",
                        ],
                        "correct": "B",
                        "why": "Wikipedia says the giraffe heart must generate about double the blood pressure a human needs to keep blood flowing to the brain. Exact pressure readings vary, so we keep the “roughly double” idea.",
                    },
                    {
                        "slot": 3,
                        "id": "rete-mirabile",
                        "title": "Circulation",
                        "stem": "What helps protect a giraffe’s brain when the head drops to drink?",
                        "choices": [
                            "Extra lungs in the ossicones",
                            "A rete mirabile in the neck plus valves in the jugular veins",
                            "The tongue plugs the windpipe",
                        ],
                        "correct": "B",
                        "why": "When the head lowers, a rete mirabile — a net of vessels in the upper neck — plus valves in the jugular veins keep too much blood from flooding the brain.",
                    },
                    {
                        "slot": 4,
                        "id": "cervical-length",
                        "title": "Neck bones",
                        "stem": "How is a giraffe’s neck built, compared with most other mammals?",
                        "choices": [
                            "It added many extra cervical vertebrae",
                            "It still has seven cervical vertebrae, each greatly lengthened",
                            "The neck is one solid bone with no joints",
                        ],
                        "correct": "B",
                        "why": "Like most mammals, a giraffe still has seven cervical vertebrae. Each bone is greatly lengthened — the neck did not gain a stack of extra bones.",
                    },
                    {
                        "slot": 5,
                        "id": "flehmen",
                        "title": "Scent",
                        "stem": "How do male giraffes check whether a female is ready to mate?",
                        "choices": [
                            "They listen for a roar",
                            "They taste her urine (flehmen), sending cues toward the vomeronasal organ",
                            "They count her spots",
                        ],
                        "correct": "B",
                        "why": "Males use the flehmen response: tasting a female’s urine to detect oestrus. The lip-curl routes chemical cues toward the vomeronasal organ.",
                    },
                    {
                        "slot": 6,
                        "id": "gestation",
                        "title": "Gestation",
                        "stem": "About how long is giraffe pregnancy, and how many calves are usual?",
                        "choices": [
                            "Roughly 400–460 days; usually one calf",
                            "About two weeks; often a dozen calves",
                            "About 30 days; twins every time",
                        ],
                        "correct": "A",
                        "why": "Wikipedia gives gestation as about 400–460 days. Usually one calf is born; twins are rare. We keep that range rather than one exact day count.",
                    },
                    {
                        "slot": 7,
                        "id": "neck-evolution",
                        "title": "Evolution",
                        "stem": "What two main ideas does Wikipedia discuss for why giraffe necks became so long?",
                        "choices": [
                            "Only swimming, with no other idea",
                            "Competing browsers reaching high food, and sexual selection via necking",
                            "Necks grew so giraffes could hibernate",
                        ],
                        "correct": "B",
                        "why": "Wikipedia discusses both the competing-browsers idea (reaching food others cannot) and sexual selection (long necks helping males in necking contests). Scientists still debate which mattered more.",
                    },
                    {
                        "slot": 8,
                        "id": "spot-physiology",
                        "title": "Spots",
                        "stem": "What may the skin under a giraffe’s dark patches do besides camouflage?",
                        "choices": [
                            "Store extra water like a camel hump",
                            "Hold complex blood vessels and large sweat glands that may help cool the body",
                            "Make electricity",
                        ],
                        "correct": "B",
                        "why": "Wikipedia notes the skin under the dark blotches has complex blood-vessel systems and large sweat glands, which may help the giraffe regulate body temperature.",
                    },
                    {
                        "slot": 9,
                        "id": "laryngeal-nerve",
                        "title": "Nerves",
                        "stem": "What is striking about a giraffe’s left recurrent laryngeal nerve?",
                        "choices": [
                            "It is the shortest nerve in any mammal",
                            "It takes an extreme detour down the neck and back up, making it extraordinarily long",
                            "It only exists in baby giraffes",
                        ],
                        "correct": "B",
                        "why": "In mammals the left recurrent laryngeal nerve loops around a vessel near the heart, then returns to the larynx. In a giraffe that detour is extraordinarily long — a classic comparative-anatomy example.",
                    },
                    {
                        "slot": 10,
                        "id": "fission-fusion",
                        "title": "Society",
                        "stem": "How do giraffe social groups actually work?",
                        "choices": [
                            "Purely random open herds with no lasting ties",
                            "Fission–fusion groups, with lasting female associations and kinship",
                            "Only solitary animals that never meet",
                        ],
                        "correct": "B",
                        "why": "Giraffe groups were once called open and ever-changing. Newer work describes a fission–fusion society: groups split and join, but females often keep lasting associations and kinship ties.",
                    },
                ],
            },
        },
    },
    "african-elephant": {
        "id": "african-elephant",
        "source": WIKI_AFRICAN_ELEPHANT,
        "source_note": "Facts from Wikipedia, African elephant / Elephant.",
        "talk_about": list(TALK_ABOUT_ELEPHANT),
        "push_further": list(PUSH_FURTHER_ELEPHANT),
        "levels": {
            "easy": {
                # Teaching-first: pride-of-place facts. Do not spoiler every quiz slot.
                "teach": [
                    "The African elephant is the largest living land animal.",
                    "It eats plants — grass, leaves, and bark — not meat.",
                    "Its trunk can grab, drink, spray, and smell.",
                    "A baby elephant is a calf.",
                    "A herd is led by the oldest female.",
                ],
                "questions": [
                    {
                        "slot": 1,
                        "id": "biggest",
                        "title": "Biggest",
                        "stem": "What record does an African elephant hold among living land animals?",
                        "choices": [
                            "Tallest living land animal",
                            "Largest / heaviest living land animal",
                            "Fastest runner",
                        ],
                        "correct": "B",
                        "why": "The African elephant is the largest and heaviest living land animal.",
                    },
                    {
                        "slot": 2,
                        "id": "food",
                        "title": "Food",
                        "stem": "What do African elephants eat?",
                        "choices": ["Meat", "Plants — grass, leaves, and bark", "Fish"],
                        "correct": "B",
                        "why": "African elephants are herbivores. They eat plants such as grass, leaves, and bark — not meat.",
                    },
                    {
                        "slot": 3,
                        "id": "trunk",
                        "title": "Trunk",
                        "stem": "What does an elephant use its trunk for?",
                        "choices": ["Only to hear", "To grab, drink, spray, and smell", "To fly"],
                        "correct": "B",
                        "why": "The trunk is a long nose and upper lip. Elephants use it to grab food, drink, spray water, and smell.",
                    },
                    {
                        "slot": 4,
                        "id": "ears",
                        "title": "Ears",
                        "stem": "Why does an African elephant have such big ears?",
                        "choices": ["To stay cool", "To fly", "To store food"],
                        "correct": "A",
                        "why": "Big ears help an African elephant shed heat and stay cool.",
                    },
                    {
                        "slot": 5,
                        "id": "young",
                        "title": "Young",
                        "stem": "What is a baby elephant called?",
                        "choices": ["A cub", "A calf", "A chick"],
                        "correct": "B",
                        "why": "A baby elephant is a calf.",
                    },
                    {
                        "slot": 6,
                        "id": "family",
                        "title": "Family",
                        "stem": "Who usually leads an elephant herd?",
                        "choices": [
                            "The oldest female (the matriarch)",
                            "The youngest calf",
                            "A lone zebra",
                        ],
                        "correct": "A",
                        "why": "Elephant families live in a herd led by the oldest female, called the matriarch.",
                    },
                    {
                        "slot": 7,
                        "id": "tusks",
                        "title": "Tusks",
                        "stem": "What are an elephant’s tusks?",
                        "choices": ["Horns made of hair", "Very long teeth", "Feathers"],
                        "correct": "B",
                        "why": "Tusks are very long teeth — not horns.",
                    },
                    {
                        "slot": 8,
                        "id": "voice",
                        "title": "Voice",
                        "stem": "What sound is an elephant famous for?",
                        "choices": ["A moo", "A trumpet", "A meow"],
                        "correct": "B",
                        "why": "An elephant’s famous call is a trumpet — a loud sound made through the trunk.",
                    },
                    {
                        "slot": 9,
                        "id": "water",
                        "title": "Water",
                        "stem": "How can an African elephant swim?",
                        "choices": [
                            "It cannot swim",
                            "It can swim, and its trunk can act like a snorkel",
                            "It uses wings",
                        ],
                        "correct": "B",
                        "why": "Elephants can swim. They sometimes swim underwater and use the trunk like a snorkel.",
                    },
                    {
                        "slot": 10,
                        "id": "myth",
                        "title": "Myth buster",
                        "stem": "Can an elephant jump?",
                        "choices": [
                            "Yes — they hop like kangaroos",
                            "No — elephants cannot jump",
                            "Only over tiny puddles",
                        ],
                        "correct": "B",
                        "why": "Elephants cannot jump. Their heavy bodies stay on the ground.",
                    },
                ],
            },
            "hard": {
                # Answer-light: no Learn-first strip. Facts from Wikipedia,
                # African elephant / Elephant. Soften exact trunk-muscle counts.
                "teach": [],
                "questions": [
                    {
                        "slot": 1,
                        "id": "trunk-muscle",
                        "title": "Trunk",
                        "stem": "How is an elephant’s trunk built, muscle-wise?",
                        "choices": [
                            "One long bone down the middle",
                            "Tens of thousands of muscles and no bone",
                            "A hollow tube of cartilage only",
                        ],
                        "correct": "B",
                        "why": "The trunk is a muscular hydrostat — tens of thousands of muscles and no bone. Published counts vary, so we do not lock one exact number.",
                    },
                    {
                        "slot": 2,
                        "id": "infrasound",
                        "title": "Voice",
                        "stem": "How do elephants often talk across long distances?",
                        "choices": [
                            "Only by slapping their ears",
                            "With low-frequency rumbles, many too low for humans to hear",
                            "By flashing bright colours",
                        ],
                        "correct": "B",
                        "why": "Elephants use infrasonic rumbles. Much of that communication is too low for humans, and it can travel far across the landscape.",
                    },
                    {
                        "slot": 3,
                        "id": "gestation",
                        "title": "Gestation",
                        "stem": "About how long is African elephant pregnancy?",
                        "choices": [
                            "About two weeks",
                            "About 22 months — the longest of any land mammal",
                            "About 22 years",
                        ],
                        "correct": "B",
                        "why": "Calves are usually born after about 22 months. That is the longest pregnancy of any land mammal.",
                    },
                    {
                        "slot": 4,
                        "id": "matriarch-memory",
                        "title": "Memory",
                        "stem": "Why can an older matriarch be especially important in a drought?",
                        "choices": [
                            "She is the fastest runner",
                            "Her memory of water and food can guide the family",
                            "She stores water in her tusks",
                        ],
                        "correct": "B",
                        "why": "The oldest female leads the herd. Her long memory of where water and food were in hard years can help the family survive drought.",
                    },
                    {
                        "slot": 5,
                        "id": "molars",
                        "title": "Teeth",
                        "stem": "How do elephants replace worn chewing teeth?",
                        "choices": [
                            "They never get new teeth",
                            "New molars move forward from the back, like a conveyor, several times in a lifetime",
                            "They grow a new set all at once each year",
                        ],
                        "correct": "B",
                        "why": "Worn front molars drop out as new ones move forward from the back. Elephants replace these chewing teeth several times in a lifetime.",
                    },
                    {
                        "slot": 6,
                        "id": "silent-steps",
                        "title": "Feet",
                        "stem": "Why can such a heavy animal walk so quietly?",
                        "choices": [
                            "It has feathers on its feet",
                            "Fatty cushion pads under the feet help nearly silent steps",
                            "It walks only on its toenails",
                        ],
                        "correct": "B",
                        "why": "Soft fatty cushion pads under the feet spread the weight and help an elephant walk with almost no sound.",
                    },
                    {
                        "slot": 7,
                        "id": "smell",
                        "title": "Smell",
                        "stem": "How strong is an elephant’s sense of smell?",
                        "choices": [
                            "Elephants cannot smell at all",
                            "Among the best senses of smell of any mammal",
                            "Only as strong as a goldfish",
                        ],
                        "correct": "B",
                        "why": "An elephant’s trunk is a powerful nose. Elephants rank among the mammals with the best sense of smell.",
                    },
                    {
                        "slot": 8,
                        "id": "threats",
                        "title": "Threats",
                        "stem": "What are the main threats to wild African elephants today?",
                        "choices": [
                            "Too many leaves",
                            "Ivory poaching and habitat loss",
                            "Elephants moving to the deep ocean",
                        ],
                        "correct": "B",
                        "why": "The biggest threats are poaching for ivory and the loss and breakup of habitat.",
                    },
                    {
                        "slot": 9,
                        "id": "vs-asian",
                        "title": "Compare",
                        "stem": "How can you usually tell an African elephant from an Asian elephant?",
                        "choices": [
                            "African elephants have smaller ears and a rounded back",
                            "African elephants have larger ears and a concave (dipped) back",
                            "African elephants have no trunks",
                        ],
                        "correct": "B",
                        "why": "African elephants typically have larger ears and a concave, dipped back. Asian elephants have smaller ears and a convex or level back.",
                    },
                    {
                        "slot": 10,
                        "id": "mice-myth",
                        "title": "Myth buster",
                        "stem": "Are elephants really afraid of mice?",
                        "choices": [
                            "Yes — they run from every mouse they see",
                            "No — that is a myth; they react to sudden movement, not mice specifically",
                            "Only pink mice",
                        ],
                        "correct": "B",
                        "why": "“Afraid of mice” is a cartoon myth. Elephants may startle at sudden movement near their feet, not at mice as a special fear.",
                    },
                ],
            },
            "zoologist": {
                # Answer-light: no Learn-first strip. Facts from Wikipedia,
                # African elephant / Elephant. Soften TP53 copy counts and
                # IUCN status letters. Bush vs forest / Loxodonta lives here.
                "teach": [],
                "questions": [
                    {
                        "slot": 1,
                        "id": "species-split",
                        "title": "Species",
                        "stem": "How do scientists treat living African elephants today?",
                        "choices": [
                            "Always one species forever, with no split",
                            "As two living species: bush/savanna Loxodonta africana and forest L. cyclotis",
                            "Only as extinct mammoths",
                        ],
                        "correct": "B",
                        "why": "Wikipedia treats living African elephants as two species — the bush or savanna elephant Loxodonta africana and the forest elephant L. cyclotis. IUCN assesses them separately. Status labels have shifted, so we do not lock one letter.",
                    },
                    {
                        "slot": 2,
                        "id": "trunk-anatomy",
                        "title": "Trunk",
                        "stem": "What is an elephant’s trunk, anatomically?",
                        "choices": [
                            "A hollow bone like a horn",
                            "A fusion of the nose and the upper lip",
                            "Only a stretched nose, with no lip involved",
                        ],
                        "correct": "B",
                        "why": "The trunk, or proboscis, is a prehensile elongation of the nose and upper lip. Those parts fuse in early development — it is not a nose alone.",
                    },
                    {
                        "slot": 3,
                        "id": "trunk-tip",
                        "title": "Trunk tip",
                        "stem": "How does an African elephant’s trunk tip differ from an Asian elephant’s?",
                        "choices": [
                            "African elephants have no finger-like tip",
                            "African elephants have two finger-like processes; Asian elephants have one",
                            "Both have exactly five fingers",
                        ],
                        "correct": "B",
                        "why": "African elephants have two finger-like processes at the tip of the trunk. Asian elephants have one and more often wrap the trunk around food.",
                    },
                    {
                        "slot": 4,
                        "id": "seismic",
                        "title": "Senses",
                        "stem": "How can elephants pick up distant seismic signals?",
                        "choices": [
                            "Only by watching the sky",
                            "They detect ground-borne vibrations through their feet and trunk",
                            "By tasting the air with their tusks",
                        ],
                        "correct": "B",
                        "why": "Wikipedia notes elephants communicate with seismic vibrations that travel through the ground. They detect those ground-borne waves through the feet and the trunk.",
                    },
                    {
                        "slot": 5,
                        "id": "musth",
                        "title": "Musth",
                        "stem": "What happens when an adult bull elephant is in musth?",
                        "choices": [
                            "He sheds his trunk",
                            "Testosterone rises; he becomes more aggressive and sexually active, with temporal-gland signs",
                            "He stops eating plants",
                        ],
                        "correct": "B",
                        "why": "Musth is a state in adult males: elevated testosterone, heightened aggression and sexual activity, plus temporal-gland secretions running down the face.",
                    },
                    {
                        "slot": 6,
                        "id": "allomothers",
                        "title": "Family",
                        "stem": "Who besides the mother often helps care for an elephant calf?",
                        "choices": [
                            "Only adult bulls",
                            "Other young females in the family — allomothers",
                            "Passing zebras",
                        ],
                        "correct": "B",
                        "why": "Calves are cared for by their mother and other young females in the group, a pattern called allomothering or alloparenting.",
                    },
                    {
                        "slot": 7,
                        "id": "last-molars",
                        "title": "Teeth",
                        "stem": "What can happen after an old elephant’s last molar set wears out?",
                        "choices": [
                            "New tusks become chewing teeth",
                            "The elephant may starve, because it can no longer grind plants well",
                            "It grows a bird-like beak",
                        ],
                        "correct": "B",
                        "why": "After the final molar set wears out, an old elephant may starve — a common late-life cause of death. The last replacement is the last.",
                    },
                    {
                        "slot": 8,
                        "id": "hindgut",
                        "title": "Digestion",
                        "stem": "How do African elephants digest tough plants?",
                        "choices": [
                            "With a four-chamber ruminant stomach like a giraffe",
                            "By hindgut fermentation",
                            "By storing food in the tusks",
                        ],
                        "correct": "B",
                        "why": "Fermentation of food takes place in the hindgut. Elephants are hindgut fermenters, not four-chamber ruminants like giraffes.",
                    },
                    {
                        "slot": 9,
                        "id": "tp53",
                        "title": "Genes",
                        "stem": "What gene story is linked to elephants’ size and cancer resistance?",
                        "choices": [
                            "They have no tumor-suppressor genes",
                            "They carry many copies of TP53, a gene linked to cancer resistance (Peto’s paradox)",
                            "They rely on extra hearts only",
                        ],
                        "correct": "B",
                        "why": "Elephants carry many copies of the TP53 tumor-suppressor gene, which researchers link to unusually low cancer rates for such large, long-lived animals — Peto’s paradox. Published copy counts vary, so we do not lock one number.",
                    },
                    {
                        "slot": 10,
                        "id": "megagardener",
                        "title": "Seeds",
                        "stem": "Why are African elephants sometimes called megagardeners?",
                        "choices": [
                            "They plant seeds with their tusks on purpose",
                            "They are long-distance seed dispersers; dung can carry many plant species",
                            "They only eat meat and never spread seeds",
                        ],
                        "correct": "B",
                        "why": "Elephants are long-distance seed dispersers. Seeds pass through the gut and germinate in dung, which can carry many plant species — a megagardener role in the landscape.",
                    },
                ],
            },
        },
    },
    "african-penguin": {
        "id": "african-penguin",
        "source": WIKI_AFRICAN_PENGUIN,
        "source_note": "Facts from Wikipedia, African penguin.",
        "talk_about": list(TALK_ABOUT_PENGUIN),
        "push_further": list(PUSH_FURTHER_PENGUIN),
        "levels": {
            "easy": {
                # Teaching-first: pride-of-place facts. Do not spoiler every quiz slot.
                "teach": [
                    "African penguins live in Africa, not Antarctica.",
                    "They cannot fly in the air — they swim with flippers.",
                    "They eat fish and other sea food.",
                    "They live together in a colony.",
                    "They lay eggs in burrows or under bushes on the shore.",
                ],
                "questions": [
                    {
                        "slot": 1,
                        "id": "home",
                        "title": "Home",
                        "stem": "Where do wild African penguins live?",
                        "choices": [
                            "Antarctica only",
                            "Southern African coasts",
                            "The North Pole",
                        ],
                        "correct": "B",
                        "why": "African penguins live along southern African coasts, such as South Africa and Namibia — not Antarctica.",
                    },
                    {
                        "slot": 2,
                        "id": "flight",
                        "title": "Flight",
                        "stem": "Can an African penguin fly in the air?",
                        "choices": [
                            "Yes — they fly like eagles",
                            "No — they are flightless and “fly” underwater with flippers",
                            "Only at night",
                        ],
                        "correct": "B",
                        "why": "Like all penguins, African penguins cannot fly in the air. Their wings are stiff flippers they use to swim.",
                    },
                    {
                        "slot": 3,
                        "id": "food",
                        "title": "Food",
                        "stem": "What do African penguins mostly eat?",
                        "choices": [
                            "Grass and leaves",
                            "Fish and other sea prey, such as squid",
                            "Bamboo",
                        ],
                        "correct": "B",
                        "why": "They hunt in the sea. Wikipedia says they feed primarily on fish and squid, plus other small sea animals.",
                    },
                    {
                        "slot": 4,
                        "id": "voice",
                        "title": "Voice",
                        "stem": "Why is the African penguin sometimes called a “jackass penguin”?",
                        "choices": [
                            "It looks like a donkey",
                            "It makes a loud, donkey-like bray",
                            "It lives on a farm",
                        ],
                        "correct": "B",
                        "why": "One nickname is “jackass penguin,” from the species’ loud, donkey-like call.",
                    },
                    {
                        "slot": 5,
                        "id": "colony",
                        "title": "Colony",
                        "stem": "What do you call a large group of African penguins living together?",
                        "choices": ["A pride", "A colony", "A herd"],
                        "correct": "B",
                        "why": "African penguins live and breed together in a large group called a colony.",
                    },
                    {
                        "slot": 6,
                        "id": "eggs",
                        "title": "Eggs",
                        "stem": "How do African penguins have babies?",
                        "choices": [
                            "They give birth to live pups",
                            "They lay eggs",
                            "They plant seeds",
                        ],
                        "correct": "B",
                        "why": "African penguins lay eggs. They do not give birth to live young.",
                    },
                    {
                        "slot": 7,
                        "id": "coat",
                        "title": "Coat",
                        "stem": "How does an African penguin’s black-and-white coat help it hide?",
                        "choices": [
                            "It makes the penguin glow in the dark",
                            "Countershading — a dark back and pale belly hide it from hunters above and below",
                            "It keeps the penguin dry only",
                        ],
                        "correct": "B",
                        "why": "The dark back blends with the water from above, and the pale belly is harder to see from below. That hiding trick is called countershading.",
                    },
                    {
                        "slot": 8,
                        "id": "flippers",
                        "title": "Flippers",
                        "stem": "What are an African penguin’s wings like?",
                        "choices": [
                            "Soft wings for flying in the air",
                            "Stiff, flat flippers for swimming",
                            "Long arms for climbing trees",
                        ],
                        "correct": "B",
                        "why": "The wings are stiffened and flattened into flippers, made for swimming — not for flying in the air.",
                    },
                    {
                        "slot": 9,
                        "id": "nest",
                        "title": "Nest",
                        "stem": "Where do African penguins usually nest?",
                        "choices": [
                            "On Antarctic ice",
                            "In burrows or under bushes on the shore",
                            "High in rainforest trees",
                        ],
                        "correct": "B",
                        "why": "They nest in burrows or under rocks and bushes on the shore — not on ice.",
                    },
                    {
                        "slot": 10,
                        "id": "myth",
                        "title": "Myth buster",
                        "stem": "Do all penguins live on cold ice?",
                        "choices": [
                            "Yes — every penguin lives on ice",
                            "No — African penguins live on warmer African coasts",
                            "Only in zoos",
                        ],
                        "correct": "B",
                        "why": "Not every penguin lives somewhere icy. African penguins live on warmer coasts in southern Africa.",
                    },
                ],
            },
            "hard": {
                # Answer-light: no Learn-first strip. Facts from Wikipedia,
                # African penguin. Soften IUCN letters and pair counts.
                "teach": [],
                "questions": [
                    {
                        "slot": 1,
                        "id": "heat-patch",
                        "title": "Heat patch",
                        "stem": "What does the bare pink skin above an African penguin’s eye help it do?",
                        "choices": [
                            "Hear better underwater",
                            "Lose heat — the patch flushes pinker when the bird is warmer",
                            "Store extra fish oil",
                        ],
                        "correct": "B",
                        "why": "Bare pink skin above the eye helps dump heat. More blood flows there when the bird is warmer, so the patch looks pinker.",
                    },
                    {
                        "slot": 2,
                        "id": "chest-spots",
                        "title": "Chest spots",
                        "stem": "What is special about an African penguin’s chest spots?",
                        "choices": [
                            "Every penguin has the same spots",
                            "Each bird’s spot pattern is unique, like a fingerprint",
                            "The spots wash off in salt water",
                        ],
                        "correct": "B",
                        "why": "The black spots on the chest form a pattern unique to each bird, like a human fingerprint. Keepers can use that to tell individuals apart.",
                    },
                    {
                        "slot": 3,
                        "id": "moult",
                        "title": "Moult",
                        "stem": "What happens in an African penguin’s catastrophic moult?",
                        "choices": [
                            "It sheds a few feathers a day and keeps swimming",
                            "It sheds all its feathers at once and must stay out of the water for weeks while new ones grow",
                            "It never replaces its feathers",
                        ],
                        "correct": "B",
                        "why": "Penguins moult all feathers at once. New feathers are not waterproof yet, so the bird stays on land and fasts for weeks while the coat grows back.",
                    },
                    {
                        "slot": 4,
                        "id": "salt-gland",
                        "title": "Salt gland",
                        "stem": "How does an African penguin get rid of extra salt from seawater and sea food?",
                        "choices": [
                            "It never eats or drinks anything salty",
                            "A salt gland near the eye helps dump the extra salt",
                            "It stores salt in its flippers",
                        ],
                        "correct": "B",
                        "why": "A salt gland near the eye lets the penguin get rid of extra salt from seawater and a marine diet, so the body can stay in balance.",
                    },
                    {
                        "slot": 5,
                        "id": "fish-shortage",
                        "title": "Threats",
                        "stem": "What is the biggest problem facing wild African penguins today?",
                        "choices": [
                            "Too many icebergs",
                            "Not enough prey fish, after commercial fishing and warming seas",
                            "Too many trees on the beach",
                        ],
                        "correct": "B",
                        "why": "The biggest squeeze today is not enough prey fish. Commercial fishing and warming seas have made sardines and anchovies harder to find near colonies.",
                    },
                    {
                        "slot": 6,
                        "id": "guano",
                        "title": "Guano",
                        "stem": "How did old guano harvesting hurt African penguin nests?",
                        "choices": [
                            "It painted the rocks bright white",
                            "It removed the dung layer they dug nest burrows into",
                            "It made the fish taste better",
                        ],
                        "correct": "B",
                        "why": "Penguins once dug nest burrows into a thick guano (dung) layer. People harvested that dung for fertilizer, so many colonies lost the layer they nested in.",
                    },
                    {
                        "slot": 7,
                        "id": "pairs",
                        "title": "Pairs",
                        "stem": "How do African penguin pairs often behave from year to year?",
                        "choices": [
                            "They pick a new partner every week",
                            "They are often long-term and return to the same nest site",
                            "They never come back to land",
                        ],
                        "correct": "B",
                        "why": "Pairs are often long-term. They tend to return to the same nest site each breeding season.",
                    },
                    {
                        "slot": 8,
                        "id": "range",
                        "title": "Range",
                        "stem": "Where do African penguins breed in the wild?",
                        "choices": [
                            "On Arctic ice with polar bears",
                            "On coasts and islands of southern Africa",
                            "Only in inland deserts",
                        ],
                        "correct": "B",
                        "why": "They breed on coasts and islands of southern Africa, such as Namibia and South Africa — the only penguin that breeds on the African continent.",
                    },
                    {
                        "slot": 9,
                        "id": "banded",
                        "title": "Banded look",
                        "stem": "Why are African penguins called banded penguins?",
                        "choices": [
                            "They wear metal ID bands only",
                            "They belong to the Spheniscus group, with distinctive dark band(s) across the chest",
                            "They have rainbow stripes on their flippers",
                        ],
                        "correct": "B",
                        "why": "African penguins are banded (Spheniscus) penguins. They have distinctive dark band(s) across the chest — a light family look shared with a few other penguins.",
                    },
                    {
                        "slot": 10,
                        "id": "polar-bear",
                        "title": "Myth buster",
                        "stem": "Do wild penguins and polar bears ever meet?",
                        "choices": [
                            "Yes — they share the same ice",
                            "No — they live at opposite ends of the planet",
                            "Only in winter",
                        ],
                        "correct": "B",
                        "why": "Polar bears live in the Arctic. Wild penguins live in the Southern Hemisphere. They never meet in the wild — opposite ends of the planet.",
                    },
                ],
            },
            "zoologist": {
                # Answer-light: no Learn-first strip. Facts from Wikipedia,
                # African penguin. Soften IUCN letters, exact % decline,
                # and max dive depth/time. Do not redo JR/PR themes.
                "teach": [],
                "questions": [
                    {
                        "slot": 1,
                        "id": "genus",
                        "title": "Genus",
                        "stem": "Which genus do African penguins belong to, and who are their closest banded-penguin relatives?",
                        "choices": [
                            "Aptenodytes, with emperor and king penguins",
                            "Spheniscus, with Humboldt, Magellanic, and Galápagos penguins",
                            "Pygoscelis, with Adélie, chinstrap, and gentoo penguins",
                        ],
                        "correct": "B",
                        "why": "African penguins sit in Spheniscus, the banded penguins. Wikipedia groups them with Humboldt, Magellanic, and Galápagos penguins — similar in shape, colour, and behaviour.",
                    },
                    {
                        "slot": 2,
                        "id": "old-world",
                        "title": "Old World",
                        "stem": "What makes the African penguin unique among living penguins?",
                        "choices": [
                            "It is the only penguin that lives in Antarctica",
                            "It is the only penguin species that breeds on the African continent — the only penguin found in the Old World",
                            "It is the only penguin that can fly",
                        ],
                        "correct": "B",
                        "why": "Wikipedia calls it the only penguin species that breeds in Africa, and the only penguin found in the Old World. Other living penguins breed in the New World or farther south.",
                    },
                    {
                        "slot": 3,
                        "id": "supraorbital",
                        "title": "Salt gland",
                        "stem": "How does an African penguin’s supraorbital salt gland keep the body in osmotic balance?",
                        "choices": [
                            "It stores seawater in the stomach until the salt evaporates",
                            "It sits above the eyes and excretes concentrated salt, so extra salt from seawater and prey can leave the body",
                            "It turns salt into fresh water inside the lungs",
                        ],
                        "correct": "B",
                        "why": "African penguins have supraorbital salt glands above the eyes. The glands excrete concentrated salt, which helps maintain osmotic balance while the bird forages at sea.",
                    },
                    {
                        "slot": 4,
                        "id": "countershading",
                        "title": "Camouflage",
                        "stem": "What named camouflage strategy is an African penguin’s dark back and pale belly?",
                        "choices": [
                            "Disruptive coloration — random blotches that hide the outline",
                            "Classic countershading — a dark dorsal surface and pale ventral surface that hide the bird from above and below",
                            "Aposematism — bright warning colours that scare predators",
                        ],
                        "correct": "B",
                        "why": "Wikipedia names the colouring as countershading, a classic camouflage strategy. The dark back blends with the water from above, and the pale belly is harder to see from below.",
                    },
                    {
                        "slot": 5,
                        "id": "vasodilation",
                        "title": "Blood flow",
                        "stem": "What actually makes the pink facial patch above an African penguin’s eye look pinker when the bird is warmer?",
                        "choices": [
                            "Sunburn that permanently dyes the skin",
                            "More blood flowing into the patch (vasodilation); less flow (vasoconstriction) when the bird is cooler",
                            "Extra salt crystals sitting on the feathers",
                        ],
                        "correct": "B",
                        "why": "Blood flow controls the colour. When the bird is warmer, more blood reaches the facial patch (vasodilation), so it looks pinker. Cooler birds send less blood there (vasoconstriction).",
                    },
                    {
                        "slot": 6,
                        "id": "decline-drivers",
                        "title": "Decline",
                        "stem": "What combination of pressures has driven the sharp drop in wild African penguins?",
                        "choices": [
                            "Too many icebergs crowding the beaches",
                            "Prey shortage, habitat loss, and climate / ocean change acting together",
                            "Extra trees shading every nest",
                        ],
                        "correct": "B",
                        "why": "Wikipedia ties the decline to several threats at once — not enough prey, lost nesting habitat, and climate / ocean change. We do not lock a single status letter or an exact percent drop.",
                    },
                    {
                        "slot": 7,
                        "id": "fishery",
                        "title": "Fisheries",
                        "stem": "How do commercial fisheries compete with African penguins near colonies?",
                        "choices": [
                            "They harvest ice that penguins need for nests",
                            "Purse-seine and other commercial boats take sardines and anchovies — the same prey the birds hunt",
                            "They collect penguin eggs for fertilizer",
                        ],
                        "correct": "B",
                        "why": "Commercial fishing of sardines and anchovies leaves less prey near colonies, so birds must travel farther or switch to poorer food. Purse-seine and other commercial fleets work the same waters the penguins use.",
                    },
                    {
                        "slot": 8,
                        "id": "no-take",
                        "title": "Closures",
                        "stem": "Why can no-take fishing closures around African penguin colonies help breeding birds?",
                        "choices": [
                            "They keep tourists from seeing the penguins",
                            "They keep more sardines and anchovies within the birds’ foraging range while chicks are being raised",
                            "They force penguins to nest on ice instead",
                        ],
                        "correct": "B",
                        "why": "Closures and no-fishing zones around colonies leave more prey within a breeding bird’s reach. Wikipedia notes that restricting fishing near sites such as Robben Island improved breeding success, and later no-fishing zones were set around key breeding areas.",
                    },
                    {
                        "slot": 9,
                        "id": "pursuit-dive",
                        "title": "Diving",
                        "stem": "How do African penguins usually catch their prey underwater?",
                        "choices": [
                            "They sit on the surface and wait for fish to jump",
                            "They forage by pursuit diving — chasing prey underwater on relatively shallow, short dives",
                            "They walk along the beach and pick leftover shells",
                        ],
                        "correct": "B",
                        "why": "Wikipedia calls the African penguin a pursuit diver. Typical dives are relatively shallow and short; we do not lock a single max depth or dive time.",
                    },
                    {
                        "slot": 10,
                        "id": "tubenoses",
                        "title": "Relatives",
                        "stem": "What are penguins’ closest living relatives as an order?",
                        "choices": [
                            "Ostriches and other flightless land birds",
                            "Tubenoses such as albatrosses and petrels — not ostriches or gulls",
                            "Gulls and other typical coastal seabirds",
                        ],
                        "correct": "B",
                        "why": "Penguins (order Sphenisciformes) sit closest to the tubenoses (albatrosses, petrels, and shearwaters). They are not closest to ostriches, and not closest to gulls.",
                    },
                ],
            },
        },
    },
    "caribbean-flamingo": {
        "id": "caribbean-flamingo",
        "source": WIKI_AMERICAN_FLAMINGO,
        "source_note": "Facts from Wikipedia, American flamingo / Caribbean flamingo.",
        "talk_about": list(TALK_ABOUT_FLAMINGO),
        "push_further": list(PUSH_FURTHER_FLAMINGO),
        "levels": {
            "easy": {
                # Teaching-first: pride-of-place facts. Do not spoiler every quiz slot.
                "teach": [
                    "Grown-up Caribbean flamingos are bright pink.",
                    "They often stand on one leg.",
                    "They find food in shallow water.",
                    "A group of flamingos is a flock.",
                    "Baby flamingos are grey and fluffy — not bright pink at first.",
                ],
                "questions": [
                    {
                        "slot": 1,
                        "id": "colour",
                        "title": "Colour",
                        "stem": "What colour are grown-up Caribbean flamingos?",
                        "choices": [
                            "Bright green",
                            "Bright pink / reddish-pink",
                            "All black",
                        ],
                        "correct": "B",
                        "why": "Adult American flamingos — also called Caribbean flamingos — have reddish-pink feathers. Wikipedia also calls them rosy flamingos because of that pink colour.",
                    },
                    {
                        "slot": 2,
                        "id": "one-leg",
                        "title": "One leg",
                        "stem": "How do Caribbean flamingos often stand?",
                        "choices": [
                            "On one leg",
                            "On their beaks",
                            "Upside down in trees",
                        ],
                        "correct": "A",
                        "why": "Flamingos often stand on one leg with the other tucked up. Wikipedia says this may help them keep warm or rest with less effort.",
                    },
                    {
                        "slot": 3,
                        "id": "food-place",
                        "title": "Food place",
                        "stem": "Where do Caribbean flamingos find their food?",
                        "choices": [
                            "High in rainforest trees",
                            "In shallow water",
                            "Only on dry desert sand",
                        ],
                        "correct": "B",
                        "why": "They wade in shallow water — lagoons, mudflats, and shallow lakes — and stir the bottom to find small food.",
                    },
                    {
                        "slot": 4,
                        "id": "flock",
                        "title": "Flock",
                        "stem": "What do you call a group of Caribbean flamingos?",
                        "choices": ["A pride", "A flock", "A school"],
                        "correct": "B",
                        "why": "Flamingos live and fly together in a flock. Wikipedia often talks about flocks of American flamingos.",
                    },
                    {
                        "slot": 5,
                        "id": "chicks",
                        "title": "Chicks",
                        "stem": "What do baby Caribbean flamingos look like at first?",
                        "choices": [
                            "Bright pink like the grown-ups",
                            "Grey and fluffy",
                            "Covered in shiny scales",
                        ],
                        "correct": "B",
                        "why": "Chicks hatch greyish and fluffy. They are not bright pink at first — that colour comes later from their food.",
                    },
                    {
                        "slot": 6,
                        "id": "neck",
                        "title": "Neck",
                        "stem": "What is special about a Caribbean flamingo’s neck?",
                        "choices": [
                            "It is short and stiff",
                            "It is long and bendy",
                            "It is made of wood",
                        ],
                        "correct": "B",
                        "why": "Flamingos have a long, bendy neck. It helps them reach down into shallow water to feed.",
                    },
                    {
                        "slot": 7,
                        "id": "nest",
                        "title": "Nest",
                        "stem": "What kind of nest does a Caribbean flamingo build?",
                        "choices": [
                            "A high stick nest in a tree",
                            "A little mound of mud",
                            "A hole in Antarctic ice",
                        ],
                        "correct": "B",
                        "why": "Wikipedia says the American flamingo lays its egg on a mud mound. Both parents help with the nest.",
                    },
                    {
                        "slot": 8,
                        "id": "beak",
                        "title": "Beak",
                        "stem": "What is a Caribbean flamingo’s beak like?",
                        "choices": [
                            "Straight like a needle",
                            "Bent in the middle (curved / angled)",
                            "Round like a spoon with no bend",
                        ],
                        "correct": "B",
                        "why": "The beak is hooked downward — bent in the middle. That curved shape helps the bird filter food from the water.",
                    },
                    {
                        "slot": 9,
                        "id": "pink-food",
                        "title": "Pink from food",
                        "stem": "Why are grown-up Caribbean flamingos pink?",
                        "choices": [
                            "They are painted pink",
                            "The pink colour comes from the food they eat",
                            "They are born that bright pink",
                        ],
                        "correct": "B",
                        "why": "The pink comes from colour in their food, such as tiny shrimp and algae. They are not painted, and chicks are not born that bright pink.",
                    },
                    {
                        "slot": 10,
                        "id": "myth",
                        "title": "Myth buster",
                        "stem": "Can Caribbean flamingos fly?",
                        "choices": [
                            "No — they are flightless like ostriches",
                            "Yes — they are strong fliers",
                            "Only if a zoo clips their wings first",
                        ],
                        "correct": "B",
                        "why": "Flamingos are capable flyers. They fly in flocks to find food. They are not flightless.",
                    },
                ],
            },
        },
    },
}


def level_display_name(level: str | None = None) -> str:
    """User-facing name for a study-card level key."""
    key = str(level or DEFAULT_LEVEL).strip().lower()
    return LEVEL_DISPLAY_NAMES.get(key) or LEVEL_DISPLAY_NAMES[DEFAULT_LEVEL]


def _esc(s: str) -> str:
    return (
        str(s or "")
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def study_card_ids() -> tuple[str, ...]:
    return tuple(STUDY_CARDS)


def shipped_levels_for(card_id: str) -> tuple[str, ...]:
    """Shipped picker keys for a card — only levels listed in SHIPPED_LEVELS."""
    raw = STUDY_CARDS.get(str(card_id or "").strip()) or {}
    have = raw.get("levels") or {}
    return tuple(key for key in SHIPPED_LEVELS if key in have)


def _prompt_lines(raw: dict, pack: dict, key: str) -> list[str]:
    """Per-level override when the key is set; otherwise card-level shared prompts."""
    if key in pack and pack.get(key) is not None:
        src = pack.get(key) or []
    else:
        src = raw.get(key) or []
    return [str(line).strip() for line in src if str(line).strip()]


def study_deck_for(card_id: str, level: str = DEFAULT_LEVEL) -> dict | None:
    """Return a flattened deck for one card + level, or None."""
    raw = STUDY_CARDS.get(str(card_id or "").strip())
    if not raw:
        return None
    pack = (raw.get("levels") or {}).get(level)
    if not pack:
        return None
    questions = list(pack.get("questions") or [])
    if len(questions) != STUDY_SLOTS:
        return None
    return {
        "id": raw["id"],
        "level": level,
        "level_label": level_display_name(level),
        "source": raw.get("source") or "",
        "source_note": raw.get("source_note") or "",
        "teach": list(pack.get("teach") or []),
        "talk_about": _prompt_lines(raw, pack, "talk_about"),
        "push_further": _prompt_lines(raw, pack, "push_further"),
        "questions": questions,
    }


def validate_deck(deck: dict) -> list[str]:
    """Return human-readable problems. Empty list means the deck is locked.

    Easy requires a Learn-first teach strip. Hard and Zoologist are
    answer-light (empty teach).
    """
    errors: list[str] = []
    if not deck:
        return ["missing deck"]
    level = str(deck.get("level") or DEFAULT_LEVEL)
    teach = deck.get("teach") or []
    if level not in ANSWER_LIGHT_LEVELS and not teach:
        errors.append("teach strip empty")
    if level in ANSWER_LIGHT_LEVELS and teach:
        errors.append(f"{level} deck must not include a teach strip")
    questions = deck.get("questions") or []
    if len(questions) != STUDY_SLOTS:
        errors.append(f"expected {STUDY_SLOTS} questions, got {len(questions)}")
    seen_slots: set[int] = set()
    seen_ids: set[str] = set()
    for i, q in enumerate(questions, start=1):
        slot = int(q.get("slot") or 0)
        if slot != i:
            errors.append(f"slot {i} has slot={slot}")
        if slot in seen_slots:
            errors.append(f"duplicate slot {slot}")
        seen_slots.add(slot)
        qid = str(q.get("id") or "")
        if not qid:
            errors.append(f"slot {i} missing id")
        if qid in seen_ids:
            errors.append(f"duplicate id {qid}")
        seen_ids.add(qid)
        choices = list(q.get("choices") or [])
        if len(choices) != 3:
            errors.append(f"slot {i} needs 3 choices")
        correct = str(q.get("correct") or "")
        if correct not in LETTERS:
            errors.append(f"slot {i} correct must be A/B/C")
        elif choices and LETTERS.index(correct) >= len(choices):
            errors.append(f"slot {i} correct letter out of range")
        if not str(q.get("stem") or "").strip():
            errors.append(f"slot {i} missing stem")
        if not str(q.get("why") or "").strip():
            errors.append(f"slot {i} missing why")
        if not str(q.get("title") or "").strip():
            errors.append(f"slot {i} missing title")
    return errors


def decks_as_jsonable() -> dict:
    return STUDY_CARDS


def write_study_artifacts() -> None:
    """JSON + window.FP_STUDY_CARDS for print-kit / study-card.js."""
    STUDY_JSON.parent.mkdir(parents=True, exist_ok=True)
    STUDY_DATA_JS.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(STUDY_CARDS, indent=2, ensure_ascii=False)
    STUDY_JSON.write_text(payload + "\n", encoding="utf-8")
    names_js = json.dumps(LEVEL_DISPLAY_NAMES, ensure_ascii=False, separators=(",", ":"))
    STUDY_DATA_JS.write_text(
        "/* Generated from scripts/study_cards.py — edit the Python source. */\n"
        "window.FP_STUDY_LEVEL_NAMES = "
        + names_js
        + ";\n"
        "window.FPStudyLevelName = function (level) {\n"
        "  var names = window.FP_STUDY_LEVEL_NAMES || {};\n"
        "  var key = String(level || \"easy\").toLowerCase();\n"
        "  return names[key] || names.easy || \"Junior Ranger\";\n"
        "};\n"
        "window.FP_STUDY_CARDS = "
        + json.dumps(STUDY_CARDS, ensure_ascii=False, separators=(",", ":"))
        + ";\n",
        encoding="utf-8",
    )


def study_deepen_html(deck: dict, *, print_mode: bool = False, hidden: bool = False) -> str:
    """Talk about it + Push further. Screen answers area or print page 2."""
    talk = list(deck.get("talk_about") or [])
    push = list(deck.get("push_further") or [])
    if not talk and not push:
        return ""
    cls = "ps-study-deepen" if print_mode else "study-deepen"
    kick = "ps-study-deepen-kicker" if print_mode else "study-deepen-kicker"
    col = "ps-study-deepen-col" if print_mode else "study-deepen-col"
    parts: list[str] = []
    for title, lines in (("Talk about it", talk), ("Push further", push)):
        if not lines:
            continue
        items = "".join(f"<li>{_esc(line)}</li>" for line in lines)
        parts.append(
            f'<div class="{col}">'
            f'<p class="{kick}">{title}</p>'
            f"<ol>{items}</ol>"
            f"</div>"
        )
    hide = " hidden" if hidden and not print_mode else ""
    return f'<aside class="{cls}"{hide} aria-label="Go further">{"".join(parts)}</aside>'


def _level_picker_html(card_id: str, current: str) -> str:
    """Junior Ranger / Park Ranger / Zoologist segment when 2+ levels ship."""
    levels = shipped_levels_for(card_id)
    if len(levels) < 2:
        label = _esc(level_display_name(current))
        return f'<p class="study-level-badge">{label}</p>'
    buttons: list[str] = []
    for key in levels:
        on = key == current
        pressed = "true" if on else "false"
        active = " is-active" if on else ""
        buttons.append(
            f'<button type="button" class="study-level-btn{active}" '
            f'data-study-pick="{_esc(key)}" aria-pressed="{pressed}">'
            f"{_esc(level_display_name(key))}</button>"
        )
    return (
        f'<div class="study-level-picker" role="group" aria-label="Study level">'
        f"{''.join(buttons)}</div>"
    )


def study_talk_html(deck: dict, *, heading: str = "Talk") -> str:
    """Screen: optional teach strip + 10 MCQs + reveal/why. Picker when 2+ levels."""
    level = deck.get("level") or DEFAULT_LEVEL
    card_id = deck.get("id") or ""
    picker = _level_picker_html(str(card_id), str(level))
    teach_items = "".join(f"<li>{_esc(line)}</li>" for line in deck.get("teach") or [])
    teach = (
        f'<details class="study-teach">'
        f'<summary class="study-teach-kicker">Learn first '
        f'<span class="study-teach-hint">— tap to open</span></summary>'
        f"<ul>{teach_items}</ul>"
        f"</details>"
        if teach_items
        else ""
    )
    deepen = study_deepen_html(deck, hidden=True)
    cards: list[str] = []
    for q in deck.get("questions") or []:
        choices = []
        for letter, label in zip(LETTERS, q.get("choices") or []):
            choices.append(
                f'<button type="button" class="choice study-choice" '
                f'data-letter="{letter}" data-choice="{_esc(label)}">'
                f'<span class="dot" aria-hidden="true"></span>'
                f'<span><span class="study-letter">{letter}</span> {_esc(label)}</span>'
                f"</button>"
            )
        why = _esc(q.get("why") or "")
        cards.append(
            f'<section class="mission card-talk-q study-q" data-slot="{int(q["slot"])}" '
            f'data-qid="{_esc(q.get("id") or "")}" data-correct="{_esc(q.get("correct") or "")}">'
            f'<div class="mission-head"><span class="badge">{int(q["slot"])}</span>'
            f'<p class="mission-title">{_esc(q.get("title") or "")}</p></div>'
            f'<h3 class="mission-q">{_esc(q.get("stem") or "")}</h3>'
            f'<div class="choices" data-multi="0" data-count="3">{"".join(choices)}</div>'
            f'<p class="study-why" hidden>{why}</p>'
            f"</section>"
        )
    source = _esc(deck.get("source_note") or "")
    source_html = f'<p class="study-source">{source}</p>' if source else ""
    n = STUDY_SLOTS
    return (
        f'<section class="card-talk-pack card-study-pack" aria-label="{_esc(heading)}" '
        f'data-study-id="{_esc(deck.get("id") or "")}" data-study-level="{_esc(level)}">'
        f'<div class="study-head">'
        f'<h2 class="card-talk-h">{_esc(heading)}</h2>'
        f"{picker}"
        f"</div>"
        f"{teach}"
        f'<div class="study-toolbar no-print">'
        f'<p class="study-score">Score <span data-study-correct>0</span>/{n}</p>'
        f'<button type="button" class="btn btn-secondary" data-study-reveal>Show answers</button>'
        f"</div>"
        f'<div class="mission-grid study-grid">{"".join(cards)}</div>'
        f"{deepen}"
        f"{source_html}"
        f"</section>"
    )


def _print_q_card(q: dict) -> str:
    choice_html = []
    for letter, label in zip(LETTERS, q.get("choices") or []):
        choice_html.append(
            f'<div class="ps-choice"><span class="ps-dot"></span>'
            f"<span>{letter} · {_esc(label)}</span></div>"
        )
    return (
        f'<section class="ps-card ps-study-q">'
        f'<div class="ps-card-head"><span class="ps-num">{int(q["slot"])}</span>'
        f'<p class="ps-title">{_esc(q.get("title") or "")}</p></div>'
        f'<h3 class="ps-q">{_esc(q.get("stem") or "")}</h3>'
        f'<div class="ps-choices ps-study-choices">{"".join(choice_html)}</div>'
        f"</section>"
    )


def study_print_html(
    deck: dict,
    *,
    name: str,
    emoji: str = "",
    photo: str = "",
    photo_pos: str = "",
) -> str:
    """A4 duplex-ready: front quiz + back answers. Each face is one 9.4in sheet."""
    questions = list(deck.get("questions") or [])
    teach_items = "".join(f"<li>{_esc(line)}</li>" for line in deck.get("teach") or [])
    teach = (
        f'<div class="ps-study-teach"><p class="ps-talk-label">Learn first</p>'
        f"<ul>{teach_items}</ul></div>"
        if teach_items
        else ""
    )
    pos_style = ""
    if photo_pos:
        pos_style = (
            f' style="--ps-photo-pos:{_esc(photo_pos)};object-position:{_esc(photo_pos)}"'
        )
    photo_block = (
        f'<div class="ps-study-photo"><img class="ps-photo-big" src="{_esc(photo)}" '
        f'alt="{_esc(name)}" decoding="async"{pos_style} /></div>'
        if photo
        else ""
    )
    top_qs = "".join(_print_q_card(q) for q in questions[:2])
    rest_qs = "".join(_print_q_card(q) for q in questions[2:])
    answers = []
    for q in questions:
        letter = str(q.get("correct") or "")
        idx = LETTERS.index(letter) if letter in LETTERS else 0
        label = (q.get("choices") or [""])[idx]
        answers.append(
            f"<li><strong>{int(q['slot'])} {_esc(q.get('title') or '')} — {letter} {_esc(label)}.</strong> "
            f"{_esc(q.get('why') or '')}</li>"
        )
    source = _esc(deck.get("source_note") or "Facts from Wikipedia, Lion.")
    banner_name = f"{emoji} {name}".strip()
    level_label = _esc(deck.get("level_label") or level_display_name(deck.get("level")))
    return (
        f'<div class="ps-study-front ps-page">'
        f'<div class="ps-banner"><h1>FIELD TRIP KIT</h1>'
        f"<p>{_esc(name)} · {level_label} · Circle one · Flip for answers</p></div>"
        f'<header class="ps-head"><h2>{_esc(banner_name)}</h2>'
        f'<p class="ps-line"><strong>Explorer:</strong> <span class="write-in-line">________________</span></p>'
        f"</header>"
        f"{teach}"
        f'<div class="ps-study-top">{photo_block}'
        f'<div class="ps-study-top-qs">{top_qs}</div></div>'
        f'<div class="ps-study-grid">{rest_qs}</div>'
        f'<p class="ps-footer">{source} · 1less.app · Duplex: this side questions, back answers</p>'
        f"</div>"
        f'<div class="ps-study-back ps-page">'
        f'<div class="ps-banner"><h1>FIELD TRIP KIT</h1>'
        f"<p>{_esc(name)} · {level_label} · Answers</p></div>"
        f'<ol class="ps-study-answers">{"".join(answers)}</ol>'
        f"{study_deepen_html(deck, print_mode=True)}"
        f'<p class="ps-footer">{source} · {_esc(deck.get("source") or WIKI_LION)}</p>'
        f"</div>"
    )
