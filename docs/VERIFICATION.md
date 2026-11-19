# 🧪 Project 9 verification record

This record transcribes evidence supplied from the Windows PowerShell session on November 17 and 18, 2026. The raw reports and runner log remain on that laptop under `outputs/`. The observations below were reviewed from the supplied console output.

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

## 🗓️ Daily trigger

The daily 08:00 registration was supplied with missed-run catch-up, `IgnoreNew` for overlapping task invocations, and battery-operation settings. The last reported `NextRunTime` was **November 19, 2026 at 08:00 Windows local time**.

**⏳ Automatic daily execution remains unverified.** Inspect a subsequent automatic run's `LastRunTime`, result code, and fresh report together before marking it verified.

## 🔬 Evidence boundaries

- 📄 Cedar uses synthetic local CI evidence.
- 🧠 Factual preservation in the example was manually reviewed. The code checks empty and truncated responses.
- 🪟 Windows execution was demonstrated. Other operating systems were not exercised in the supplied record.
- 🧪 No additional runtime or model tests were performed as part of the visual documentation update.
