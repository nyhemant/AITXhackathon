/* Animal of the day.
   42 published animal and sea-life cards. name + hook are the first
   FIELD_PACK_CATALOG blurb for that id. Photo is the existing 320px webp.
   Index is the local day-of-year (Jan 1 = 0) modulo 42, id order stable.
   The HTML tile is the no-JS fallback; this script only swaps it. */
(function () {
  var ANIMALS = [
  {id:"african-elephant", name:"African elephant", hook:"Biggest land animal — trunk to grab, spray, and say hello.", w:320, h:346},
  {id:"african-lion", name:"African lion", hook:"Look close — mane, whiskers, a tuft on the tail. Lions often rest in a pride.", w:320, h:213},
  {id:"african-penguin", name:"African penguin", hook:"Waddle on land, zoom in water.", w:320, h:480},
  {id:"american-alligator", name:"American alligator", hook:"Armored wetland predator — stay on boardwalks and far from the water edge.", w:320, h:427},
  {id:"american-bison", name:"American bison", hook:"Huge grassland icon — never approach; watch from a car or far pullout.", w:320, h:207},
  {id:"asian-small-clawed-otter", name:"Asian small-clawed otter", hook:"Playful swimmer — smallest otter.", w:320, h:240},
  {id:"caribbean-flamingo", name:"Caribbean flamingo", hook:"Bright pink wader — long legs for shallow water.", w:320, h:213},
  {id:"cheetah", name:"Cheetah", hook:"Fastest land animal — built to sprint.", w:320, h:480},
  {id:"chimpanzee", name:"Chimpanzee", hook:"Smart forest ape — climbs and tools.", w:320, h:213},
  {id:"clownfish", name:"Clownfish", hook:"Bright reef fish — friends with anemones.", w:320, h:216},
  {id:"crab", name:"Crab", hook:"Sideways walker with a hard shell and pinchers.", w:320, h:240},
  {id:"cuttlefish", name:"Cuttlefish", hook:"Color-changing cousin of the octopus — a living disguise.", w:320, h:453},
  {id:"eel", name:"Eel", hook:"Long snaky fish — loves rocky hidey-holes.", w:320, h:240},
  {id:"elk", name:"Elk", hook:"Big deer of meadows and mountains — quiet watch from a safe distance.", w:320, h:257},
  {id:"freshwater-fish", name:"River / lake fish", hook:"Fish that live in fresh water — rivers, lakes, ponds.", w:320, h:399},
  {id:"galapagos-tortoise", name:"Galápagos tortoise", hook:"Giant tortoise — slow and steady.", w:320, h:213},
  {id:"giant-panda", name:"Giant panda", hook:"Black-and-white bamboo lover — calm and famous.", w:320, h:480},
  {id:"jellyfish", name:"Jellyfish", hook:"Soft drifter — no bones, glows and pulses in the water.", w:320, h:213},
  {id:"kelp-forest", name:"Kelp forest", hook:"An underwater forest of giant seaweed — fish and otters hide here.", w:320, h:208},
  {id:"koala", name:"Koala", hook:"Sleepy tree-sitter — look up in the eucalyptus.", w:320, h:230},
  {id:"manta-ray", name:"Manta ray", hook:"Giant winged swimmer — bigger and gentler than a stingray.", w:320, h:212},
  {id:"nile-hippo", name:"Nile hippo", hook:"Huge river giant that loves the water.", w:320, h:213},
  {id:"octopus", name:"Octopus", hook:"Eight arms and a big brain — master of hide-and-seek.", w:320, h:241},
  {id:"orangutan", name:"Orangutan", hook:"Tree ape with long arms — watches from the canopy.", w:320, h:207},
  {id:"ostrich", name:"Ostrich", hook:"Biggest bird — can’t fly, runs fast.", w:320, h:213},
  {id:"polar-bear", name:"Polar bear", hook:"Arctic swimmer in a white coat — built for ice.", w:320, h:213},
  {id:"puffin", name:"Puffin", hook:"Seabird that flies, swims, and carries a beak full of fish.", w:320, h:320},
  {id:"red-panda", name:"Red panda", hook:"Rusty tree-climber with a ringed tail — not a giant panda!", w:320, h:213},
  {id:"reticulated-giraffe", name:"Reticulated giraffe", hook:"Tallest animal on long legs — look up!", w:320, h:406},
  {id:"ring-tailed-lemur", name:"Ring-tailed lemur", hook:"Stripy tail from Madagascar.", w:320, h:480},
  {id:"sea-otter", name:"Sea otter", hook:"Furriest swimmer — floats on its back and uses rocks as tools.", w:320, h:207},
  {id:"sea-turtle", name:"Sea turtle", hook:"Shelled ocean traveler — flippers for swimming.", w:320, h:213},
  {id:"seahorse", name:"Seahorse", hook:"Tiny upright swimmer that holds on with its tail.", w:320, h:427},
  {id:"shark", name:"Shark", hook:"Ocean hunter with a strong swishy body.", w:320, h:177},
  {id:"starfish", name:"Sea star", hook:"Star-shaped ocean friend — often in touch tanks.", w:320, h:249},
  {id:"stingray", name:"Stingray", hook:"Flat swimmer — often in touch pools (gentle hands!).", w:320, h:241},
  {id:"sumatran-tiger", name:"Sumatran tiger", hook:"Stripy forest big cat — strong and stealthy.", w:320, h:427},
  {id:"two-toed-sloth", name:"Two-toed sloth", hook:"Slow forest climber — hangs upside down.", w:320, h:240},
  {id:"warthog", name:"Warthog", hook:"Savanna pig with tusks.", w:320, h:213},
  {id:"western-lowland-gorilla", name:"Western lowland gorilla", hook:"Strong gentle ape in family groups.", w:320, h:480},
  {id:"whale-shark", name:"Whale shark", hook:"Biggest fish in the sea — a gentle giant with a wide, filtering mouth.", w:320, h:213},
  {id:"zebra", name:"Zebra", hook:"Striped grassland runner — every pattern is unique.", w:320, h:411},
  ];

  function indexFor(date) {
    var y = date.getFullYear();
    var start = new Date(y, 0, 1);
    var today = new Date(y, date.getMonth(), date.getDate());
    var doy = Math.round((today.getTime() - start.getTime()) / 86400000);
    var n = ANIMALS.length;
    return ((doy % n) + n) % n;
  }

  function fill(root, animal) {
    var link = root.querySelector(".aotd-link");
    var img = root.querySelector(".aotd-photo");
    var name = root.querySelector(".aotd-name");
    var hook = root.querySelector(".aotd-hook");
    if (!link || !img || !name || !hook || !animal) return;
    link.setAttribute("href", "/field-pack/cards/" + animal.id + "/#from=aotd");
    img.setAttribute("src", "/field-pack/photos/" + animal.id + "-320-v1.webp");
    img.setAttribute("width", String(animal.w));
    img.setAttribute("height", String(animal.h));
    name.textContent = animal.name;
    hook.textContent = animal.hook;
  }

  function boot() {
    var animal = ANIMALS[indexFor(new Date())];
    var nodes = document.querySelectorAll(".aotd");
    for (var i = 0; i < nodes.length; i++) fill(nodes[i], animal);
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot);
  else boot();
})();
