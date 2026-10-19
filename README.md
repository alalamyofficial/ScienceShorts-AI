# ScienceShorts AI (zero-budget starter)

Creates three vertical English science-fact videos per run using a curated starter fact bank, online Edge TTS, locally generated graphics, FFmpeg and timed captions. It does not require an LLM API key, but scripts are template/curated rather than freshly invented by an AI model. Verify every fact and source before publishing.

## Run locally or on a Linux cloud runner

Requires Python 3.10+, FFmpeg + ffprobe, and network access for Edge TTS.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

On Windows activate with `.venv\\Scripts\\activate` after creating the environment. Install FFmpeg separately and ensure `ffmpeg` and `ffprobe` are on PATH.

Output: `output/*.mp4`, `.srt`, `.json`, and `manifest.json`.

## GitHub Actions

Copy `.github/workflows/daily.yml` into a GitHub repository. For public repos, workflow logs and code are public; never commit tokens. Scheduled runs can be delayed and free service limits can change. This workflow generates videos and stores them as a 7-day artifact; it does not persist files to a server.

## TikTok publishing

This starter intentionally does not upload automatically. TikTok Direct Post requires a registered developer app, approved `video.publish` scope, OAuth authorization, creator-info/privacy UI and user consent. Un-audited apps are restricted to private-only posts; public posting requires TikTok's audit. TikTok's guidelines also say an app intended only as a utility for posting to accounts managed by the developer/team is not an acceptable use case. Therefore do not assume a private automation script will be approved. Official docs: https://developers.tiktok.com/docs/en/content-posting-api-get-started and https://developers.tiktok.com/docs/en/content-sharing-guidelines

Once an app is approved for your legitimate product use, integrate the official API according to its current documentation and provide the required creator-facing confirmation flow. Do not use browser bots, fake region data, or unofficial endpoints.

## Accuracy and monetization

The built-in facts are starter examples with source pointers, not a guarantee of editorial accuracy. Check the source URLs, improve citations, and review audio/captions. Synthetic/AI-generated content should be labelled when TikTok requires it. Eligibility for Creator Rewards and earnings are not guaranteed.
