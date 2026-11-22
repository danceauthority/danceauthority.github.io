# About AST 2026 (Austin Studio Tour Mission Control)

This file is the technical log. The project's front door (status, decisions, next steps) is Ryan's Obsidian vault: `Personal/Projects/Austin Studio Tour Mission Control/_About Austin Studio Tour Mission Control.md`. Data exports: **Personal Drive** (ryangossen@gmail.com) › Projects › Austin Studio Tour Mission Control.

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
- **Menu (☰).** Holds the tour-day picker, the crew status, sharing and import, and demo on/off. The green dot on the button means crew sync is connected.
- **Map follows the tab.** Route zooms to your route and fades other stops. Studios shows only the studios that match your search and filters. Meet shows the proposed meetup spots with time labels. Crew shows everyone's live position with name labels.
- **Map first.** The map is the main screen. Tapping a stop opens its full listing in the bottom drawer: hours, parking notes, each artist's photo, "what to expect" and bio. **Plan mode** makes each tap add or remove a stop, which is the fast way to build a route.
- **Route.** Drawn along bike-friendly streets using the free OSRM bike router (routing.openstreetmap.de). If that service is down, it falls back to straight dashed lines. "Optimize order" re-sorts the remaining stops into the shortest ride starting from where you are. ETAs use your pace (default 9 mph) plus time at each stop (default 20 min) and flag anything after 5pm.
- **After each stop.** Tap "I'm here" (or accept the automatic "You're at #18" prompt when GPS is on). The app marks the stop visited, shows the planned next stop and suggests 3 nearby ones.
- **Meetups.** Drop a pin (the coral pin button on the map, or Meet › Drop a pin) and the app asks for a time right away. You can also start from a stop or from where you are now. Every proposed time and place shows a 👍 / 👎 list of who can and can't make it, plus who hasn't answered yet. Anyone can propose another time and place. The option with the most 👍 rises to the top, and anyone can lock it in. Only the person who proposed an option can withdraw it, and only the person who started a meetup can delete it.
- **GPS (opt-in, two levels).**
  1. *Use my location on this phone.* This gives the blue dot, distances and the "you're at a stop" check-in prompt. Nothing leaves the phone.
  2. *Share my location* (one switch on the Crew tab): in a crew, others see your dot. It turns itself off after 8 hours, and it's removed when the person switches it off or closes the page. Updates go out about every 90 seconds or every 60 m moved. Phones only send updates while the page is open on screen, which is a browser limit.
- **Demo crew** (add `?demo=1` to the address): loads sample data for 7 riders. You, Maya, Jordan and Priya are together at Canopy partway through the shared route. Sam, Alex and Tess are on their own around town, with live dots that drift. Sam and Alex have proposed conflicting lunch plans that are tied 3–3. Nothing in demo mode is saved or sent anywhere.
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
- Nov 14, 2026: Crew sync turned on — Firebase project "ast-mc" (personal Google account, ryangossen@gmail.com), Realtime Database in the US, anonymous sign-in, rules from database.rules.json published.
- Nov 11, 2026: Meetups changed to 👍/👎 per proposed time and place, with name lists; dropping a pin goes straight to choosing a time.
- Nov 10, 2026: v2 built (map-first planning, full descriptions, real bike route lines, meetup voting, opt-in GPS, Firebase sync).
- Tested in a phone-size browser in solo mode and with two simulated crew members (shared route, proposals, votes, live location). It hasn't been tested against a real Firebase project yet, so do a two-phone test before Saturday.

## Finding other crews
- **Public list (`directory`):** shows each crew's **name, rider count and when it was last active**. Crews drop off after 14 hours of inactivity. The secret crew code is never listed, because anyone with the code could read the crew's route and live locations.
- **Asking to join:** someone not in a crew (or in another one) taps **Ask to join**. Every member of that crew sees "X asking to join" on the Crew tab, with **Let in** or **Decline**. Letting someone in hands their phone the crew code, and it joins automatically.
- **Where other crews are:** the list also shows the studio a crew most recently checked in at (or its next planned stop). Tapping the crew shows that studio on the map. Exact GPS positions are only ever visible inside a crew.
- **Hiding a crew:** the "We're listed / We're hidden" switch on the Crew tab takes the crew off the public list. Invite links still work.
- Behind the scenes: `crews/<code>/pub` holds the crew's public ID, `pubmembers/<pubId>/<person>` proves membership (the rules check it), and requests live in `joinreq/<pubId>/<person>`.

## Usage study (Nov 14, 2026)
- **What's recorded:** button taps, tabs, studios opened, route changes (full stop list each time), check-ins (manual and the automatic "You're at #…" prompt), handoffs to Apple/Google Maps, meetup actions, location on/off, search terms, filters, the app going to the background and coming back, connection drops, location-permission errors, failed bike routes or map images, and script errors. Each event has a timestamp, an anonymous phone ID (the same one used in the crew) and the crew code. No names.
- **Ride paths:** saved only for people who ticked "Also save my ride path" (in the first-visit notice, or later in the ☰ menu), and only while their location sharing is on. One point every ~60 m or 90 s.
- **Consent:** everyone sees a one-time notice on first open. "Don't record me" turns it off, and the ☰ menu has on/off switches for both.
- **Where it goes:** Firebase › Realtime Database › `study/<phone id>/<batch>`. Events are sent in batches about every 20 seconds and whenever the app goes to the background. Nobody can read it from the app; only you can, from the Firebase console.
- **Getting the data:** Firebase console › Realtime Database › Data › click `study` › ⋮ menu › **Export JSON**. Send me the file to analyze. Crew names and routes are under `crews` (export that too for planned-vs-actual).
- **When done:** delete the `study` node (⋮ › Delete) once you have what you need.

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
- 2026-11-14: Tap a rider in your crew to jump the map to them (live dot, or their last check-in). Tap another crew in the list to see the studio they're at, or heading to. Only the studio is shared with other crews, never anyone's GPS position.
- 2026-11-14: Crew list and join requests (public list shows names only; any member can let people in). Rules updated — re-paste database.rules.json.
- 2026-11-14: Usage study instrumentation added (event log, sessions, planned vs actual, errors; ride paths opt-in). Rules updated with a write-only `study` section — re-paste database.rules.json.
- 2026-11-14: Fix: crew dots no longer blink on and off (markers update in place); friends draw on top of your own dot; Route view includes riders within 2.5 mi. Crew list tags each rider 📍 live / last seen / location off.
- 2026-11-14: Crew tab condensed: crew name at the top (tap to rename; set when the crew is started), riders listed right under it, and a single "Share my location" switch (shares with the crew, turns off after 8 hours). Crew name is saved with the crew route.
- 2026-11-14: Fix: people who open the invite link now appear in the crew right away, even before entering a name (shown as "New rider (no name yet)").
- 2026-11-14: Slimmer header; menu has "Start fresh on this phone" (clears this phone's route, stars, name and crew link).
- 2026-11-10: Created folder; first version published.
- 2026-11-14: Renamed the app to "Austin Studio Tour Mission Control".
- 2026-11-14: Tried game-piece icons for crew members (emoji, then silhouettes) and went back to letters in a purple circle.
- 2026-11-14: One route only — in a crew, everyone uses the crew route (the "Just mine" option is gone; stops planned before joining become the crew route if it is still empty). "Stops" tab renamed "Studios". Title and menu button centered.
- 2026-11-14: Bottom panel can be dragged from anywhere (handle, tabs, or the list when it's scrolled to the top); a "Show the map" button appears when it's fully open.
- 2026-11-14: One-line title; the day picker and crew status moved into a menu (☰, green dot = crew connected). Switching Route / Stops / Meet / Crew now moves the map to show those items and fades everything else.
- 2026-11-11: Added demo crew (`?demo=1`), a close (X) button on every pop-up, and renamed the meetup form to "Propose a meetup" with the field "Proposed time to meet".
- 2026-11-11: Meetup 👍/👎 responses replace single-choice votes (Firebase path `meetups/<id>/rsvp/<option>/<person>`). Re-paste `database.rules.json` if Firebase was already set up.

- 2026-11-14: Location sharing now survives page reloads (iPhones reload background tabs often), and a rider's dot no longer disappears when their phone locks; it shows their last position, up to 30 minutes old.
- 2026-11-14: When a crew member opens the app with location off, a banner offers one tap to turn it on.
- 2026-11-14: Whoever proposed a meetup time can change its time or place (✎ Change time/place). Changing it clears the old votes so the crew answers again.
- 2026-11-15: From the Day 1 usage study: automatic check-in after 3 minutes at a studio (with Undo); next-meetup card at the top of the map with one-tap 👍/👎; the name prompt can't be dismissed without a name; step-by-step help when the phone blocks location. Add to Home Screen tip was dropped: on iPhone a home-screen copy has separate storage, so riders would have to rejoin and would appear twice.
- 2026-11-15: App opens on the Crew tab with the list collapsed and the map fitted to the crew. Tabs reordered: Crew, Studios, Meet, Route. "Plan mode" renamed "＋ Add studios" ("✓ Done adding" when on); while on, every open studio shows on the map, larger and tappable.
- 2026-11-15: Joining asks for a name (aliases fine) and offers "Join and share my location" or "Just looking". Just-looking riders see the crew, show to others as 👀 just looking, and aren't nudged to share.
- 2026-11-15: Add to Home Screen: menu item and a one-time hint on a phone's second open; app icon and manifest. On iPhone the home-screen copy has its own storage, so the app hands over crew, name and just-looking choice in the link while the instructions are open (only honoured inside the home-screen app), and the old browser identity is hidden from the crew list.
- 2026-11-15: Adding a studio puts the route in the shortest order automatically (from the rider's location, exact for up to 10 remaining stops; visited stops and a "Go next" choice stay put; Undo restores the previous order).
- 2026-11-15: Route tab: "⇅ Reverse order" button next to Optimize order (visited stops stay put; Undo).
- 2026-11-22: Renamed to *Studio Tourist* (header: "Studio Tourist · austin studio tour 11.22.26"; home-screen name Studio Tourist).
- 2026-11-22: Riders who haven't opened the app in 18 hours are hidden from the crew list, map and counts, with a one-line note (last weekend's crew had been reused).
