#!/usr/bin/env python3
"""Knowledge store CLI: bootstrap, RAG prompts, ingest, promote."""
from __future__ import annotations

import argparse
import json
import sys

from knowledge import batch, bootstrap, build_prompt, ingest, promote, retrieval
from knowledge.paths import DRAFT_DIR
from knowledge.text_format import sync_json_to_txt, sync_txt_to_json


def _utf8() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")


def cmd_bootstrap(_: argparse.Namespace) -> int:
    stats = bootstrap.run_bootstrap()
    print(json.dumps(stats, ensure_ascii=False, indent=2))
    return 0


def cmd_index_rebuild(_: argparse.Namespace) -> int:
    stats = retrieval.rebuild_index()
    print(json.dumps(stats, ensure_ascii=False, indent=2))
    return 0


def cmd_prepare_batch(args: argparse.Namespace) -> int:
    stats = batch.prepare_batch(args.batch)
    print(json.dumps(stats, ensure_ascii=False, indent=2))
    return 0


def cmd_build_prompt(args: argparse.Namespace) -> int:
    out = build_prompt.build_prompt_for_batch(args.batch)
    print(f"prompt -> {out}")
    return 0


def cmd_ingest(args: argparse.Namespace) -> int:
    stats = ingest.ingest_batch(args.batch, from_txt=not args.json_only)
    print(json.dumps(stats, ensure_ascii=False, indent=2))
    return 0


def cmd_promote(args: argparse.Namespace) -> int:
    if args.all:
        stats = promote.promote_all_in_batch(args.batch)
    else:
        if not args.id:
            print("Provide --id or --all", file=sys.stderr)
            return 1
        stats = promote.promote_example(args.id, batch=args.batch)
    print(json.dumps(stats, ensure_ascii=False, indent=2))
    return 0


def cmd_sync(args: argparse.Namespace) -> int:
    batch_id = f"batch-{int(args.batch):03d}" if args.batch.isdigit() else args.batch
    draft_json = DRAFT_DIR / f"{batch_id}.json"
    draft_txt = DRAFT_DIR / f"{batch_id}.txt"
    if args.direction == "txt2json":
        sync_txt_to_json(draft_txt, draft_json)
        print(f"synced {draft_txt} -> {draft_json}")
    else:
        sync_json_to_txt(draft_json, draft_txt)
        print(f"synced {draft_json} -> {draft_txt}")
    return 0


def cmd_rules_approve(args: argparse.Namespace) -> int:
    stats = promote.approve_rule(args.rule_id)
    print(json.dumps(stats, ensure_ascii=False, indent=2))
    return 0


def main(argv: list[str] | None = None) -> int:
    _utf8()
    parser = argparse.ArgumentParser(description="Quizlet knowledge store")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("bootstrap", help="Import repo data into knowledge/")
    p.set_defaults(func=cmd_bootstrap)

    p = sub.add_parser("index", help="Rebuild embedding index")
    p_rebuild = p.add_subparsers(dest="index_cmd", required=True)
    pr = p_rebuild.add_parser("rebuild")
    pr.set_defaults(func=cmd_index_rebuild)

    p = sub.add_parser("prepare-batch", help="Prepare batch draft from queue")
    p.add_argument("--batch", default="001")
    p.set_defaults(func=cmd_prepare_batch)

    p = sub.add_parser("build-prompt", help="Build RAG prompt for Cursor")
    p.add_argument("--batch", default="001")
    p.set_defaults(func=cmd_build_prompt)

    p = sub.add_parser("ingest", help="Save corrections from draft vs snapshot")
    p.add_argument("--batch", default="001")
    p.add_argument("--json-only", action="store_true", help="Read draft .json only, not .txt")
    p.set_defaults(func=cmd_ingest)

    p = sub.add_parser("promote", help="Promote example(s) to golden")
    p.add_argument("--id", help="Example slug id")
    p.add_argument("--batch", default="001")
    p.add_argument("--all", action="store_true", help="Promote all in batch draft")
    p.set_defaults(func=cmd_promote)

    p = sub.add_parser("sync", help="Sync draft .txt <-> .json")
    p.add_argument("--batch", default="001")
    p.add_argument("--direction", choices=["txt2json", "json2txt"], default="txt2json")
    p.set_defaults(func=cmd_sync)

    p = sub.add_parser("rules", help="Manage rules")
    p_rules = p.add_subparsers(dest="rules_cmd", required=True)
    pa = p_rules.add_parser("approve")
    pa.add_argument("rule_id")
    pa.set_defaults(func=cmd_rules_approve)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
