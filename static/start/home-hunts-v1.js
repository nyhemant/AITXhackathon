/* Printable-hunt hero on /start/. Filters places from venue JSON. */
(function () {
  "use strict";

  var places = [{"slug":"acadia","name":"Acadia National Park","city":"Bar Harbor"},{"slug":"adelaide-zoo","name":"Adelaide Zoo","city":"Adelaide"},{"slug":"air-and-space","name":"National Air and Space Museum","city":"Washington"},{"slug":"al-ain-zoo","name":"Al Ain Zoo","city":"Al Ain"},{"slug":"albuquerque-biopark","name":"ABQ BioPark Zoo","city":"Albuquerque"},{"slug":"american-samoa","name":"National Park of American Samoa","city":"Pago Pago"},{"slug":"amnh","name":"American Museum of Natural History","city":"New York"},{"slug":"antwerp-zoo","name":"Antwerp Zoo","city":"Antwerp"},{"slug":"aquarium-of-the-pacific","name":"Aquarium of the Pacific","city":"Long Beach"},{"slug":"arches","name":"Arches National Park","city":"Moab"},{"slug":"arizona-science-center","name":"Arizona Science Center","city":"Phoenix"},{"slug":"artis-zoo","name":"Artis Zoo","city":"Amsterdam"},{"slug":"athens-attica-zoo","name":"Attica Zoological Park","city":"Athens"},{"slug":"auckland-zoo","name":"Auckland Zoo","city":"Auckland"},{"slug":"audubon-aquarium","name":"Audubon Aquarium","city":"New Orleans"},{"slug":"audubon-zoo","name":"Audubon Zoo","city":"New Orleans"},{"slug":"austin-zoo","name":"Austin Zoo","city":"Austin"},{"slug":"badlands","name":"Badlands National Park","city":"Interior"},{"slug":"banff","name":"Banff National Park","city":"Banff"},{"slug":"bangalore-bannerghatta","name":"Bannerghatta Biological Park","city":"Bengaluru"},{"slug":"bangkok-safari-world","name":"Safari World Bangkok","city":"Bangkok"},{"slug":"barcelona-zoo","name":"Barcelona Zoo","city":"Barcelona"},{"slug":"beijing-zoo","name":"Beijing Zoo","city":"Beijing"},{"slug":"berlin-zoo","name":"Berlin Zoo","city":"Berlin"},{"slug":"big-bend","name":"Big Bend National Park","city":"Big Bend"},{"slug":"biscayne","name":"Biscayne National Park","city":"Homestead"},{"slug":"black-canyon-gunnison","name":"Black Canyon of the Gunnison National Park","city":"Montrose"},{"slug":"blue-mountains","name":"Blue Mountains National Park","city":"Katoomba"},{"slug":"bogota-zoo","name":"Jaime Duque Park Zoo","city":"Bogotá"},{"slug":"bronx-zoo","name":"Bronx Zoo","city":"New York"},{"slug":"bryce-canyon","name":"Bryce Canyon National Park","city":"Bryce Canyon City"},{"slug":"budapest-zoo","name":"Budapest Zoo","city":"Budapest"},{"slug":"cairo-zoo","name":"Giza Zoo","city":"Cairo"},{"slug":"cal-academy","name":"California Academy of Sciences","city":"San Francisco"},{"slug":"calgary-zoo","name":"Calgary Zoo","city":"Calgary"},{"slug":"california-science-center","name":"California Science Center","city":"Los Angeles"},{"slug":"canyonlands","name":"Canyonlands National Park","city":"Moab"},{"slug":"capitol-reef","name":"Capitol Reef National Park","city":"Torrey"},{"slug":"carlsbad-caverns","name":"Carlsbad Caverns National Park","city":"Carlsbad"},{"slug":"carnegie-natural-history","name":"Carnegie Museum of Natural History","city":"Pittsburgh"},{"slug":"channel-islands","name":"Channel Islands National Park","city":"Ventura"},{"slug":"chapultepec-zoo","name":"Chapultepec Zoo","city":"Mexico City"},{"slug":"childrens-aquarium-dallas","name":"Children's Aquarium Dallas","city":"Dallas"},{"slug":"childrens-museum-perot","name":"Children's Museum (Perot)","city":"Dallas"},{"slug":"cincinnati-zoo","name":"Cincinnati Zoo & Botanical Garden","city":"Cincinnati"},{"slug":"cleveland-metroparks-zoo","name":"Cleveland Metroparks Zoo","city":"Cleveland"},{"slug":"columbus-zoo","name":"Columbus Zoo and Aquarium","city":"Powell"},{"slug":"congaree","name":"Congaree National Park","city":"Hopkins"},{"slug":"copenhagen-zoo","name":"Copenhagen Zoo","city":"Copenhagen"},{"slug":"crater-lake","name":"Crater Lake National Park","city":"Crater Lake"},{"slug":"cuyahoga-valley","name":"Cuyahoga Valley National Park","city":"Peninsula"},{"slug":"dallas-arboretum","name":"Dallas Arboretum (kids trails)","city":"Dallas"},{"slug":"dallas-world-aquarium","name":"Dallas World Aquarium","city":"Dallas"},{"slug":"dallas-zoo","name":"Dallas Zoo","city":"Dallas"},{"slug":"death-valley","name":"Death Valley National Park","city":"Furnace Creek"},{"slug":"delhi-zoo","name":"National Zoological Park","city":"Delhi"},{"slug":"denali","name":"Denali National Park","city":"Denali Park"},{"slug":"denver-museum-nature-science","name":"Denver Museum of Nature & Science","city":"Denver"},{"slug":"denver-zoo","name":"Denver Zoo","city":"Denver"},{"slug":"detroit-zoo","name":"Detroit Zoo","city":"Royal Oak"},{"slug":"discovery-place","name":"Discovery Place Science","city":"Charlotte"},{"slug":"doseum","name":"The DoSeum","city":"San Antonio"},{"slug":"dry-tortugas","name":"Dry Tortugas National Park","city":"Key West"},{"slug":"dubai-aquarium","name":"Dubai Aquarium & Underwater Zoo","city":"Dubai"},{"slug":"dublin-zoo","name":"Dublin Zoo","city":"Dublin"},{"slug":"ecoparque-ba","name":"Ecoparque Buenos Aires","city":"Buenos Aires"},{"slug":"edinburgh-zoo","name":"Edinburgh Zoo","city":"Edinburgh"},{"slug":"everglades","name":"Everglades National Park","city":"Homestead"},{"slug":"field-museum","name":"Field Museum","city":"Chicago"},{"slug":"fiordland","name":"Fiordland National Park","city":"Te Anau"},{"slug":"florida-aquarium","name":"The Florida Aquarium","city":"Tampa"},{"slug":"fort-worth-zoo","name":"Fort Worth Zoo","city":"Fort Worth"},{"slug":"french-island","name":"French Island National Park","city":"Tankerton"},{"slug":"frost-science","name":"Phillip and Patricia Frost Museum of Science","city":"Miami"},{"slug":"fuji-hakone-izu","name":"Fuji-Hakone-Izu National Park","city":"Fujikawaguchiko"},{"slug":"galapagos","name":"Galápagos National Park","city":"Puerto Ayora"},{"slug":"gates-of-arctic","name":"Gates of the Arctic National Park","city":"Bettles"},{"slug":"gateway-arch","name":"Gateway Arch National Park","city":"St. Louis"},{"slug":"georgia-aquarium","name":"Georgia Aquarium","city":"Atlanta"},{"slug":"giant-panda-national-park","name":"Giant Panda National Park","city":"Wolong"},{"slug":"glacier-bay","name":"Glacier Bay National Park","city":"Gustavus"},{"slug":"glacier","name":"Glacier National Park","city":"West Glacier"},{"slug":"grand-canyon","name":"Grand Canyon National Park","city":"Grand Canyon Village"},{"slug":"grand-teton","name":"Grand Teton National Park","city":"Moose"},{"slug":"great-basin","name":"Great Basin National Park","city":"Baker"},{"slug":"great-sand-dunes","name":"Great Sand Dunes National Park","city":"Mosca"},{"slug":"great-smoky-mountains","name":"Great Smoky Mountains National Park","city":"Gatlinburg"},{"slug":"guadalupe-mountains","name":"Guadalupe Mountains National Park","city":"Salt Flat"},{"slug":"haleakala","name":"Haleakalā National Park","city":"Kula"},{"slug":"hawaii-volcanoes","name":"Hawaiʻi Volcanoes National Park","city":"Hilo"},{"slug":"helsinki-zoo","name":"Korkeasaari Zoo","city":"Helsinki"},{"slug":"hogle-zoo","name":"Utah's Hogle Zoo","city":"Salt Lake City"},{"slug":"hong-kong-ocean-park","name":"Ocean Park Hong Kong","city":"Hong Kong"},{"slug":"honolulu-zoo","name":"Honolulu Zoo","city":"Honolulu"},{"slug":"hot-springs","name":"Hot Springs National Park","city":"Hot Springs"},{"slug":"houston-zoo","name":"Houston Zoo","city":"Houston"},{"slug":"iguazu-argentina","name":"Iguazú National Park (Argentina)","city":"Puerto Iguazú"},{"slug":"indiana-dunes","name":"Indiana Dunes National Park","city":"Porter"},{"slug":"indy-childrens-museum","name":"Children's Museum of Indianapolis","city":"Indianapolis"},{"slug":"isle-royale","name":"Isle Royale National Park","city":"Houghton"},{"slug":"istanbul-aquarium","name":"Istanbul Aquarium","city":"Istanbul"},{"slug":"jakarta-ragunan","name":"Ragunan Zoo","city":"Jakarta"},{"slug":"jasper","name":"Jasper National Park","city":"Jasper"},{"slug":"johannesburg-zoo","name":"Johannesburg Zoo","city":"Johannesburg"},{"slug":"joshua-tree","name":"Joshua Tree National Park","city":"Twentynine Palms"},{"slug":"kansas-city-zoo","name":"Kansas City Zoo","city":"Kansas City"},{"slug":"katmai","name":"Katmai National Park","city":"King Salmon"},{"slug":"kenai-fjords","name":"Kenai Fjords National Park","city":"Seward"},{"slug":"kennedy-space-center","name":"Kennedy Space Center","city":"Merritt Island"},{"slug":"killarney","name":"Killarney National Park","city":"Killarney"},{"slug":"kings-canyon","name":"Kings Canyon National Park","city":"Three Rivers"},{"slug":"kobuk-valley","name":"Kobuk Valley National Park","city":"Kotzebue"},{"slug":"kruger","name":"Kruger National Park","city":"Skukuza"},{"slug":"kuala-lumpur-zoo","name":"Zoo Negara","city":"Kuala Lumpur"},{"slug":"la-zoo","name":"Los Angeles Zoo","city":"Los Angeles"},{"slug":"lake-clark","name":"Lake Clark National Park","city":"Port Alsworth"},{"slug":"lake-district","name":"Lake District National Park","city":"Keswick"},{"slug":"lassen-volcanic","name":"Lassen Volcanic National Park","city":"Mineral"},{"slug":"lima-leyendas","name":"Parque de las Leyendas","city":"Lima"},{"slug":"lincoln-park-zoo","name":"Lincoln Park Zoo","city":"Chicago"},{"slug":"lisbon-zoo","name":"Lisbon Zoo","city":"Lisbon"},{"slug":"london-zoo","name":"London Zoo","city":"London"},{"slug":"lotte-aquarium-seoul","name":"Lotte World Aquarium","city":"Seoul"},{"slug":"madrid-zoo","name":"Madrid Zoo Aquarium","city":"Madrid"},{"slug":"mammoth-cave","name":"Mammoth Cave National Park","city":"Mammoth Cave"},{"slug":"manila-zoo","name":"Manila Zoo","city":"Manila"},{"slug":"melbourne-zoo","name":"Melbourne Zoo","city":"Melbourne"},{"slug":"memphis-zoo","name":"Memphis Zoo","city":"Memphis"},{"slug":"mesa-verde","name":"Mesa Verde National Park","city":"Mesa Verde"},{"slug":"miami-zoo","name":"Zoo Miami","city":"Miami"},{"slug":"milan-aquarium","name":"Acquario di Milano","city":"Milan"},{"slug":"milwaukee-zoo","name":"Milwaukee County Zoo","city":"Milwaukee"},{"slug":"minnesota-zoo","name":"Minnesota Zoo","city":"Apple Valley"},{"slug":"monterey-bay-aquarium","name":"Monterey Bay Aquarium","city":"Monterey"},{"slug":"montreal-biodome","name":"Montreal Biodome","city":"Montreal"},{"slug":"moscow-zoo","name":"Moscow Zoo","city":"Moscow"},{"slug":"mount-rainier","name":"Mount Rainier National Park","city":"Ashford"},{"slug":"mumbai-byculla-zoo","name":"Byculla Zoo (Jijamata Udyan)","city":"Mumbai"},{"slug":"munich-zoo","name":"Hellabrunn Zoo","city":"Munich"},{"slug":"museum-of-science-boston","name":"Museum of Science","city":"Boston"},{"slug":"museum-of-science-industry-chi","name":"Museum of Science and Industry","city":"Chicago"},{"slug":"nairobi-safari-walk","name":"Nairobi Safari Walk","city":"Nairobi"},{"slug":"nashville-adventure-science","name":"Adventure Science Center","city":"Nashville"},{"slug":"nashville-zoo","name":"Nashville Zoo","city":"Nashville"},{"slug":"national-aquarium-baltimore","name":"National Aquarium","city":"Baltimore"},{"slug":"national-zoo","name":"Smithsonian National Zoo","city":"Washington"},{"slug":"new-england-aquarium","name":"New England Aquarium","city":"Boston"},{"slug":"new-river-gorge","name":"New River Gorge National Park","city":"Glen Jean"},{"slug":"nhm-london","name":"Natural History Museum","city":"London"},{"slug":"nikko","name":"Nikkō National Park","city":"Nikko"},{"slug":"north-carolina-zoo","name":"North Carolina Zoo","city":"Asheboro"},{"slug":"north-cascades","name":"North Cascades National Park","city":"Marblemount"},{"slug":"olympic","name":"Olympic National Park","city":"Port Angeles"},{"slug":"omaha-henry-doorly","name":"Omaha's Henry Doorly Zoo & Aquarium","city":"Omaha"},{"slug":"oregon-museum-science-industry","name":"OMSI","city":"Portland"},{"slug":"oregon-zoo","name":"Oregon Zoo","city":"Portland"},{"slug":"orlando-science-center","name":"Orlando Science Center","city":"Orlando"},{"slug":"osaka-aquarium","name":"Osaka Aquarium Kaiyukan","city":"Osaka"},{"slug":"oslo-zoo","name":"Kristiansand Zoo","city":"Kristiansand"},{"slug":"paris-zoo","name":"Parc Zoologique de Paris","city":"Paris"},{"slug":"perot-museum","name":"Perot Museum of Nature and Science","city":"Dallas"},{"slug":"perth-zoo","name":"Perth Zoo","city":"Perth"},{"slug":"petrified-forest","name":"Petrified Forest National Park","city":"Holbrook"},{"slug":"philadelphia-zoo","name":"Philadelphia Zoo","city":"Philadelphia"},{"slug":"phoenix-zoo","name":"Phoenix Zoo","city":"Phoenix"},{"slug":"pinnacles","name":"Pinnacles National Park","city":"Paicines"},{"slug":"pittsburgh-zoo","name":"Pittsburgh Zoo & Aquarium","city":"Pittsburgh"},{"slug":"please-touch-museum","name":"Please Touch Museum","city":"Philadelphia"},{"slug":"plitvice-lakes","name":"Plitvice Lakes National Park","city":"Plitvička Jezera"},{"slug":"point-defiance-zoo","name":"Point Defiance Zoo & Aquarium","city":"Tacoma"},{"slug":"prague-zoo","name":"Prague Zoo","city":"Prague"},{"slug":"redwood","name":"Redwood National and State Parks","city":"Crescent City"},{"slug":"rio-zoo","name":"BioParque do Rio","city":"Rio de Janeiro"},{"slug":"rocky-mountain","name":"Rocky Mountain National Park","city":"Estes Park"},{"slug":"rome-bioparco","name":"Bioparco di Roma","city":"Rome"},{"slug":"saguaro","name":"Saguaro National Park","city":"Tucson"},{"slug":"san-antonio-zoo","name":"San Antonio Zoo","city":"San Antonio"},{"slug":"san-diego-safari-park","name":"San Diego Zoo Safari Park","city":"Escondido"},{"slug":"san-diego-zoo","name":"San Diego Zoo","city":"San Diego"},{"slug":"santiago-zoo","name":"Parque Metropolitano Zoo","city":"Santiago"},{"slug":"sao-paulo-zoo","name":"São Paulo Zoo","city":"São Paulo"},{"slug":"seattle-aquarium","name":"Seattle Aquarium","city":"Seattle"},{"slug":"seoul-zoo","name":"Seoul Grand Park Zoo","city":"Seoul"},{"slug":"sequoia","name":"Sequoia National Park","city":"Three Rivers"},{"slug":"shanghai-ocean-aquarium","name":"Shanghai Ocean Aquarium","city":"Shanghai"},{"slug":"shedd-aquarium","name":"Shedd Aquarium","city":"Chicago"},{"slug":"shenandoah","name":"Shenandoah National Park","city":"Luray"},{"slug":"singapore-night-safari","name":"Night Safari","city":"Singapore"},{"slug":"singapore-zoo","name":"Singapore Zoo","city":"Singapore"},{"slug":"smithsonian-natural-history","name":"National Museum of Natural History","city":"Washington"},{"slug":"snowdonia","name":"Eryri (Snowdonia) National Park","city":"Llanberis"},{"slug":"st-louis-zoo","name":"Saint Louis Zoo","city":"St. Louis"},{"slug":"stockholm-skansen","name":"Skansen","city":"Stockholm"},{"slug":"table-mountain","name":"Table Mountain National Park","city":"Cape Town"},{"slug":"taipei-zoo","name":"Taipei Zoo","city":"Taipei"},{"slug":"tampa-zoo","name":"ZooTampa at Lowry Park","city":"Tampa"},{"slug":"taronga-zoo","name":"Taronga Zoo","city":"Sydney"},{"slug":"theodore-roosevelt","name":"Theodore Roosevelt National Park","city":"Medora"},{"slug":"thinkery","name":"Thinkery","city":"Austin"},{"slug":"toronto-zoo","name":"Toronto Zoo","city":"Toronto"},{"slug":"torres-del-paine","name":"Torres del Paine National Park","city":"Puerto Natales"},{"slug":"two-oceans-aquarium","name":"Two Oceans Aquarium","city":"Cape Town"},{"slug":"ueno-zoo","name":"Ueno Zoo","city":"Tokyo"},{"slug":"union-station-kc-science","name":"Science City at Union Station","city":"Kansas City"},{"slug":"vancouver-aquarium","name":"Vancouver Aquarium","city":"Vancouver"},{"slug":"vienna-zoo","name":"Schönbrunn Zoo","city":"Vienna"},{"slug":"virgin-islands","name":"Virgin Islands National Park","city":"Cruz Bay"},{"slug":"virginia-aquarium","name":"Virginia Aquarium","city":"Virginia Beach"},{"slug":"voyageurs","name":"Voyageurs National Park","city":"International Falls"},{"slug":"waikiki-aquarium","name":"Waikiki Aquarium","city":"Honolulu"},{"slug":"warsaw-zoo","name":"Warsaw Zoo","city":"Warsaw"},{"slug":"wellington-zoo","name":"Wellington Zoo","city":"Wellington"},{"slug":"white-sands","name":"White Sands National Park","city":"Alamogordo"},{"slug":"wind-cave","name":"Wind Cave National Park","city":"Hot Springs"},{"slug":"woodland-park-zoo","name":"Woodland Park Zoo","city":"Seattle"},{"slug":"wrangell-st-elias","name":"Wrangell–St. Elias National Park","city":"Copper Center"},{"slug":"yellowstone","name":"Yellowstone National Park","city":"Yellowstone"},{"slug":"yoho","name":"Yoho National Park","city":"Field"},{"slug":"yosemite","name":"Yosemite National Park","city":"Yosemite Valley"},{"slug":"zion","name":"Zion National Park","city":"Springdale"},{"slug":"zurich-zoo","name":"Zurich Zoo","city":"Zurich"}];
  var cards = Array.prototype.slice.call(document.querySelectorAll(".home-hunts-card"));
  var input = document.getElementById("home-hunts-q");
  var extra = document.getElementById("home-hunts-extra");
  var form = document.getElementById("home-hunts-search");
  var featured = {};

  cards.forEach(function (card) {
    featured[card.getAttribute("data-home-hunt-slug") || ""] = true;
  });

  function trackSlug(slug) {
    if (typeof window.FPTrack === "function") {
      window.FPTrack("home_hunt_card_click", { slug: slug || "" });
    }
  }

  cards.forEach(function (card) {
    card.addEventListener("click", function () {
      trackSlug(card.getAttribute("data-home-hunt-slug"));
    });
  });

  function esc(s) {
    return String(s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function norm(s) {
    return String(s || "").toLowerCase();
  }

  function render(raw) {
    var query = norm(raw).trim();
    cards.forEach(function (card) {
      if (!query) {
        card.hidden = false;
        return;
      }
      var blob = [
        card.getAttribute("data-home-hunt-name"),
        card.getAttribute("data-home-hunt-city"),
        card.getAttribute("data-home-hunt-slug")
      ].join(" ");
      card.hidden = norm(blob).indexOf(query) === -1;
    });
    if (!extra) return;
    if (query.length < 2) {
      extra.hidden = true;
      extra.innerHTML = "";
      return;
    }
    var hits = [];
    for (var i = 0; i < places.length && hits.length < 8; i++) {
      var place = places[i];
      if (featured[place.slug]) continue;
      var blob = place.name + " " + place.city + " " + place.slug;
      if (norm(blob).indexOf(query) !== -1) hits.push(place);
    }
    if (!hits.length) {
      var anyCard = cards.some(function (card) { return !card.hidden; });
      extra.hidden = anyCard;
      extra.innerHTML = anyCard ? "" : '<li class="home-hunts-empty">No places match</li>';
      return;
    }
    extra.innerHTML = hits.map(function (place) {
      return '<li><a href="/field-pack/' + encodeURIComponent(place.slug) +
        '/#printable-hunt" data-home-hunt-slug="' + esc(place.slug) + '">' +
        '<span class="home-hunts-card-name">' + esc(place.name) + '</span>' +
        '<span class="home-hunts-card-city">' + esc(place.city) + '</span></a></li>';
    }).join("");
    extra.hidden = false;
    extra.querySelectorAll("a[data-home-hunt-slug]").forEach(function (link) {
      link.addEventListener("click", function () {
        trackSlug(link.getAttribute("data-home-hunt-slug"));
      });
    });
  }

  if (form) {
    form.addEventListener("submit", function (event) {
      event.preventDefault();
      render(input ? input.value : "");
    });
  }
  if (input) {
    input.addEventListener("input", function () {
      render(input.value);
    });
  }
})();
