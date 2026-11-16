"""School/group field-trip printables block for place pages with field-trip search demand.

2026-11-16: Hogle Zoo only ("hogle zoo field trips" query, ChiefGrok SEO audit item 1).
Facts come from the zoo's own Field Trips page (checked 2026-11-16):
https://www.hoglezoo.org/field-trips/ . Never add a venue here without a source.
The 24 scavenger test/comparison pages must not get this block before ~2026-12-10.
"""
from __future__ import annotations

PDFS = (
    ("teacher-handout", "Teacher handout", "Before, during, and after prompts."),
    ("chaperone-card", "Chaperone card", "Half-page rules and questions for each small group."),
    ("carpool", "Carpool Adventure Sheet", "Road spotting and an A–Z animal game for the drive."),
)

FIELD_TRIP_BLOCKS = {
    "hogle-zoo": {
        "heading": "Hogle Zoo field trip printables",
        "lead": (
            "Planning a school field trip to Utah’s Hogle Zoo? Book it on the zoo’s official "
            "Field Trips page. School reservations open in August for the coming school year and "
            "are for Utah K–12 public, private, and charter schools. The zoo asks for one adult, "
            "21 or older, for every five students, and name tags with the school and teacher name. "
            "Then print these for the day:"
        ),
        "links": (
            ("https://www.hoglezoo.org/field-trips/", "Hogle Zoo Field Trips (official site)"),
            ("https://www.hoglezoo.org/teacher-resources/", "Teacher resources (official site)"),
        ),
        "checked": "Field trip details checked on the zoo’s site in Nov 2026.",
    },
}


def field_trip_block_html(slug: str) -> str:
    cfg = FIELD_TRIP_BLOCKS.get(slug)
    if not cfg:
        return ""
    items = "".join(
        f'\n        <li><strong>{label}</strong> — {blurb} '
        f'<a href="/printables/pdf/letter/{name}.pdf" download data-kz-cta="field-trip">US Letter PDF</a> · '
        f'<a href="/printables/pdf/a4/{name}-a4.pdf" download data-kz-cta="field-trip">A4 PDF</a></li>'
        for name, label, blurb in PDFS
    )
    links = " · ".join(
        f'<a href="{href}" target="_blank" rel="noopener noreferrer">{text} ↗</a>'
        for href, text in cfg["links"]
    )
    return f"""
    <section class="seo-list-block seo-field-trip no-print" id="field-trip" aria-labelledby="field-trip-heading">
      <h2 id="field-trip-heading">{cfg["heading"]}</h2>
      <p>{cfg["lead"]}</p>
      <ul class="seo-field-trip-list">{items}
      </ul>
      <p>{links}</p>
      <p class="seo-checked">{cfg["checked"]}</p>
    </section>"""


def with_field_trip_block(slug: str, html: str) -> str:
    """Insert the block right after the hunt section (or before Explore more). Idempotent."""
    block = field_trip_block_html(slug)
    if not block or 'id="field-trip"' in html:
        return html
    start = html.find('<section class="seo-list-block seo-hunt-block"')
    if start != -1:
        end = html.find("</section>", start) + len("</section>")
        return html[:end] + "\n" + block + html[end:]
    anchor = html.find("<!-- kz-mesh:explore -->")
    if anchor == -1:
        raise ValueError(f"no place for the field-trip block on {slug}")
    return html[:anchor] + block.lstrip("\n") + "\n    " + html[anchor:]
