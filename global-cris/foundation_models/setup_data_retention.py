#!/usr/bin/env python3
"""
Amazon Bedrock Data Retention Setup for Claude Fable 5 / Mythos 5

Claude Fable 5 and future Mythos-class models require data retention opt-in
(provider_data_share) before you can invoke them. This script configures the
data retention setting across one or more AWS Regions.

Anthropic requires 30-day inputs and outputs retention with human review for
Mythos-class models. Once opted in, inference data leaves AWS's data and
security boundary and is shared with Anthropic.

Usage:
    python setup_data_retention.py                  # Interactive (prompts for confirmation)
    python setup_data_retention.py --yes            # Non-interactive (auto-confirm)
    python setup_data_retention.py --region us-east-1 --yes   # Single region, auto-confirm

References:
- Data Retention API: https://docs.aws.amazon.com/bedrock/latest/userguide/abuse-detection.html
- Claude Fable 5 model card: https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-anthropic-claude-fable-5.html
- Blog: https://aws.amazon.com/blogs/aws/anthropic-claude-fable-5-on-aws-mythos-class-capabilities-with-built-in-safeguards-now-available/

Author: Navule Pavan Kumar Rao
Date: July 1, 2026
"""

import argparse
import json
import sys

import boto3
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest
from botocore.exceptions import BotoCoreError, ClientError
from botocore.httpsession import URLLib3Session

# Data retention is exposed as a REST route on the Bedrock control plane
# (GET/PUT /data-retention). It is not a modeled boto3 client operation, so we
# sign the raw request with SigV4 using the standard AWS credential chain.
# See: https://docs.aws.amazon.com/bedrock/latest/userguide/data-retention.html
_SIGNING_SERVICE = "bedrock"

# Default regions to configure data retention for Global CRIS usage
DEFAULT_REGIONS = [
    "us-east-1",
    "us-east-2",
    "us-west-2",
    "eu-north-1",
    "eu-west-1",
    "ap-south-1",
    "ap-northeast-1",
]


def _data_retention_request(method: str, region: str, body: dict | None = None):
    """Send a SigV4-signed request to the Bedrock control plane data-retention route."""
    session = boto3.Session()
    credentials = session.get_credentials()
    if credentials is None:
        raise RuntimeError(
            "No AWS credentials found. Configure credentials via environment, "
            "shared config, or an IAM role before running this script."
        )

    url = f"https://bedrock.{region}.amazonaws.com/data-retention"
    data = json.dumps(body) if body is not None else None
    headers = {"Content-Type": "application/json"} if body is not None else {}

    request = AWSRequest(method=method, url=url, data=data, headers=headers)
    SigV4Auth(credentials, _SIGNING_SERVICE, region).add_auth(request)

    http = URLLib3Session()
    return http.send(request.prepare())


def get_current_retention(region: str) -> dict:
    """Get current data retention setting for a region."""
    try:
        response = _data_retention_request("GET", region)
        if response.status_code == 200:
            payload = json.loads(response.text)
            return {
                "mode": payload.get("mode", "unknown"),
                "updatedAt": payload.get("updated_at"),
            }
        return {
            "mode": "error",
            "error": f"HTTP {response.status_code}: {response.text.strip()}",
        }
    except (ClientError, BotoCoreError, RuntimeError, ValueError) as e:
        return {"mode": "error", "error": str(e)}


def set_data_retention(region: str, mode: str = "provider_data_share") -> dict:
    """Set data retention mode for a region."""
    try:
        response = _data_retention_request("PUT", region, body={"mode": mode})
        if response.status_code in (200, 201):
            payload = json.loads(response.text)
            return {
                "success": True,
                "mode": payload.get("mode"),
                "updatedAt": payload.get("updated_at"),
            }
        return {
            "success": False,
            "error": f"HTTP {response.status_code}: {response.text.strip()}",
        }
    except (ClientError, BotoCoreError, RuntimeError, ValueError) as e:
        return {"success": False, "error": str(e)}


def main():
    parser = argparse.ArgumentParser(
        description="Configure Amazon Bedrock data retention for Claude Fable 5 / Mythos 5"
    )
    parser.add_argument(
        "--yes", "-y",
        action="store_true",
        default=True,
        help="Skip confirmation prompt (default: auto-confirm)"
    )
    parser.add_argument(
        "--no-confirm",
        action="store_true",
        help="Require explicit confirmation before setting"
    )
    parser.add_argument(
        "--region", "-r",
        type=str,
        default=None,
        help="Single region to configure (default: all common regions)"
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="Only show current data retention settings (no changes)"
    )
    args = parser.parse_args()

    # Determine regions to process
    regions = [args.region] if args.region else DEFAULT_REGIONS

    print("=" * 60)
    print("Amazon Bedrock Data Retention Configuration")
    print("=" * 60)
    print()
    print("Claude Fable 5 / Mythos 5 require data retention opt-in.")
    print("Mode: provider_data_share")
    print("  - Anthropic retains inputs/outputs for 30 days")
    print("  - Human review is enabled")
    print("  - Data leaves AWS data boundary")
    print()
    print(f"Regions to configure: {', '.join(regions)}")
    print()

    # Show current settings
    print("Current settings:")
    print("-" * 40)
    for region in regions:
        current = get_current_retention(region)
        status = current.get("mode", "unknown")
        icon = "✅" if status == "provider_data_share" else "⚠️"
        print(f"  {icon} {region}: {status}")
    print()

    if args.list:
        return

    # Check if confirmation needed
    if args.no_confirm:
        print("⚠️  This will enable provider data sharing for Bedrock inference.")
        print("   Your inference data will be shared with Anthropic for 30 days.")
        response = input("\nProceed? [y/N]: ").strip().lower()
        if response not in ("y", "yes"):
            print("Aborted.")
            sys.exit(0)

    # Apply data retention settings
    print("Applying data retention settings...")
    print("-" * 40)
    success_count = 0
    for region in regions:
        result = set_data_retention(region)
        if result["success"]:
            print(f"  ✅ {region}: provider_data_share (updated: {result.get('updatedAt') or 'now'})")
            success_count += 1
        else:
            print(f"  ❌ {region}: FAILED — {result['error']}")

    print()
    print(f"Done! {success_count}/{len(regions)} regions configured successfully.")
    print()
    print("You can now invoke Claude Fable 5 and Mythos 5 models.")
    print("Example:")
    print("  python global-cris/foundation_models/invoke_model/simple_claude_fable_5_invoke_model_example.py")


if __name__ == "__main__":
    main()
