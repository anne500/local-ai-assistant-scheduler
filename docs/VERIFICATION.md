# 🧪 Project 9 verification record

This record transcribes evidence supplied from the Windows PowerShell session on November 17–19, 2026. The raw reports and runner log remain on that laptop under `outputs/`. The observations below were reviewed from the supplied console output.

<a id="local-inference"></a>

## 🧠 Local inference

The first request exceeded a 120-second PowerShell timeout. The later successful request explicitly set `think = false`, temperature `0`, a 64-token output limit, and a 180-second client timeout.

- 📄 Input: `The Cedar smoke test failed because the signing certificate expired.`
- 🧠 Output: `The Cedar smoke test failed due to an expired signing certificate.`
- ⏱️ Model loading: **9.29 seconds**.
- ⏱️ Total: **11.51 seconds**.
- 🔢 Remaining request time: **2.22 seconds**, calculated as total minus model loading.

Both facts were preserved in the observed sentence. One run establishes this example's observed result. It does not estimate general accuracy, repeatability, or the cause of the earlier timeout.

## 📝 Python worker and runner

| Observation | Recorded evidence |
| --- | --- |
| ✅ Direct worker | `cedar-ci-2026-11-17_21-51-42_341560.md`, summary and synthetic source printed |
| ✅ Normal runner | `cedar-ci-2026-11-17_21-53-45_544924.md`, runner exit code `0` |

<a id="windows-launch"></a>

## 🪟 Windows on-demand launch

The registered task was started with `Start-ScheduledTask`.

| Observation | Recorded evidence |
| --- | --- |
| 🗓️ LastRunTime | November 17, 2026 at 22:14:08 |
| 🟢 LastTaskResult | `0` |
| 📝 Fresh report | `cedar-ci-2026-11-17_22-14-18_588846.md` |
| 📋 Log entry | `2026-11-17 22:14:18,593 INFO Report saved: ...` |

This establishes successful execution through Windows Task Scheduler's on-demand entry point.

<a id="failure-and-recovery"></a>

## 🛡️ Controlled failure and recovery

A temporary `agents/aaa_failure_demo.py` defined `run()` to raise `RuntimeError("Controlled test: CI evidence is unavailable.")`. Its filename sorted before Cedar.

| Stage | Recorded evidence |
| --- | --- |
| 🔴 Failing worker | November 18 at `20:42:39,257`, `ERROR Worker failed: aaa_failure_demo.py`, followed by traceback |
| 🟢 Cedar continued | `cedar-ci-2026-11-18_20-42-50_612897.md` saved |
| 🚦 Overall failure | `Failure test exit code: 1` |
| 🧹 Cleanup | The supplied PowerShell block removed the temporary file in `finally` |
| 🟢 Normal recovery | `cedar-ci-2026-11-18_22-50-43_830419.md` saved, `Recovery exit code: 0` |

The normal run supports recovery after the controlled test. The supplied transcript did not include a separate `Test-Path` result for the removed file.

<a id="weather-worker"></a>

## 🌤️ Weather worker and two-worker execution

The weather worker was published in commit `ec5b53bcf1668ab9ccfff0a436d0fac2d4b912a4`. Its `LOCATION` is the tutorial sample, New York. It fetches wttr.in JSON, records selected source values and UTC retrieval time, then requests a local Ollama summary.

| Check | Supplied evidence |
| --- | --- |
| ✅ Two-worker discovery | Cedar and weather reports saved in the same invocation |
| ✅ Process result | Runner exit code `0` |
| 📝 Cedar report | `cedar-ci-2026-11-19_16-29-49_001337.md` |
| 🌤️ Weather report | `weather-brief-2026-11-19_16-29-58_279993.md` |
| 🕰️ Retrieval timestamp | `2026-11-20T00:29:49.894568+00:00` |
| 🔎 Source | `https://wttr.in/New%20York?format=j1` |
| ⏳ Observation timestamp | `Unavailable` |

### 📄 Reviewed output and source values

> In New York, the weather is clear with a temperature of 54°F and a feels-like temperature of 51°F.
>
> The humidity is at 55% and the wind speed is 4 mph.

| Field | Saved source | Generated summary |
| --- | --- | --- |
| 📍 Requested location | New York | New York |
| 🌤️ Description | `Clear ` | clear |
| 🌡️ Temperature | 54 F | 54°F |
| 🧥 Feels like | 51 F | 51°F |
| 💧 Humidity | 55 percent | 55% |
| 🌬️ Wind speed | 4 mph | 4 mph |

The reviewed sample matched each supplied field. This was a manual comparison with retrieved JSON. Independent weather observation accuracy was not evaluated.

### 🛠️ Prompt and display corrections

1. An earlier summary linked wind to feels-like temperature with a causal phrase. The prompt was tightened to report the supplied values independently.
2. A subsequent summary repeated both bullets. The final prompt assigns temperature and conditions to bullet 1, humidity and wind to bullet 2.
3. The final supplied sample produced distinct bullets and preserved the supplied values.
4. An earlier PowerShell read displayed `Â°F`. Reading with `Get-Content -Encoding UTF8` displayed `°F` correctly.

The worker checks empty and truncated output. Factual support and bullet separation are prompt instructions with manual sample review. The missing observation timestamp prevents a freshness claim based on retrieval time alone.

<a id="automatic-daily-run"></a>

## 🗓️ Automatic daily Cedar execution

The daily 08:00 task registration includes missed-run catch-up, `IgnoreNew` for overlapping task invocations, and battery-operation settings.

The supplied Task Scheduler status and matching runner log establish one automatic Cedar run on November 19, 2026.

| Observation | Supplied evidence |
| --- | --- |
| 🕰️ Time of status check | November 19, 2026 at 17:47:49 Windows local time |
| 🗓️ LastRunTime | November 19, 2026 at 08:00:01 |
| 🟢 LastTaskResult | `0` |
| 📝 Cedar report | `cedar-ci-2026-11-19_08-00-13_632505.md` |
| 📋 Saved-report log entry | `2026-11-19 08:00:13,663 INFO Report saved:` followed by the report path |
| ➡️ NextRunTime | November 20, 2026 at 08:00:00 |

**✅ Automatic Cedar execution is verified from the matching task status and saved-report log entry.** The report contents from this particular run were not supplied for separate factual review.

**⏳ Automatic weather execution awaits verification.** The weather worker was added in the afternoon, after the verified morning invocation. Its manual two-worker runs are recorded above. Further daily runs would establish repeated operation.

## 🔬 Evidence boundaries

- 📄 Cedar uses synthetic local CI evidence.
- 🧠 Cedar and weather source comparisons were manually reviewed. The code checks empty and truncated responses.
- 🪟 Windows execution was demonstrated. Other operating systems were not exercised in the supplied record.
- 🧪 Weather executions were run on the Windows laptop and reviewed from supplied console output. Documentation updates did not rerun the model.

## 📈 Stock and 📰 RSS news implementation checks

The new workers use the tutorial's GOOGL chart endpoint and a public Hugging Face RSS feed. RSS is an adaptation prompted by the hosted search API's credit requirement encountered earlier.

- ✅ Ten standard-library unit tests passed in the authoring environment. They cover quote arithmetic, invalid prices, provider errors, symbol mismatch, RSS ordering/deduplication/source hosts, empty feeds, retained source links, report assembly, and empty/truncated/incomplete model responses.
- ✅ Live Yahoo chart retrieval parsed successfully into quote evidence.
- ✅ Live Hugging Face RSS retrieval parsed successfully and selected up to three entries.
- ✅ Both reports assembled from live retrieval with model responses replaced by test stubs.
- ✅ Subsequent Windows execution and source review are recorded in the November 19 four-worker section below. That review identified empty news excerpts and led to the headline-only correction.

Run all workers from the project root and review the resulting stock and news reports. The news digest uses one publisher's feed excerpts. Python appends publication dates and URLs. Quote changes are computed in Python with Decimal arithmetic against chartPreviousClose. Quote timestamps are retained so the report can be interpreted in context.

<a id="four-worker-windows-run"></a>

## ✅ November 19 four-worker Windows run

The supplied Windows transcript records commit `0df7ec9`, ten offline tests passing in 0.005 seconds, and all four workers producing reports with runner exit code `0`.

| Worker | Report |
| --- | --- |
| 📰 AI news | `ai-news-2026-11-19_20-57-42_248967.md` |
| 📄 Cedar | `cedar-ci-2026-11-19_20-57-44_252282.md` |
| 📈 GOOGL | `googl-stock-2026-11-19_20-57-52_364190.md` |
| 🌤️ Weather | `weather-brief-2026-11-19_20-58-02_171429.md` |

### 📈 Stock source comparison

The supplied stock sentence stated 272.66 USD and a 3.46% decrease relative to 282.44. Saved JSON records change `-9.78`, percent change `-3.46`, direction `down`, and quote time `2026-11-19T21:00:00+00:00`.

Python arithmetic confirms `272.66 - 282.44 = -9.78` and `(-9.78 / 282.44) * 100` rounds to `-3.46` percent. The reviewed sentence matches the saved values. The source market-state field was unavailable.

### 📰 News evidence boundary and correction

All three saved news entries had empty `excerpt` values. The output restated headlines, and one sentence inferred an IBM Research attribution from the source context. Article-content support was unavailable in the supplied evidence.

The corrected worker keeps the original feed headline and emits the exact message **Headline only. The feed supplied no article excerpt.** It sets `evidence_scope` to `headline_only` and skips the model call for that entry. Entries with excerpts use `feed_excerpt`; their prompt requests attribution to the post and forbids adding authors or affiliations.

Twelve offline checks passed in the authoring environment after the correction. New checks cover zero model calls for headline-only input and the observed stock arithmetic. The subsequent Windows verification of the headline-only path is recorded below. Automatic scheduling evidence remains the earlier Cedar-only run.

<a id="headline-only-windows-run"></a>

## ✅ Headline-only correction verified on Windows

The user pulled commit `e6cb8c2` and supplied the following results from November 19, 2026.

| Check | Supplied evidence |
| --- | --- |
| 🧪 Regression checks | 12 tests passed in 0.008 seconds |
| 📰 News report | `ai-news-2026-11-19_21-07-41_009197.md` |
| 📄 Cedar report | `cedar-ci-2026-11-19_21-07-50_475437.md` |
| 📈 GOOGL report | `googl-stock-2026-11-19_21-07-58_321034.md` |
| 🌤️ Weather report | `weather-brief-2026-11-19_21-08-05_974808.md` |
| 🟢 Runner exit code | `0` |
| 🕰️ News retrieval time | `2026-11-20T05:07:41.009197+00:00` |

The supplied news report retained three feed headlines and their source URLs and publication dates. Each entry displayed **Headline only. The feed supplied no article excerpt.** All three source records contained `excerpt: ""` and `evidence_scope: "headline_only"`.

This verifies the corrected report through the normal Windows runner entry point. The regression test confirms that empty-excerpt items skip model calls. Live summary quality for nonempty feed excerpts remains unverified. The initial 08:00 automatic scheduling evidence covers Cedar; the expanded four-worker automatic run still awaits evidence.

## 🔎 CI extension prepared after the four-worker baseline

The separately invoked `extensions.github_ci` implementation was built while waiting for the expanded automatic four-worker run. Authoring verification completed 22 offline checks, including ten CI checks, and a live public retrieval in metadata-only mode.

The pinned source was Home Assistant BRI demo run `21890541227`, attempt `1`, created on February 11, 2026. It reported failure with one failed job `63195208285` and an empty steps list. The report explicitly recorded missing diagnostic logs and unavailable root cause.

The normalized snapshot was retrieved at `2026-11-20T05:15:04.982647+00:00` and is saved under [docs/evidence](evidence/github-ci-21890541227.json). SHA-256 is `78fb8db7e29557b3d910f242577bb41ec07531b8a686d3305b67d4af8cedb22f`.

The subsequent Windows CI-extension metadata and Qwen checks are recorded below. The CI extension can be verified independently of the automatic four-worker check. Wider diagnosis-quality evaluation remains future work. See the [CI extension guide](GITHUB_CI_EXTENSION.md).

<a id="windows-ci-extension"></a>

## ✅ Windows CI extension verification

Both Windows invocations used Home Assistant BRI demo run **21890541227**, attempt **1**, with workflow **Validate with hassfest**, status **completed**, and conclusion **failure**. The run creation time remained **2026-02-11T02:33:54Z**.

| Mode | Retrieval time (UTC) | Exit code | Saved evidence filename |
| --- | --- | --- | --- |
| 📄 Metadata only | 2026-11-20T05:38:07.536711+00:00 | 0 | `github-ci-21890541227-2026-11-20_05-38-07_538716-5dab80b7.json` |
| 🧠 Local Qwen summary | 2026-11-20T05:39:09.475666+00:00 | 0 | `github-ci-21890541227-2026-11-20_05-39-09_475666-a6cca59d.json` |

The user supplied both Markdown reports. Each recorded the failed job **63195208285**, an empty step list, and explicit unavailable root cause because diagnostic logs were not retrieved.

The reviewed Qwen sentence was:

> The GitHub workflow named "Validate with hassfest" for repository anne500/home-assistant-bri-demo, run ID 21890541227, completed with a failure conclusion.

The sentence matched the workflow, repository, run ID, status, and conclusion. It added no cause, repair, or release decision. This is one reviewed historical failure case.

The reports recorded these SHA-256 values for their saved JSON evidence:

- 📄 Metadata only: `d19b03b7ce4f25d799bddb719d0cffb9e5d41e6c8758875a0173e9ed9c078985`.
- 🧠 Qwen mode: `df09f0a741d51640a89c09130cfda55f2509072df517c7e21ac25951247e0e82`.

All 22 offline tests previously passed on Windows in **0.034 seconds**. Automatic execution of the expanded four-worker set remains pending verification. Broader diagnosis-quality evaluation requires additional evidence and cases.
