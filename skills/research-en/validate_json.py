#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JSON Field Validation Script
Validates whether JSON files completely cover all fields defined in fields.yaml
"""

import json
import yaml
import sys
from pathlib import Path
from typing import Dict, Set, Tuple

# Category mapping (English keys only)
CATEGORY_MAPPING = {
    "basic_info": ["basic_info", "Basic Info"],
    "technical_features": ["technical_features", "technical_characteristics", "Technical Features"],
    "performance_metrics": ["performance_metrics", "performance", "Performance Metrics"],
    "milestone_significance": ["milestone_significance", "milestones", "Milestone Significance"],
    "business_info": ["business_info", "commercial_info", "Business Info"],
    "competition_ecosystem": ["competition_ecosystem", "competition", "Competition Ecosystem"],
    "history": ["history", "History"],
    "market_positioning": ["market_positioning", "market", "Market Positioning"],
}


def load_fields_yaml(fields_path: Path) -> Tuple[Set[str], Set[str], Dict[str, str]]:
    """
    Load fields.yaml and return:
    - all_fields: set of all field names
    - required_fields: set of field names where required=true
    - field_categories: mapping from field name to category
    """
    with open(fields_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)

    all_fields = set()
    required_fields = set()
    field_categories = {}

    for category_info in data.get("field_categories", []):
        category_name = category_info["category"]
        for field in category_info.get("fields", []):
            field_name = field["name"]
            all_fields.add(field_name)
            field_categories[field_name] = category_name
            if field.get("required", False):
                required_fields.add(field_name)

    return all_fields, required_fields, field_categories


def extract_json_fields(data: Dict, category_mapping: Dict = None) -> Set[str]:
    """
    Extract all field names from JSON (supports both flat and nested structures)
    Only extracts field names at category level, not nested dict/list values
    """
    if category_mapping is None:
        category_mapping = CATEGORY_MAPPING

    # Get all possible nested keys (category containers)
    nested_keys = set()
    for keys in category_mapping.values():
        nested_keys.update(keys)

    fields = set()

    def collect_fields(d, is_category_level: bool = True):
        """
        Collect fields from dict or list structures
        is_category_level: True if we're at top level or inside a category container
        """
        if isinstance(d, dict):
            for k, v in d.items():
                # Skip internal fields
                if k in {"_source_file", "uncertain"}:
                    continue
                # If it's a category container key, recurse into it
                if is_category_level and k in nested_keys:
                    if isinstance(v, dict):
                        collect_fields(v, is_category_level=True)
                else:
                    # This is a field name, add it
                    fields.add(k)
                    # Don't recurse into field values (avoid counting nested keys as fields)
        elif isinstance(d, list):
            # Handle list-of-dict structures at category level
            for item in d:
                if isinstance(item, dict):
                    collect_fields(item, is_category_level=is_category_level)

    collect_fields(data)
    return fields


def validate_json(json_path: Path, all_fields: Set[str], required_fields: Set[str],
                  field_categories: Dict[str, str]) -> Dict:
    """
    Validate a single JSON file
    Returns validation result dictionary
    """
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    json_fields = extract_json_fields(data)

    # Calculate coverage
    covered = all_fields & json_fields
    missing = all_fields - json_fields
    extra = json_fields - all_fields

    # Categorize missing fields
    missing_required = missing & required_fields
    missing_optional = missing - required_fields

    # Group missing fields by category
    missing_by_category = {}
    for field in missing:
        cat = field_categories.get(field, "Unknown")
        if cat not in missing_by_category:
            missing_by_category[cat] = []
        missing_by_category[cat].append(field)

    # Sort lists within categories for deterministic output
    for cat in missing_by_category:
        missing_by_category[cat].sort()

    return {
        "file": json_path.name,
        "total_defined": len(all_fields),
        "covered": len(covered),
        "missing": len(missing),
        "extra": len(extra),
        "coverage_rate": len(covered) / len(all_fields) * 100 if all_fields else 100,
        "missing_required": sorted(missing_required),
        "missing_optional": sorted(missing_optional),
        "missing_by_category": missing_by_category,
        "extra_fields": sorted(extra),
        "valid": len(missing_required) == 0,  # Valid if all required fields are covered
    }


def print_result(result: Dict, verbose: bool = True):
    """Print validation result"""
    status = "PASS" if result["valid"] else "FAIL"
    print(f"\n{'='*60}")
    print(f"[{status}] {result['file']}")
    print(f"{'='*60}")
    print(f"Coverage: {result['coverage_rate']:.1f}% ({result['covered']}/{result['total_defined']})")

    if result["missing_required"]:
        print(f"\n[ERROR] Missing required fields ({len(result['missing_required'])}):")
        for field in result["missing_required"]:
            print(f"  - {field}")

    if verbose and result["missing_optional"]:
        print(f"\n[WARN] Missing optional fields ({len(result['missing_optional'])}):")
        for cat in sorted(result["missing_by_category"].keys()):
            fields = result["missing_by_category"][cat]
            optional_fields = [f for f in fields if f not in result["missing_required"]]
            if optional_fields:
                print(f"  [{cat}]: {', '.join(optional_fields)}")

    if verbose and result["extra_fields"]:
        print(f"\n[INFO] Extra fields ({len(result['extra_fields'])}):")
        print(f"  {', '.join(result['extra_fields'][:10])}")
        if len(result["extra_fields"]) > 10:
            print(f"  ... and {len(result['extra_fields']) - 10} more")


def main():
    """Main function"""
    import argparse
    parser = argparse.ArgumentParser(description="Validate whether JSON files cover all fields defined in fields.yaml")
    parser.add_argument("--fields", "-f", type=str, help="Path to fields.yaml", default="fields.yaml")
    parser.add_argument("--json", "-j", type=str, nargs="*", help="JSON file paths to validate")
    parser.add_argument("--dir", "-d", type=str, help="Directory containing JSON files", default="results")
    parser.add_argument("--quiet", "-q", action="store_true", help="Show summary only")
    args = parser.parse_args()

    # Locate fields.yaml
    fields_path = Path(args.fields)
    if not fields_path.exists():
        # Try to find in current and parent directory
        for p in [Path.cwd() / "fields.yaml", Path.cwd().parent / "fields.yaml"]:
            if p.exists():
                fields_path = p
                break

    if not fields_path.exists():
        print(f"[ERROR] fields.yaml not found: {fields_path}")
        sys.exit(1)

    print(f"Field definition file: {fields_path}")
    all_fields, required_fields, field_categories = load_fields_yaml(fields_path)
    print(f"Total fields: {len(all_fields)} (required: {len(required_fields)}, optional: {len(all_fields) - len(required_fields)})")

    # Collect JSON files
    json_files = []
    if args.json:
        json_files = [Path(p) for p in args.json]
    else:
        json_dir = Path(args.dir)
        if json_dir.exists():
            json_files = sorted(json_dir.glob("*.json"))

    if not json_files:
        print(f"[WARN] No JSON files found")
        sys.exit(0)

    # Validate each file
    results = []
    for json_path in json_files:
        if not json_path.exists():
            print(f"[WARN] File not found: {json_path}")
            continue
        result = validate_json(json_path, all_fields, required_fields, field_categories)
        results.append(result)
        print_result(result, verbose=not args.quiet)

    # Summary
    print(f"\n{'='*60}")
    print("Summary")
    print(f"{'='*60}")
    passed = sum(1 for r in results if r["valid"])
    avg_coverage = sum(r["coverage_rate"] for r in results) / len(results) if results else 0
    print(f"Validation passed: {passed}/{len(results)}")
    print(f"Average coverage: {avg_coverage:.1f}%")

    if passed < len(results):
        sys.exit(1)


if __name__ == "__main__":
    main()
