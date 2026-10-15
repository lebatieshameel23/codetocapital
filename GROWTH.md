# Growth and monetisation: what's built, what's honest

## Reality check on monetisation (checked 14 Oct 2026)

- **Shorts ad revenue** is limited to channels with at least **10 million Shorts views in 90 days** ([Tubefilter](https://www.tubefilter.com/2026/08/10/youtube-partner-program-ad-eligibility-requirements-shorts/)). That is roughly 110,000 views a day, every day.
- **YPP for new applicants** gets tougher from **1 Feb 2027**: 8,000 watch hours in 365 days, or 20 million Shorts views in 90 days. Current partners are grandfathered ([Tubefilter](https://www.tubefilter.com/2026/08/10/youtube-partner-program-ad-eligibility-requirements-shorts/)).
- **Early tier** (fan funding, memberships, shopping): 500 subscribers, 3 public uploads in 90 days, plus 3,000 watch hours or 3 million Shorts views ([vidIQ](https://vidiq.com/blog/post/monetize-youtube-guide/)).
- **Do the arithmetic on the other plan's RPM figure.** At $0.07 to $0.20 per 1,000 views (I can't verify those numbers), 10 million views is about $700 to $2,000 per 90 days. Shorts ad money is small even when you qualify.

So the product kit is the realistic early income, and subscribers matter more than raw views. Nobody can guarantee views, and anything promising a number is selling you something.

## What the pipeline does to earn views honestly

| Lever | How it's built in |
|---|---|
| Hook in 2 seconds | Six rotating hook styles (cost, mistake, time, curiosity, result-first, myth). The promise must be paid off in the video. |
| Seamless loop | The last sentence is written to flow into the first, and the video ends 0.12 s after the last word, so replays feel continuous. |
| Constant motion | Punch-in on every beat, drifting grid, blinking cursor, success flash. |
| Sound | Synthesised typing clicks, whooshes, ding and pop (no licensing issues). |
| Word-synced captions | The current word is highlighted in yellow. |
| Series feel | Episode number (#001, #002...) in the corner. |
| Learning loop | `analytics_loop.py` scores each video by views x average % viewed + 50 x subscribers gained, then makes topics that hold viewers more likely to be picked. Every topic keeps at least 30% of its normal weight so the channel keeps exploring. |

## The funnel

1. **Free core code** on GitHub for every Short. Comment CODE and the bot replies with the link. This builds trust and subscribers.
2. **Paid kit** per video (`out/kits/<slug>.zip` and `<slug>.listing.txt`): a robust `tool.py` with a command-line interface, error handling and logging, plus a setup guide. The listing text is ready to paste.
3. **Store.** Create a Payhip, Gumroad or Shopify store, upload the zips, then set `store.url` in `config.yaml`. The link then appears in descriptions and comment replies, labelled "paid, I sell this". Each daily run uploads that day's kits as a GitHub Actions artifact (Actions tab > the run > product-kits).

I couldn't find a way for a script to create products on Payhip or Gumroad, so listing the zips is a manual two-minute step per kit. If you use your Shopify store, I can publish kits there for you from a Claude chat when you tell me to.

## What I deliberately left out of the other plan, and why

- **"Saved $10,000 in one afternoon" and "deleted 14,000 emails in 8 seconds."** Invented results. They fail the first time a viewer tries the code, and selling a $5 product on a made-up claim is misleading to buyers.
- **The lead scraper** pulling contact details of private people. It runs into privacy law (POPIA in South Africa, GDPR elsewhere) and platform terms. I replaced it with pulling public data from official APIs.
- **Amazon price scraping.** Against Amazon's terms. Replaced with alerts for pages and files you're allowed to monitor.
- **Gmail bulk deletion.** Irreversible. Inbox topics now require a dry-run mode.
- **Posting the same video to TikTok and Instagram automatically.** Their posting APIs need app review before they publish publicly, and posting from bots to personal accounts violates their terms. Exporting `out/<slug>.mp4` and using each app's own scheduler works today; I can add direct posting once you have approved API access.

## Risks to keep an eye on

- YouTube reviews channels for "reused, repetitive or low-originality content" at YPP application. A template is fine; 500 near-identical videos is not. Delete weak scripts from `content/queue/`, keep the topic list wide, and add your own voice or face over time.
- The validator proves the code compiles and fits on screen. It does not prove the code works on real files or that the kit README is accurate. Run each kit once before you list it.
- Consider the first 30 videos an experiment. The analytics loop only starts steering after 6 videos are at least 3 days old.
