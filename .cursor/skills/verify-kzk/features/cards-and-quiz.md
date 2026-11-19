# Animal cards and the kid quiz

## Sub-features
- Cards index `/field-pack/cards/` (the script expects at least 40 cards); card pages `/field-pack/cards/<id>/`; short aliases 301 (e.g. `/field-pack/cards/lion/`).
- Quick tips, "Take the quiz" (`#quiz`), "Print this card".
- Quiz: three levels (Junior Ranger, Park Ranger `?level=hard`, Zoologist), right pick shows why and counts, wrong pick says "Not quite, try another!" and does not count, progress "N of 10 done", "Show answers"/"Hide answers" (`[data-study-reveal]`), finish panel.

## How to get to it (user POV)
From /start/ "All cards" or a card tile, or a printed sheet's QR code (it opens /field-pack/cards/ with printable QR tracking tags).

## Driving it with verify.py
`--only j3,j4`. j3 opens the lion card from the index, checks tips, the quiz anchor, and Print. j4 answers Q1 right
("A pride"), Q2 wrong ("Grass") then right ("Meat"), checks progress 1 → 1 → 2, switches to Park Ranger (URL gets
`level=`, progress back to 0), then Show answers marks at least 5 keys and the button flips to "Hide answers".

## Gotchas
- Answers are pinned for the lion card only; they come from the card's own tips. Do not add answers for other cards from memory.
- Show answers does not score anything (statechart quiz model, all rules hold).
