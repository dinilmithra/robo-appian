"""Library-owned recorder command parsing and dispatch."""
from __future__ import annotations
import argparse
from pathlib import Path
from robo_appian.recorder import Recording, record_browser, write_pytest


def configure_parser(parser: argparse.ArgumentParser) -> None:
    """Register recorder commands on a standalone or nested parser."""
    sub = parser.add_subparsers(dest="recorder_command", required=True)
    record = sub.add_parser("record", help="Open a fresh browser with a paused recorder")
    record.add_argument("--url", required=True)
    record.add_argument("--output", required=True, type=Path)
    record.add_argument("--name", default="Recorded workflow")
    record.add_argument("--channel", choices=["chrome", "msedge"])
    demo = sub.add_parser("demo", help="Record the bundled local example without application credentials")
    demo.add_argument("--output", type=Path, default=Path("recordings/demo"))
    demo.add_argument("--channel", choices=["chrome", "msedge"])
    review = sub.add_parser("review", help="Reopen a saved recording for explicit step review")
    review.add_argument("recording", type=Path)
    review.add_argument("--channel", choices=["chrome", "msedge"])
    validate = sub.add_parser("validate", help="List blockers and missing approvals")
    validate.add_argument("recording", type=Path)
    generate = sub.add_parser("generate", help="Generate pytest after all steps and expectations are approved")
    generate.add_argument("recording", type=Path)
    generate.add_argument("--output", required=True, type=Path)


def run_command(args: argparse.Namespace) -> int:
    """Execute a parsed recorder command."""
    try:
        if args.recorder_command == "record":
            path = record_browser(args.url, args.output, name=args.name, channel=args.channel)
        elif args.recorder_command == "demo":
            path = record_browser(demo_url(), args.output, name="Create execution request demo", channel=args.channel)
        elif args.recorder_command == "review":
            recording = Recording.load(args.recording)
            path = record_browser(recording.data.get("start_url") or "about:blank", args.recording.parent, recording=recording, channel=args.channel)
        elif args.recorder_command == "validate":
            problems = Recording.load(args.recording).export_issues()
            print("\n".join(problems) if problems else "Recording approved and ready to generate.")
            return 1 if problems else 0
        else:
            path = write_pytest(Recording.load(args.recording), args.output)
        print(path)
        return 0
    except (ValueError, OSError, KeyError) as exc:
        print(str(exc))
        return 2

def demo_url() -> str:
    """Return the library-bundled demonstration page URI."""
    return Path(__file__).with_name("demo.html").resolve().as_uri()


def main(argv=None, *, prog="robo-appian recorder") -> int:
    parser = argparse.ArgumentParser(prog=prog)
    configure_parser(parser)
    return run_command(parser.parse_args(argv))


if __name__ == "__main__":
    raise SystemExit(main())
