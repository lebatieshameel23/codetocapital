# CodeToCapital: automated YouTube Shorts pipeline

Every day, with no manual steps after setup:

```
analytics (what held viewers)  ->  free LLM writes scripts + paid kit  ->  free voice (edge-tts)
   ->  video with sound effects, motion and loop ending  ->  scheduled YouTube upload (2 per day)
   ->  bot replies "CODE" comments  ->  product kit zip ready to list in your store
```

See `GROWTH.md` for the monetisation reality check, the funnel, and what was deliberately left out.

**Cost: $0.** Everything runs free:

| Piece | Free service | Card needed? |
|---|---|---|
| Scheduling and rendering | GitHub Actions (free for public repos) | No |
| Script writing | Google Gemini API free tier (key from aistudio.google.com/apikey); optional free backups: Groq, OpenRouter | No |
| Voice | edge-tts (Microsoft Edge voices; unofficial, can break) | No |
| Upload and analytics | YouTube Data / Analytics API | No |

Paid Anthropic is still supported but optional: set `ANTHROPIC_API_KEY` and it is used as the last fallback.
GitHub Models was retired on 30 July 2026, so it is not used.

## Files

| File | Job |
|---|---|
| `config.yaml` | Channel name, slots (12:00 and 18:00 SAST), voice, model, content pillars |
| `generate_scripts.py` | A free LLM writes scripts; each is validated (code must compile, length limits) |
| `llm.py` | Free-LLM client: Gemini, Groq, OpenRouter, optional Anthropic, with automatic failover |
| `voice.py` | Voiceover and word timings |
| `render_video.py`, `sfx.py` | 1080x1920 video: typed code, captions, badges, sound effects, punch-ins, loop ending |
| `analytics_loop.py` | Re-weights topics toward videos that held viewers and gained subscribers |
| `build_kit.py` | Builds the paid kit zip and store listing text for every video |
| `youtube_api.py`, `auth_youtube.py` | YouTube login and scheduled upload |
| `run_daily.py` | The daily orchestrator |
| `reply_bot.py` | Replies to CODE comments |
| `.github/workflows/` | The schedules (daily run, replies every 3 hours) |
| `BRAND.md` | Improved branding and the reasoning behind the changes |
| `GROWTH.md` | Monetisation reality check, funnel, and what was left out and why |

## Setup (about 30 minutes, once)

**1. Test locally (no accounts needed)**
```bash
pip install -r requirements.txt     # needs ffmpeg installed on your computer too
python run_daily.py --dry-run       # renders out/dry-run.mp4 with silent audio
python render_video.py content/samples/episode-01.json   # same, with the real voice
```

**2. Put this folder in a new public GitHub repo** and set `channel.github_repo` in `config.yaml` to `your-username/your-repo`. Public matters: the "comment CODE" links point to `snippets/` in it.

**3. YouTube login**
1. In Google Cloud Console create a project, enable **YouTube Data API v3** and **YouTube Analytics API**.
2. OAuth consent screen: External, add yourself as a test user. Create credentials: **OAuth client ID, type Desktop app**. Download as `client_secret.json` into this folder.
3. Run `python auth_youtube.py` on your computer, sign in with the channel's Google account, and copy the three printed values. (It asks for upload, comment-reply and analytics permissions. If you logged in with an older version of this kit, run it again.)

**4. Get the API project audited (important)**
Videos uploaded through the API by an unaudited project are forced to private and can't be scheduled public. Submit YouTube's API compliance audit form (search "YouTube API Services audit and quota extension form") and mention you're uploading your own channel's videos. Until it's approved, uploads still work but stay private; you can flip them public in YouTube Studio. Default API quota (10,000 units/day) is enough for 2 uploads a day.

**5. GitHub secrets** (repo Settings > Secrets and variables > Actions):
`GEMINI_API_KEY` (free, from aistudio.google.com/apikey), `YT_CLIENT_ID`, `YT_CLIENT_SECRET`, `YT_REFRESH_TOKEN`.
Optional free backup keys: `GROQ_API_KEY` (console.groq.com), `OPENROUTER_API_KEY` (openrouter.ai/keys). Add one: if Gemini is rate limited, the pipeline switches to it.
Also Settings > Actions > General > Workflow permissions: **Read and write**.

**6. Optional: your store.** Create a Payhip, Gumroad or Shopify store. Each daily run publishes that day's kits (zip + listing text) as the `product-kits` artifact on the workflow run page. Upload them, then put your store link in `store.url` in `config.yaml`.

**7. Go live.** Actions tab > "Daily Shorts" > Run workflow. After that it runs by itself at 05:00 SAST every day, generating scripts when the queue runs low and scheduling the next day's 12:00 and 18:00 Shorts.

## Everyday use

- **See the queue:** `content/queue/` (scripts waiting). Delete any you don't like; edit freely.
- **Change the schedule:** `schedule.slots` in `config.yaml`.
- **Change topics:** edit `pillars`. **Change voice:** `voice.name` (list voices with `edge-tts --list-voices`).
- **Add background music:** drop an `.mp3` you have rights to in `assets/music/`.
- **Post 3 a day:** add a third time to `schedule.slots`. Quality matters more than volume, so watch the analytics before you do.
- **Turn effects off:** `motion: false` or `sfx: false` in `config.yaml`.
- **See what the loop learned:** `content/performance.json`.
- **Refresh tokens:** if the Google project is left in "Testing" status, the refresh token expires after 7 days. Publish the OAuth consent screen ("In production") to avoid that.

## Honest limits

- Scheduling and replies run on GitHub's servers, so your computer can stay off.
- I tested script validation, rendering (with sound effects), the analytics re-weighting, kit building and the whole daily run here, using local stand-in servers for the LLM providers and stand-ins for edge-tts and YouTube and silent placeholder voice audio. The real Gemini/Groq, edge-tts and YouTube calls need your keys and network access, so the first live run is the real test: run the workflow by hand and check the first video in YouTube Studio before trusting the daily schedule.
- Review the first week of generated scripts. The validator checks that code compiles and fits the screen, not that it does what the narration claims.
- Free-tier limits change without notice, and Google no longer publishes per-model numbers (see aistudio.google.com/rate-limit for yours). This pipeline needs only a handful of requests a day (about 2 scripts plus retries). If a model id stops working the log shows `HTTP 404`; edit the model name under `ai:` in `config.yaml`.
- Free Gemini keys may let Google use prompts to improve its products. Nothing private is sent: only topic prompts.
- Free models write weaker code than paid ones, which is why every script must compile and pass the limits before it is queued, and why reviewing the first week matters.
