# Video script: Production and handoff (about 80 seconds)

I record this myself, in my own voice, over a screen recording. Until I do, the AI-narrated version is in `docs/video/demo-ai-voice.mp4` (narration at the end of this file). Setup and tips: `RECORDING_GUIDE.md`
in my portfolio folder. Read it twice, then talk from the bullets. `/` marks a natural pause. Aim for 140–160 words
a minute.

Before recording: open both live apps two minutes early so they're awake, browser zoom 125%. Never type the live
Admin password on screen; skip the Operations page or record it from a local run with a one-time password.

## Shot list

| Time | On screen | What I say |
|---|---|---|
| 0–10 s | This repo's README, first screen | The two assistants worked as demos. / But the hotel's IT lead asked, who gets told when it's down? / How do I switch it off? This repo is the answer. |
| 10–30 s | Live assistant: type input 1 (Spanish); the answer arrives in Spanish with a source | First, fixes the evals found. / A Spanish question used to get blocked. / Now it's answered in Spanish, from the English documents, with the source. |
| 30–45 s | Live agent: `?email=E12`, run it; the draft names Mountain Lodge | This guest wrote to the wrong hotel's inbox. / The agent used to answer for the wrong hotel. / Now it looks up the booking first, and gets it right. |
| 45–60 s | Live assistant: type input 2 (the emergency); the fixed safety message appears at once | And a follow-up I care about: what about an emergency? / It skips the model completely / and shows a fixed safety message, instantly. |
| 60–75 s | `docs/RUNBOOKS.md`, then the Health check workflow runs in GitHub Actions | Then the handoff. / Eight runbooks, outage, cost spike, a bad answer, an injection. / And a daily health check that opens an issue when an app is down. |
| 75–85 s | New tab: type the assistant URL, it loads | Both apps are live, no sign-in. / The links are in the README. |

## Exact inputs

| # | Where | Type or do exactly |
|---|---|---|
| 1 | <https://hotel-ops-assistant.streamlit.app> (Beach Resort) | `¿Se permiten perros en el hotel?` |
| 2 | Same app, same conversation | `There is smoke coming from under a door` |
| 3 | <https://guest-request-agent.streamlit.app/?email=E12> | Click **Run the agent on this email** |

Checked 2026-10-24: both live apps report "up" on the daily health check's status API. Against the v1.6.0 code
(locally, no API): input 1 passes the scope check and retrieves Beach Resort's pet policy; input 2 is flagged as an
emergency, so it never reaches the model. E12 gets the right hotel in 6/6 runs of the v1.1.0 release run. I didn't
type these on the live apps; do that once before recording.

## LinkedIn caption (one sentence)

Handing an AI system to a client isn't the demo: it's the fixes the evals found, a kill switch, redacted logs,
eight runbooks and a health check that tells "asleep" from "down".

## AI narration (used in docs/video/demo-ai-voice.mp4)

Until I record my own voice, the demo video (1:04) is narrated by an AI voice (Kokoro `af_heart`, local) and labelled "AI-narrated" on screen and here. It was recorded from the rendered documents on GitHub with Playwright; the captions are the narration, timed to the voice. `/` marks a pause.

| Step | Narration |
|---|---|
| problem | The two hotel assistants worked as demos. / But the hotel's IT lead asked: who gets told when it's down? / How do I switch it off? / This repo is my answer. Simulated client, synthetic data. |
| fixes | First, the fixes the evals found. / A Spanish question used to get blocked; / now it's answered in Spanish, with the source. / And an email sent to the wrong hotel's inbox is now answered for the right hotel. |
| runbooks | Then the handoff itself. / Eight runbooks: an outage, a cost spike, a bad answer, an injection attempt. / Each one says who does what, in what order. |
| slos | There are service levels, with an error budget, / and the quality gates come from the eval harness, / so a release that gets worse fails before it ships. |
| health | And a daily health check that opens an issue when an app is down, / and can tell asleep from broken. / The apps are live, and the links are in the README. |
