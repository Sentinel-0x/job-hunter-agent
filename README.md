<a id="readme-top"></a>

[![License][license-shield]][license-url]

<br />
<div align="center">
  <h3 align="center">🎯 Job Hunter Agent</h3>

  <p align="center">
    An automated job-application pipeline — red-team JD scoring, anti-hallucination resume tailoring, and SQLite-tracked submission history.
    <br />
    <a href="https://github.com/Sentinel-0x/job-hunter-agent"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="https://github.com/Sentinel-0x/job-hunter-agent/issues/new?labels=bug">Report Bug</a>
    ·
    <a href="https://github.com/Sentinel-0x/job-hunter-agent/issues/new?labels=enhancement">Request Feature</a>
<a id="readme-top"></a>

[![License][license-shield]][license-url]
[![Python][Python-badge]][Python-url]
[![OpenAI][OpenAI-badge]][OpenAI-url]
[![SQLite][SQLite-badge]][SQLite-url]

<br />
<div align="center">
  <h3 align="center">🎯 Job Hunter Agent</h3>

  <p align="center">
    An automated job-application pipeline — red-team JD scoring, anti-hallucination resume tailoring, and SQLite-tracked submission history.
    <br />
    <a href="https://github.com/Sentinel-0x/job-hunter-agent"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="https://github.com/Sentinel-0x/job-hunter-agent/issues/new?labels=bug">Report Bug</a>
    ·
    <a href="https://github.com/Sentinel-0x/job-hunter-agent/issues/new?labels=enhancement">Request Feature</a>
  </p>
</div>

<details>
  <summary>Table of Contents</summary>
  <ol>
    <li><a href="#about-the-project">About The Project</a>
      <ul><li><a href="#built-with">Built With</a></li></ul>
    </li>
    <li><a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#architecture">Architecture</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
  </ol>
</details>

## About The Project

Manually screening job postings and tailoring a resume for each one doesn't scale. This project automates the pipeline end to end: it evaluates a job description against a candidate's real background using a strict "red-team" LLM reviewer, tailors the resume **only** using facts that already exist in the master resume (no fabricated experience), tracks every decision in SQLite, and pushes submission results to Telegram.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Built With

* [![Python][Python-badge]][Python-url]
* [![OpenAI][OpenAI-badge]][OpenAI-url]
* [![SQLite][SQLite-badge]][SQLite-url]

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Getting Started

### Prerequisites

* Python 3.10 or higher
* OpenAI API Key (or compatible LLM provider)

### Installation

1. Clone the repository:
   ```bash
   git clone [https://github.com/Sentinel-0x/job-hunter-agent.git](https://github.com/Sentinel-0x/job-hunter-agent.git)
   cd job-hunter-agent  </p>
</div>

<details>
  <summary>Table of Contents</summary>
  <ol>
    <li><a href="#about-the-project">About The Project</a>
      <ul><li><a href="#built-with">Built With</a></li></ul>
    </li>
    <li><a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#architecture">Architecture</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
  </ol>
</details>

## About The Project

Manually screening job postings and tailoring a resume for each one doesn't scale. This project automates the pipeline end to end: it evaluates a job description against a candidate's real background using a strict "red-team" LLM reviewer, tailors the resume **only** using facts that already exist in the master resume (no fabricated experience), tracks every decision in SQLite, and pushes submission results to Telegram.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Built With

* [![Python][Python-badge]][Python-url]
* [![OpenAI][OpenAI-badge]][OpenAI-url]
* [![SQLite][SQLite-badge]][SQLite-url]

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Getting Started

### Prerequisites

*

Every job goes through `evaluate_job_redteam()` — a strict LLM reviewer that scores the match 0–10 and returns a `PASS`/`REJECT` verdict with pros/cons. Only jobs that pass get a tailored resume via `tailor_resume()`, which is explicitly constrained to never invent experience not present in the master resume.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Architecture

| Component | File | What it does |
|---|---|---|
| Pipeline Core | `job_agent.py` | `JobHunterPipeline` — red-team JD scoring, anti-hallucination resume tailoring, orchestrates the full per-job flow |
| Persistence | `job_agent.py` (`JobHunterDatabase`) | SQLite table tracking `id, title, company, description, score, status, tailored_resume` per job |
| Resume Reader | `pipeline/tailor.py` | `ResumeTailor` — extracts text from the master resume PDF (`pypdf`), generates position-specific summaries |
| Job Fetching | `run_job_hunter.py` | Pulls candidate postings from configured sources |
| Submission | `pipeline/auto_submitter.py` | Browser automation for form submission |

> Note: `pipeline/database.py` and `pipeline/resume_optimizer.py` also exist in this repo — their interfaces are still being consolidated with the components above.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Roadmap

- [x] Red-team JD scoring (0–10, PASS/REJECT verdict)
- [x] Anti-hallucination resume tailoring
- [x] SQLite job/status tracking
- [x] Telegram submission notifications
- [ ] Consolidate `pipeline/database.py` and `pipeline/resume_optimizer.py` into a single interface
- [ ] Evaluate integrating [`sentinel-react-engine`](https://github.com/Sentinel-0x/sentinel-react-engine) for retry/checkpoint logic
- [ ] Add automated test coverage for the submission flow

See the [open issues](https://github.com/Sentinel-0x/job-hunter-agent/issues) for a full list of proposed features.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Contributing

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## License

Distributed under the MIT License. See `LICENSE` for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Contact

Project Link: [https://github.com/Sentinel-0x/job-hunter-agent](https://github.com/Sentinel-0x/job-hunter-agent)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- MARKDOWN LINKS & IMAGES -->
[license-shield]: https://img.shields.io/github/license/Sentinel-0x/job-hunter-agent.svg?style=for-the-badge
[license-url]: https://github.com/Sentinel-0x/job-hunter-agent/blob/main/LICENSE
[Python-badge]: https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white
[Python-url]: https://www.python.org/
[OpenAI-badge]: https://img.shields.io/badge/LLM-GPT--4o--mini-412991?style=for-the-badge&logo=openai&logoColor=white
[OpenAI-url]: https://openai.com/
[SQLite-badge]: https://img.shields.io/badge/SQLite-job%20tracking-003B57?style=for-the-badge&logo=sqlite&logoColor=white
[SQLite-url]: https://www.sqlite.org/
