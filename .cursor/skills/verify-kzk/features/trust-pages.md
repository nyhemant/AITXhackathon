# About, privacy, 404

## Sub-features
- /about/ keeps "Arya’s Wildlife Project".
- /privacy/ names ask@kidzookit.com and says the weekly email runs on Kit, which emails a confirmation first.
- Unknown URLs answer 404 with a way back.
- Security headers on HTML: CSP with `frame-ancestors 'none'`, `X-Content-Type-Options`, `Referrer-Policy`.

## How to get to it (user POV)
Footer links About, FAQ, Privacy, Contact on every page.

## Driving it with verify.py
`--only j7`. Visits the pages above, the newsletter result pages, posts a bad address to `/api/newsletter` with no JS
(303 to `/newsletter/oops/?reason=email`, no Kit call), and checks headers.

## Gotchas
- Privacy wording is a legal/privacy surface: report gaps as owner decisions, do not edit it in a verify pass.
