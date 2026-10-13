"""
Command-Line Interface for FusionMind: RNA-Seq & NGS Oncogenic Gene Fusion Actionability Classifier.
"""
import argparse
import csv
import json
import ntpath
import sys
from pathlib import Path
from .models import ClinicalCasePayload
from .agents import FusionCoordinator

coordinator = FusionCoordinator()


def _validate_safe_path(path_str: str, must_exist: bool = False) -> Path:
    """Validate a file path for safety: reject traversal and ensure it stays within CWD."""
    if ntpath.isabs(path_str) or Path(path_str).is_absolute():
        raise argparse.ArgumentTypeError("Batch paths must be relative to the current directory.")
    try:
        path = Path(path_str).resolve()
    except (OSError, ValueError) as e:
        raise argparse.ArgumentTypeError(f"Invalid path '{path_str}': {e}")
    cwd = Path.cwd().resolve()
    if not path.is_relative_to(cwd):
        raise argparse.ArgumentTypeError(
            f"Path '{path_str}' is outside the working directory. "
            "Batch operations are restricted to the current directory for security."
        )
    if must_exist and not path.is_file():
        raise argparse.ArgumentTypeError(f"Input file '{path_str}' does not exist.")
    return path


def _parse_csv_bool(value: str) -> bool:
    normalized = str(value or "").strip().lower()
    if normalized in {"true", "1", "yes", "y"}:
        return True
    if normalized in {"false", "0", "no", "n", ""}:
        return False
    raise ValueError(f"Invalid Boolean value: {value!r}")


def main(argv=None):
    parser = argparse.ArgumentParser(prog="fusion-transcript-oncology-agent", description="FusionMind: RNA-Seq & NGS Oncogenic Gene Fusion Actionability Classifier")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Audit
    p_audit = subparsers.add_parser("audit", help="Run single case clinical audit")
    p_audit.add_argument("--case-id", default="CASE-2026-001")
    p_audit.add_argument("--primary", type=float, default=26.2)
    p_audit.add_argument("--secondary", type=float, default=12.5)
    p_audit.add_argument("--stat", action="store_true")
    p_audit.add_argument("--status", default="DISCORDANT")

    # Chat
    p_chat = subparsers.add_parser("chat", help="System configuration query")
    p_chat.add_argument("query", nargs="+")

    # Batch
    p_batch = subparsers.add_parser("batch", help="Batch process CSV records")
    p_batch.add_argument("-i", "--input", required=True)
    p_batch.add_argument("-o", "--output", default="results.csv")

    # Serve
    p_serve = subparsers.add_parser("serve", help="Launch FastAPI REST server")
    p_serve.add_argument("--host", default="127.0.0.1")
    p_serve.add_argument("--port", type=int, default=8000)

    args = parser.parse_args(argv)

    if args.command == "audit":
        case = ClinicalCasePayload(
            case_id=args.case_id,
            patient_synthetic_id="SYNTH-PT-881",
            primary_metric=args.primary,
            secondary_metric=args.secondary,
            status_flag=args.status,
            is_stat=args.stat,
        )
        dossier = coordinator.process_case(case)
        print("=" * 80)
        print(f"  FUSIONMIND: RNA-SEQ & NGS ONCOGENIC GENE FUSION ACTIONABILITY CLASSIFIER")
        print(f"  Domain: Genomics | Standard: ESMO ESCAT Scale & ACMG / AMP 2015")
        print(f"  Case: {dossier['case_id']} | Status: [{dossier['overall_status']}] | Total Alerts: {dossier['total_alerts']}")
        print("=" * 80)
        for a in dossier["alerts"]:
            print(f"\n  [{a['urgency']}] from {a['sub_agent']}:")
            print(f"  Title: {a['title']}")
            print(f"  Finding: {a['clinical_finding']}")
            print(f"  Action: {a['actionable_recommendation']}")
        print("\n" + "=" * 80)
        return 0

    if args.command == "chat":
        ans = coordinator.query_supervisory_chat(" ".join(args.query))
        print(f"\n[FusionCoordinator]:\n{ans}\n")
        return 0

    if args.command == "batch":
        input_path = _validate_safe_path(args.input, must_exist=True)
        output_path = _validate_safe_path(args.output, must_exist=False)
        try:
            with open(input_path, mode="r", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                fieldnames = list(reader.fieldnames or [])
                rows = list(reader)
        except (csv.Error, OSError) as e:
            print(f"Error reading input file '{args.input}': {e}", file=sys.stderr)
            return 1

        if "metric_primary" not in fieldnames and "primary_metric" not in fieldnames:
            print("CSV requires metric_primary or primary_metric.", file=sys.stderr)
            return 1
        if input_path == output_path:
            print("Input and output paths must differ.", file=sys.stderr)
            return 1
        out_fields = list(dict.fromkeys(fieldnames + ["overall_status", "total_alerts", "stat_critical_alerts", "consensus_summary"]))
        out_rows = []
        for index, r in enumerate(rows, start=2):
            try:
                case = ClinicalCasePayload(
                    case_id=r.get("case_id") or f"CASE-{index}",
                    patient_synthetic_id=r.get("patient_synthetic_id") or "SYNTH-01",
                    primary_metric=float(r.get("metric_primary") or r.get("primary_metric")),
                    secondary_metric=float(r.get("metric_secondary") or r.get("secondary_metric") or 0),
                    status_flag=r.get("status_flag") or r.get("status_text") or "NORMAL",
                    is_stat=_parse_csv_bool(r.get("is_stat") or r.get("critical_flag") or ""),
                )
                dossier = coordinator.process_case(case)
            except (ValueError, TypeError) as exc:
                print(f"Invalid data on CSV line {index}: {exc}", file=sys.stderr)
                return 1
            row_dict = dict(r)
            row_dict["overall_status"] = dossier["overall_status"]
            row_dict["total_alerts"] = dossier["total_alerts"]
            row_dict["stat_critical_alerts"] = dossier["stat_critical_alerts"]
            row_dict["consensus_summary"] = dossier["consensus_summary"]
            out_rows.append(row_dict)

        try:
            with open(output_path, mode="w", encoding="utf-8", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=out_fields)
                writer.writeheader()
                writer.writerows(out_rows)
        except OSError as e:
            print(f"Error writing output file '{args.output}': {e}", file=sys.stderr)
            return 1
        print(f"Batch processed {len(out_rows)} records -> {args.output}")
        return 0

    if args.command == "serve":
        try:
            import uvicorn
            from .server import create_app
            app = create_app()
            if app:
                print(f"Starting FusionMind: RNA-Seq & NGS Oncogenic Gene Fusion Actionability Classifier on http://{args.host}:{args.port}")
                uvicorn.run(app, host=args.host, port=args.port)
        except ImportError:
            print("FastAPI / uvicorn not installed. Run 'pip install fastapi uvicorn'")
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
