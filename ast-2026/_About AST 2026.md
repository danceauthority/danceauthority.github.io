# About AST 2026 (Studio Tour Crew)

## What this is
A phone web app for riding the Austin Studio Tour (Nov 14–15 and 21–22, 2026) by bike with a group. You plan on the map first: tap studios to add them to a route, see the bike route drawn on the map, re-plan after each stop, set up meetups that the crew votes on, and hand off turn-by-turn directions to Apple Maps or Google Maps.

Live address once published: https://danceauthority.github.io/ast-2026/

## What's here
| File | What it is |
|---|---|
| `index.html` | The whole app: layout, styles and code |
| `data.js` | Studio data for all 270 tour locations and 672 artists, groups and hosts, copied from https://atxstudiotour.com/explore/ on Nov 10, 2026 |
| `config.js` | Crew sync settings. Set to `null` = solo mode (works without any setup) |
| `database.rules.json` | Security rules to paste into Firebase if you turn on crew sync |
| `tools/make_data.py` | The script that turned the scraped site data into `data.js` (for reference) |

## How it works
- **Map first.** The map is the main screen. Tapping a stop opens its full listing in the bottom drawer: hours, parking notes, each artist's photo, "what to expect" and bio. **Plan mode** makes each tap add or remove a stop, which is the fast way to build a route.
- **Route.** Drawn along bike-friendly streets using the free OSRM bike router (routing.openstreetmap.de). If that service is down, it falls back to straight dashed lines. "Optimize order" re-sorts the remaining stops into the shortest ride starting from where you are. ETAs use your pace (default 9 mph) plus time at each stop (default 20 min) and flag anything after 5pm.
- **After each stop.** Tap "I'm here" (or accept the automatic "You're at #18" prompt when GPS is on). The app marks the stop visited, shows the planned next stop and suggests 3 nearby ones.
- **Meetups.** Drop a pin (the coral pin button on the map, or Meet › Drop a pin) and the app asks for a time right away. You can also start from a stop or from where you are now. Every proposed time and place shows a 👍 / 👎 list of who can and can't make it, plus who hasn't answered yet. Anyone can propose another time and place. The option with the most 👍 rises to the top, and anyone can lock it in. Only the person who proposed an option can withdraw it, and only the person who started a meetup can delete it.
- **GPS (opt-in, two levels).**
  1. *Use my location on this phone.* This gives the blue dot, distances and the "you're at a stop" check-in prompt. Nothing leaves the phone.
  2. *Share live location with the crew* for 1, 3 or 6 hours. It turns itself off when the time is up, and it's removed when the person switches it off or closes the page. Updates go out about every 90 seconds or every 60 m moved. Phones only send updates while the page is open on screen, which is a browser limit.
- **Solo mode** (no Firebase): everything is saved on each phone, and routes and meetups can be shared as text or as a `?plan=18,101,33` link.

## Turning on crew sync (one-time, about 15 minutes)
This needs your personal Google account (ryangossen@gmail.com). Nothing in here is Lachesis.
1. Go to https://console.firebase.google.com and click **Create a project** (any name, e.g. `ast-crew`). Google Analytics is not needed.
2. **Build › Authentication › Get started › Sign-in method**: enable **Anonymous**.
3. **Build › Realtime Database › Create database** (location: United States) and start in **locked mode**.
4. In the Realtime Database **Rules** tab, replace everything with the contents of `database.rules.json` and click **Publish**.
5. **Project settings (gear) › Your apps › Web (`</>`)**: register an app (no hosting). Copy the `firebaseConfig` values.
6. In `config.js`, replace `window.AST_FIREBASE = null;` with your values. It must include `databaseURL`. Commit the change.
7. Optional hardening: in Google Cloud console › APIs & Services › Credentials, restrict the browser API key to the referrer `https://danceauthority.github.io/*`.
8. Open the app, go to **Crew › Start a crew**, enter your name, and send the invite link to everyone.

The Firebase web config is not a secret. Google designs it to sit in public web pages. The security rules are what protect the data.

## Where it stands
- Nov 11, 2026: Meetups changed to 👍/👎 per proposed time and place, with name lists; dropping a pin goes straight to choosing a time.
- Nov 10, 2026: v2 built (map-first planning, full descriptions, real bike route lines, meetup voting, opt-in GPS, Firebase sync).
- Tested in a phone-size browser in solo mode and with two simulated crew members (shared route, proposals, votes, live location). It hasn't been tested against a real Firebase project yet, so do a two-phone test before Saturday.

## Rules and security
- **Who can see a crew:** anyone with the crew link, signed in anonymously. Crew codes are 12 random characters, long enough to be unguessable. The rules refuse crew codes shorter than 10 characters.
- **What people can change:** each person can only write their own name, check-in, live position and votes. Anyone in the crew can edit the shared route and lock or unlock meetups. Each person can only set their own 👍/👎. Only the author can edit or withdraw their own meetup proposal or delete their own meetup.
- **Live location** is only written after the person opts in. It's deleted when they stop sharing or disconnect, and other phones hide it if it's more than 30 minutes old.
- **Third-party services the app calls:** OpenStreetMap map images (tile.openstreetmap.org), the OSRM bike router (routing.openstreetmap.de, which receives the route's coordinates), artist photos linked from atxstudiotour.com, Leaflet from unpkg.com, and Firebase (Google) only if configured.

## Working notes for whoever helps
- The data is a snapshot. To refresh it, re-scrape https://atxstudiotour.com/explore/ and rebuild `data.js` with `tools/make_data.py`. The site's map has a `data-markers` attribute with location numbers and coordinates, the profile list loads through `admin-ajax.php` (`listing_load_more`), and each profile page has the medium, hours, bio and "What to expect" text.
- Records in `data.js`: `L` = locations `{n, lat, lng, a=address, v=venue, d=day bits, h=hours, f=family, x=activities, nav=parking notes}`. `P` = people `[name, type A/G/H, medium ids, [[loc, day bits, hours]], what-to-expect, profile path, bio, photo path, host category]`. `M` = medium names. Day bits: 1 = Sat 11/14, 2 = Sun 11/15, 4 = Sat 11/21, 8 = Sun 11/22.
- Phone storage key: `ast26-crew-v2`.

## Log
- 2026-11-10: Created folder; first version published.
- 2026-11-11: Meetup 👍/👎 responses replace single-choice votes (Firebase path `meetups/<id>/rsvp/<option>/<person>`). Re-paste `database.rules.json` if Firebase was already set up.
