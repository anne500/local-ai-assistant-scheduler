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
- ⏳ Local Qwen execution through the new workers on Windows awaits verification. No generated stock or news summary has yet been reviewed.

Run all workers from the project root and review the resulting stock and news reports. The news digest uses one publisher's feed excerpts. Python appends publication dates and URLs. Quote changes are computed in Python with Decimal arithmetic against chartPreviousClose. Quote timestamps are retained so the report can be interpreted in context.
