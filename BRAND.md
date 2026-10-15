# CodeToCapital: improved brand and concept kit

## What I changed from the original kit, and why

| Original | Problem | Now |
|---|---|---|
| "A client was paying $800/month... saved $10,000 in one afternoon" | Invented client story presented as true. The maths also doesn't hold: $800/month is $9,600 a year, not $10,000 in an afternoon. Fake case studies risk viewer trust and platform deception rules. | Hypothetical framing ("Say you pay someone $800 a month...") with correct arithmetic on screen ($800/mo = $9,600/yr), and an "illustrative demo" label in every video. |
| "5 lines of code" + "1,000 PDFs in 3 seconds" | Unverifiable claims; viewers who try the code will check them. | Real snippets of at most 10 lines that compile (the pipeline rejects any script whose code doesn't), plus one honest limitation per video. |
| AI-generated 3D clips (Kling / Google Flow) | Manual, credit-limited, inconsistent look, can't be automated for free. | Programmatic visuals: code typing live in a terminal. Fully automated, consistent branding, and the code on screen is the proof. |
| Manual CapCut captions | 5+ minutes per video. | Word-synced captions burned in automatically. |
| Manual upload and posting | Daily chore. | Scheduled upload through the YouTube API, 2 per day. |
| "Comment CODE" with no delivery | Someone has to reply by hand. | Each Short's code is published to `snippets/` on GitHub and a bot replies with the link. |
| "Claude 3.5 Sonnet" | Outdated model. | `claude-sonnet-5-5` (change in `config.yaml`). |

## Identity

- **Name:** CodeToCapital, handle `@codetocapital`. Check the handle is free on YouTube before you commit; I can't verify availability from here. Fallbacks: SyntaxToCash, ScriptingMoney.
- **Tagline:** Code. Automate. Save Thousands. (Keep "thousands" as the direction of the channel, not a promise in any single video.)
- **Bio:** Short Python and automation scripts that replace boring manual work. New Short daily. Full code for every video is on GitHub: comment CODE and I'll send the link.
- **Colours:** Slate `#1E1E2E` (background), Terminal Green `#00FF66` (accent), Yellow `#FFE600` (highlight words and badges). Already used by the renderer.
- **Profile picture:** neon-green `{ $ }` on the dark slate background.
- **Banner:** "Code. Automate. Save Thousands." Keep key text in the centre; banners crop heavily on mobile.

## Format rules (baked into the generator)

1. Hook in the first 3 seconds, ideally a cost the viewer recognises.
2. 25 to 35 seconds. Five beats. Code appears line by line as it's explained.
3. Money is always framed as "say you pay..." with the arithmetic visible.
4. The last beat gives one real limitation and the CODE call to action.
5. Eight rotating content pillars (see `config.yaml`) so the feed doesn't become one repeated template.

## Risks to know about before you scale

- **Templated, mass-produced content.** YouTube's monetisation policies target repetitive, low-effort or mass-produced content (the policy was reworded in 2025; check the current "inauthentic content" wording in YouTube Help). The pillars, real code and honest framing help, but review the queue now and then, delete weak scripts, and add your own face, voice or commentary over time if you want to monetise.
- **Monetisation thresholds change.** Check YouTube Partner Program requirements for Shorts in YouTube Help rather than trusting any number I'd quote.
- **API uploads can be locked private.** Videos uploaded through the API from an unaudited Google Cloud project are restricted to private until the project passes YouTube's API compliance audit. See README, step 4.
- **Synthetic voice disclosure.** A TTS voice reading a coding tutorial is not a realistic depiction of a person, but check YouTube's current altered/synthetic content disclosure rules and tick the box if they apply.
- **Music.** The pipeline only mixes in audio you place in `assets/music/`. Use tracks you have rights to; don't use random downloads.
