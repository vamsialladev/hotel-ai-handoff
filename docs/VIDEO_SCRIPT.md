# Video script: Production and handoff (about 80 seconds)

I record this myself, in my own voice, over a screen recording. No AI voice. Setup and tips: `RECORDING_GUIDE.md`
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

Tested 2026-10-24: both live apps answered (Streamlit status: up). Inputs 1 and 2 match the stage 4 held-out cases
that pass in the v1.6.0 release run (Spanish answer, emergency without a model call); E12 passes 6/6 in the v1.1.0
release run. Check all three once on the live apps before recording.

## LinkedIn caption (one sentence)

Handing an AI system to a client isn't the demo: it's the fixes the evals found, a kill switch, redacted logs,
eight runbooks and a health check that tells "asleep" from "down".
