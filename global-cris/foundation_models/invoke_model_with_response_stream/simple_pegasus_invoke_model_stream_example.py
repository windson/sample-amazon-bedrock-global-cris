#!/usr/bin/env python3
"""
Simple Amazon Bedrock Global CRIS streaming example using InvokeModelWithResponseStream API
Demonstrates streaming with TwelveLabs Pegasus v1.2 and Global CRIS for video understanding

Note: TwelveLabs Pegasus is a video understanding model that requires video input.
It does not support the Converse API - only InvokeModel and InvokeModelWithResponseStream.

Video input options:
- base64String: For videos up to 25MB
- s3Location: For videos up to 2GB / 1 hour (recommended for larger files)

This script downloads a sample video, uploads it to your S3 bucket, and invokes Pegasus with streaming.

Author: Navule Pavan Kumar Rao
Date: March 3, 2026
"""

import json
import os
import tempfile
import urllib.request

import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils import ensure_bedrock_bucket_access

# Load environment variables from .env file
load_dotenv()

# Get configuration from environment or prompt user
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
AWS_REGION = os.getenv("AWS_REGION")

if not S3_BUCKET_NAME:
    S3_BUCKET_NAME = input("Enter S3 bucket name: ").strip()
    if not S3_BUCKET_NAME:
        raise ValueError("S3 bucket name is required")

if not AWS_REGION:
    AWS_REGION = input("Enter AWS region (e.g., ap-south-1): ").strip()
    if not AWS_REGION:
        raise ValueError("AWS region is required")

# Initialize AWS clients with consistent region
bedrock = boto3.client("bedrock-runtime", region_name=AWS_REGION)
s3 = boto3.client("s3", region_name=AWS_REGION)
sts = boto3.client("sts", region_name=AWS_REGION)

# Global CRIS model ID for TwelveLabs Pegasus v1.2
MODEL_ID = "global.twelvelabs.pegasus-1-2-v1:0"

# Video analysis prompt
PROMPT = "Describe what is happening in this video and identify any key objects or people."

# Sample video URL
VIDEO_URL = "https://ws-assets-prod-iad-r-pdx-f3b3f9f1a7d6a3d0.s3.us-west-2.amazonaws.com/335119c4-e170-43ad-b55c-76fa6bc33719/NetflixMeridian.mp4"
VIDEO_KEY = "pegasus-samples/NetflixMeridian.mp4"


def get_account_id() -> str:
    """Get the current AWS account ID."""
    return sts.get_caller_identity()["Account"]


def download_video(url: str) -> str:
    """Download video from URL to a temporary file.
    
    Only HTTP and HTTPS URLs are allowed for security.
    """
    # Validate URL scheme to prevent file:// and other dangerous schemes
    from urllib.parse import urlparse
    parsed = urlparse(url)
    if parsed.scheme not in ('http', 'https'):
        raise ValueError(f"Invalid URL scheme: {parsed.scheme}. Only http and https are allowed.")
    
    print("⬇️  Downloading video...")
    tmp_file = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False)
    urllib.request.urlretrieve(url, tmp_file.name)  # nosec B310 - URL scheme validated above
    file_size = os.path.getsize(tmp_file.name)
    print(f"📦 Downloaded: {file_size / (1024 * 1024):.2f} MB")
    return tmp_file.name


def upload_to_s3(local_path: str, bucket: str, key: str) -> str:
    """Upload file to S3 and return the S3 URI."""
    print(f"☁️  Uploading to s3://{bucket}/{key}...")
    s3.upload_file(local_path, bucket, key)
    print("✅ Upload complete")
    return f"s3://{bucket}/{key}"


def check_s3_exists(bucket: str, key: str) -> bool:
    """Check if object already exists in S3."""
    try:
        s3.head_object(Bucket=bucket, Key=key)
        return True
    except ClientError:
        return False


print("🌍 Amazon Bedrock Global CRIS InvokeModelWithResponseStream Demo")
print("🚀 Model: TwelveLabs Pegasus v1.2 (Global CRIS)")
print(f"📝 Prompt: {PROMPT}")
print(f"🪣 S3 Bucket: {S3_BUCKET_NAME}")
print(f"📍 AWS Region: {AWS_REGION}")

try:
    # Get AWS account ID for bucketOwner
    account_id = get_account_id()
    print(f"🔑 AWS Account: {account_id}")

    # Ensure Bedrock has access to the S3 bucket
    ensure_bedrock_bucket_access(s3, S3_BUCKET_NAME, account_id)

    # Check if video already exists in S3, if not download and upload
    if check_s3_exists(S3_BUCKET_NAME, VIDEO_KEY):
        print(f"📁 Video already exists in S3: {VIDEO_KEY}")
        s3_uri = f"s3://{S3_BUCKET_NAME}/{VIDEO_KEY}"
    else:
        # Download and upload video
        local_path = download_video(VIDEO_URL)
        try:
            s3_uri = upload_to_s3(local_path, S3_BUCKET_NAME, VIDEO_KEY)
        finally:
            os.unlink(local_path)  # Clean up temp file

    print(f"🎬 Video: {s3_uri}")
    print("\n💬 Streaming Response:")
    print("-" * 50)

    # Format the request payload for Pegasus video understanding
    native_request = {
        "inputPrompt": PROMPT,
        "mediaSource": {
            "s3Location": {
                "uri": s3_uri,
                "bucketOwner": account_id,
            }
        },
        "temperature": 0.2,
        "maxOutputTokens": 2048,
    }

    # Convert the native request to JSON
    request_body = json.dumps(native_request)

    # Invoke the model with streaming response
    print("🔄 Invoking Pegasus model with streaming...")
    streaming_response = bedrock.invoke_model_with_response_stream(
        modelId=MODEL_ID, body=request_body, contentType="application/json"
    )

    # Extract and print the response text in real-time
    complete_response = ""
    finish_reason = None
    for event in streaming_response["body"]:
        chunk = json.loads(event["chunk"]["bytes"])
        # Handle different chunk types from Pegasus streaming
        if "message" in chunk:
            text = chunk["message"]
            print(text, end="", flush=True)
            complete_response += text
        if "finishReason" in chunk:
            finish_reason = chunk["finishReason"]

    print("\n" + "-" * 50)
    print("✅ InvokeModelWithResponseStream completed successfully!")
    if finish_reason:
        print(f"🏁 Finish reason: {finish_reason}")
    print("🌐 Request automatically routed to optimal region via Global CRIS")
    print(
        "💡 TwelveLabs Pegasus v1.2 excels at video understanding and multimodal analysis"
    )
    print(f"📊 Response length: {len(complete_response)} characters")

except ClientError as e:
    error_code = e.response.get("Error", {}).get("Code", "Unknown")
    error_message = e.response.get("Error", {}).get("Message", str(e))
    print(f"❌ AWS Error ({error_code}): {error_message}")
except Exception as e:
    print(f"❌ Unexpected error: {e}")
