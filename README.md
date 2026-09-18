<a id="readme-top"></a>

[![License][license-shield]][license-url]

<br />
<div align="center">
  <h3 align="center">🎯 Job Hunter Agent</h3>

  <p align="center">
    An AI-driven job discovery and matching pipeline — with an honest account of what works and what doesn't.
  </p>
</div>

## ⚠️ Current Status: Discovery & Matching Work; Full Auto-Submit Does Not (Yet)

This project started as an attempt to fully automate job applications end-to-end. Building it surfaced real, load-bearing engineering constraints that are documented here rather than glossed over.

### What actually works, verified with real data

- **Multi-source real job aggregation** — pulls live listings from We Work Remotely (RSS), Himalayas.app (public JSON API), Web3.career (official API), and Remote OK (public API), with automatic retry on network failures (`tenacity`)
- **LLM-based match scoring** — evaluates each job description against the candidate's real resume using a 1-10 scale (not a fake percentage), with an explicit industry-relevance gate (rejects jobs at companies that aren't genuinely AI/tech-core, regardless of surface keyword overlap)
- **Anti-hallucination resume tailoring** — generates a job-specific summary strictly from facts already in the master resume, verified against real job postings
- **Honest failure detection** — when a job application page is protected by Cloudflare or similar bot-detection, the system detects this and flags it for manual handling instead of falsely reporting success
- **Telegram notification pipeline** — daily summary of qualified jobs, delivered and verified against a real Telegram bot

### What doesn't work reliably (and why)

- **Most job application pages are protected against automation.** In real testing, the majority of qualified listings hit CAPTCHA/bot-detection walls (Cloudflare, etc.) before a form could even be filled. This isn't a bug to be fixed with more retries — it's a structural limit of automating against sites designed to block automation.
- **The target job category (AI ecosystem/GTM/strategic partnerships) is genuinely scarce** across the aggregated sources. On a typical day, ~400 real listings yield single digits of qualified matches after strict filtering — not because the filters are broken, but because this is a narrow niche.
- **LLM scoring consistency has limits.** The same job can occasionally receive different scores across separate evaluation runs, a known characteristic of LLM-based judgment rather than a deterministic bug.
- **Platforms like LinkedIn and Indeed are explicitly excluded** — their terms of service prohibit automated application submission, and real-world reports show accounts get restricted for this.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Architecture

| Component | File | What it does |
|---|---|---|
| Multi-source Fetcher | `fetcher.py` | Real API/RSS calls to 4 job boards, with retry logic |
| Title Pre-filter | `target_roles.py` | Keyword-based first-pass filter (fast, free) |
| LLM Match Scorer | `llm_matcher.py` | 1-10 scale scoring with industry-relevance gate |
| Resume Tailoring | `tailor_llm.py` | LLM-generated, anti-hallucination job-specific summaries |
| Form Automation | `pipeline/auto_submitter.py` | Playwright-based form filling with CAPTCHA detection |
| Pipeline Orchestration | `daily_pipeline.py` | Ties everything together, sends Telegram summary |
| Confirmation Handler | `check_confirmations.py` | Processes user's "confirm N" replies for actual submission |

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Getting Started

### Prerequisites

* Python 3.10+
* A SiliconFlow (or OpenAI-compatible) API key
* A master resume in PDF format
* A Telegram bot token

### Installation

```sh
git clone https://github.com/Sentinel-0x/job-hunter-agent.git
cd job-hunter-agent
pip install -r requirements.txt
playwright install chromium
```

Configure `.env` with your API keys, resume path, and Telegram credentials (see `data/base_resume.example.md` for the expected resume format).

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Usage

```sh
python3 daily_pipeline.py
```

This fetches real jobs, filters and scores them against your resume, generates tailored summaries for matches, checks each for CAPTCHA/bot-detection, and sends a Telegram summary. Jobs that pass automated form-filling wait for a manual `确认 N` reply before final submission; jobs blocked by CAPTCHA are flagged for manual application.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Lessons Learned

Building this surfaced a broader pattern worth naming: automating against consumer-facing web platforms increasingly runs into deliberate anti-bot infrastructure, and "full automation" claims in this space should be treated with skepticism until verified against live systems — which is exactly what this project did.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## License

Distributed under the MIT License. See `LICENSE` for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- MARKDOWN LINKS & IMAGES -->
[license-shield]: https://img.shields.io/github/license/Sentinel-0x/job-hunter-agent.svg?style=for-the-badge
[license-url]: https://github.com/Sentinel-0x/job-hunter-agent/blob/main/LICENSE

