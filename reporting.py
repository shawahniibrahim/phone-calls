import json
import os
import re
from dataclasses import asdict
from datetime import datetime
from html import escape
from pathlib import Path
from shutil import copyfile


def _slugify(value: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_-]+", "_", value).strip("_").lower() or "flow"


def _relative_link(from_path: Path, target_path: str | Path | None) -> str | None:
    if not target_path:
        return None

    target = Path(target_path)
    if not target.is_absolute():
        target = (Path.cwd() / target).resolve()
    else:
        target = target.resolve()

    base_dir = from_path.parent.resolve()
    try:
        return os.path.relpath(target, start=base_dir)
    except ValueError:
        return None


def _render_assertion_rows(assertion_results):
    rows = []
    for assertion in assertion_results:
        status = "PASS" if assertion["passed"] else "FAIL"
        row_class = "pass" if assertion["passed"] else "fail"
        when = "current"
        if assertion.get("exchange_offset") == 1:
            when = "next"
        elif assertion.get("exchange_offset"):
            when = f"+{assertion['exchange_offset']}"
        rows.append(
            "<tr class=\"{row_class}\">"
            "<td>{status}</td>"
            "<td>{step}</td>"
            "<td>{when}</td>"
            "<td>{atype}</td>"
            "<td>{target}</td>"
            "<td>{desc}</td>"
            "<td>{expected}</td>"
            "<td>{message}</td>"
            "</tr>".format(
                row_class=row_class,
                status=status,
                step=escape(str(assertion["step"])),
                when=escape(when),
                atype=escape(str(assertion["type"])),
                target=escape(str(assertion["target"])),
                desc=escape(str(assertion["description"])),
                expected=escape(str(assertion["expected_value"])),
                message=escape(str(assertion["message"])),
            )
        )
    return "\n".join(rows)


def _render_transcript_rows(transcript):
    rows = []
    for exchange in transcript:
        rows.append(
            "<tr>"
            "<td>{step}</td>"
            "<td>{clinic}</td>"
            "<td>{ours}</td>"
            "<td>{timestamp}</td>"
            "</tr>".format(
                step=escape(str(exchange.get("step", ""))),
                clinic=escape(str(exchange.get("clinic_said", ""))),
                ours=escape(str(exchange.get("we_said", ""))),
                timestamp=escape(str(exchange.get("timestamp", ""))),
            )
        )
    return "\n".join(rows)


def _load_report_payloads(calls_dir: Path):
    payloads = []
    seen_calls = set()
    for json_file in sorted(calls_dir.glob("*.json"), reverse=True):
        if json_file.name.endswith("_conversation.json"):
            continue

        with open(json_file, "r", encoding="utf-8") as f:
            payload = json.load(f)

        if not isinstance(payload, dict):
            continue
        if not payload.get("report_html"):
            continue

        call_key = (payload.get("flow_id"), payload.get("call_sid"))
        if call_key in seen_calls:
            continue
        seen_calls.add(call_key)
        payloads.append(payload)
    return payloads


def _write_index(calls_dir: Path) -> str:
    index_path = calls_dir.parent / "index.html"
    payloads = _load_report_payloads(calls_dir)

    rows = []
    for payload in payloads:
        report_link = _relative_link(index_path, payload.get("report_html"))
        rows.append(
            "<tr>"
            "<td>{created_at}</td>"
            "<td>{flow_id}</td>"
            "<td>{call_sid}</td>"
            "<td>{status}</td>"
            "<td>{call_status}</td>"
            "<td>{assertions}</td>"
            "<td><a href=\"{link}\">Open report</a></td>"
            "</tr>".format(
                created_at=escape(str(payload.get("generated_at", ""))),
                flow_id=escape(str(payload.get("flow_id", ""))),
                call_sid=escape(str(payload.get("call_sid", ""))),
                status="PASS" if payload.get("success") else "FAIL",
                call_status=escape(str(payload.get("call_status", ""))),
                assertions=escape(
                    f"{payload.get('assertions_passed', 0)}/{payload.get('assertions_passed', 0) + payload.get('assertions_failed', 0)}"
                ),
                link=escape(report_link or "#"),
            )
        )

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>Phone Call Reports</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, sans-serif; margin: 32px; color: #1f2937; }}
    table {{ width: 100%; border-collapse: collapse; margin-top: 16px; }}
    th, td {{ border: 1px solid #d1d5db; padding: 10px; text-align: left; vertical-align: top; }}
    th {{ background: #f3f4f6; }}
    h1 {{ margin-bottom: 8px; }}
    .muted {{ color: #6b7280; }}
  </style>
</head>
<body>
  <h1>Phone Call Reports</h1>
  <p class="muted">Generated reports for recorded call runs.</p>
  <table>
    <thead>
      <tr>
        <th>Generated</th>
        <th>Flow</th>
        <th>Call SID</th>
        <th>Status</th>
        <th>Call Status</th>
        <th>Assertions</th>
        <th>Report</th>
      </tr>
    </thead>
    <tbody>
      {"".join(rows)}
    </tbody>
  </table>
</body>
</html>"""

    index_path.write_text(html, encoding="utf-8")
    return str(index_path)


def write_call_report(result, flow_config) -> tuple[str, str, str]:
    reports_dir = Path("reports")
    calls_dir = reports_dir / "calls"
    calls_dir.mkdir(parents=True, exist_ok=True)

    generated_at = datetime.now().isoformat()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    flow_id = flow_config.get("flow_id") or _slugify(result.flow_name)
    flow_slug = _slugify(flow_id)
    call_token = result.call_sid or "unknown_call"

    payload = asdict(result)
    payload.update(
        {
            "generated_at": generated_at,
            "flow_id": flow_id,
            "phone_number": flow_config.get("phone_number"),
            "timeout": flow_config.get("timeout"),
        }
    )

    json_path = calls_dir / f"{timestamp}_{flow_slug}_{call_token}.json"
    html_path = calls_dir / f"{timestamp}_{flow_slug}_{call_token}.html"
    bundled_conversation_path = None
    if result.conversation_file and Path(result.conversation_file).exists():
        bundled_conversation_path = calls_dir / f"{timestamp}_{flow_slug}_{call_token}_conversation.json"
        copyfile(result.conversation_file, bundled_conversation_path)

    payload["report_json"] = str(json_path)
    payload["report_html"] = str(html_path)
    payload["bundled_conversation_file"] = str(bundled_conversation_path) if bundled_conversation_path else None

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    conversation_link = _relative_link(html_path, bundled_conversation_path)
    transcript_link = _relative_link(html_path, result.transcript_file)
    recording_link = _relative_link(html_path, result.recording_file)
    index_link = _relative_link(html_path, reports_dir / "index.html") or "../index.html"

    status_badge = "PASS" if result.success else "FAIL"
    transcript_rows = _render_transcript_rows(result.transcript)
    assertion_rows = _render_assertion_rows(result.assertion_results)
    error_html = (
        f"<section><h2>Error</h2><pre>{escape(result.error)}</pre></section>"
        if result.error
        else ""
    )

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>Call Report - {escape(result.flow_name)}</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, sans-serif; margin: 32px; color: #111827; background: #f9fafb; }}
    h1, h2 {{ margin-bottom: 8px; }}
    .summary {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 12px; margin: 20px 0; }}
    .card {{ background: white; border: 1px solid #e5e7eb; border-radius: 12px; padding: 16px; }}
    .badge {{ display: inline-block; padding: 4px 10px; border-radius: 999px; font-weight: 600; }}
    .pass-badge {{ background: #dcfce7; color: #166534; }}
    .fail-badge {{ background: #fee2e2; color: #991b1b; }}
    table {{ width: 100%; border-collapse: collapse; background: white; border-radius: 12px; overflow: hidden; }}
    th, td {{ border: 1px solid #e5e7eb; padding: 10px; text-align: left; vertical-align: top; }}
    th {{ background: #f3f4f6; }}
    tr.pass td {{ background: #f0fdf4; }}
    tr.fail td {{ background: #fef2f2; }}
    pre {{ white-space: pre-wrap; word-break: break-word; background: white; border: 1px solid #e5e7eb; padding: 12px; border-radius: 12px; }}
    .links a {{ margin-right: 12px; }}
  </style>
</head>
<body>
  <p><a href="{escape(index_link)}">Back to report index</a></p>
  <h1>{escape(result.flow_name)}</h1>
  <p><span class="badge {'pass-badge' if result.success else 'fail-badge'}">{status_badge}</span></p>

  <div class="summary">
    <div class="card"><strong>Flow ID</strong><br />{escape(str(flow_id))}</div>
    <div class="card"><strong>Call SID</strong><br />{escape(str(result.call_sid))}</div>
    <div class="card"><strong>Call Status</strong><br />{escape(str(result.call_status))}</div>
    <div class="card"><strong>Execution Time</strong><br />{escape(f"{result.execution_time:.1f}s")}</div>
    <div class="card"><strong>Steps</strong><br />{escape(f"{result.steps_completed}/{result.total_steps}")}</div>
    <div class="card"><strong>Assertions</strong><br />{escape(f"{result.assertions_passed} passed, {result.assertions_failed} failed")}</div>
  </div>

  <section class="links">
    <h2>Artifacts</h2>
    <p>
      <a href="{escape(conversation_link or '#')}">Conversation JSON</a>
      <a href="{escape(transcript_link or '#')}">Transcript JSON</a>
      <a href="{escape(recording_link or '#')}">Recording WAV</a>
    </p>
  </section>

  {error_html}

  <section>
    <h2>Assertions</h2>
    <table>
      <thead>
        <tr>
          <th>Status</th>
          <th>Step</th>
          <th>When</th>
          <th>Type</th>
          <th>Target</th>
          <th>Description</th>
          <th>Expected</th>
          <th>Message</th>
        </tr>
      </thead>
      <tbody>
        {assertion_rows}
      </tbody>
    </table>
  </section>

  <section>
    <h2>Transcript</h2>
    <table>
      <thead>
        <tr>
          <th>Step</th>
          <th>Clinic Said</th>
          <th>We Said</th>
          <th>Timestamp</th>
        </tr>
      </thead>
      <tbody>
        {transcript_rows}
      </tbody>
    </table>
  </section>
</body>
</html>"""

    html_path.write_text(html, encoding="utf-8")

    payload["report_json"] = str(json_path)
    payload["report_html"] = str(html_path)
    payload["bundled_conversation_file"] = str(bundled_conversation_path) if bundled_conversation_path else None
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    index_path = _write_index(calls_dir)
    return str(json_path), str(html_path), index_path
