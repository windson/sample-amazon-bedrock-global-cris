"""
Generates large API specification documents for compaction demos.

Compaction requires at least 50,000 input tokens to trigger.
This module produces realistic REST API specs sized to exceed
that threshold within 2-3 conversation turns.
"""


def generate_api_spec(service_name: str, num_endpoints: int = 30) -> str:
    """
    Generate a realistic REST API specification document.

    Args:
        service_name: Name of the fictional service.
        num_endpoints: Number of API endpoints to generate.
                       30 endpoints produces ~76,000 characters (~19,000 tokens).

    Returns:
        A large string containing a detailed API spec.
    """
    lines = [
        f"# {service_name} API Specification v2.0\n",
        f"## Overview\n",
        f"The {service_name} provides a comprehensive REST API for managing "
        f"enterprise resources. This document covers all endpoints, request/response "
        f"schemas, authentication, rate limiting, and error handling.\n",
        f"## Authentication\n",
        f"All requests require a Bearer token in the Authorization header.\n",
        f"```\nAuthorization: Bearer <access_token>\n```\n",
        f"## Base URL\n",
        f"```\nhttps://api.{service_name.lower().replace(' ', '-')}.example.com/v2\n```\n",
    ]

    http_methods = ["GET", "POST", "PUT", "PATCH", "DELETE"]
    resources = [
        "users", "organizations", "projects", "tasks", "comments",
        "attachments", "notifications", "webhooks", "integrations",
        "reports", "dashboards", "metrics", "alerts", "policies",
        "roles", "permissions", "audit-logs", "workflows", "templates",
        "schedules", "budgets", "invoices", "subscriptions", "tags",
        "labels", "milestones", "releases", "deployments", "environments",
        "secrets", "certificates", "domains", "endpoints", "pipelines",
    ]

    for i in range(num_endpoints):
        resource = resources[i % len(resources)]
        method = http_methods[i % len(http_methods)]
        endpoint_num = i + 1

        lines.append(f"\n## {endpoint_num}. {method} /api/v2/{resource}\n")
        lines.append(f"### Description\n")
        lines.append(
            f"{'Retrieves' if method == 'GET' else 'Creates' if method == 'POST' else 'Updates' if method in ('PUT', 'PATCH') else 'Deletes'} "
            f"{resource} resources with full filtering, pagination, and field selection support.\n"
        )

        lines.append(f"### Request Parameters\n")
        lines.append(f"| Parameter | Type | Required | Description |")
        lines.append(f"|-----------|------|----------|-------------|")
        lines.append(f"| id | string (UUID) | {'Yes' if method != 'POST' else 'No'} | Unique resource identifier |")
        lines.append(f"| page | integer | No | Page number for pagination (default: 1) |")
        lines.append(f"| per_page | integer | No | Items per page (default: 20, max: 100) |")
        lines.append(f"| sort_by | string | No | Field to sort by (created_at, updated_at, name) |")
        lines.append(f"| sort_order | string | No | Sort direction (asc, desc) |")
        lines.append(f"| filter[status] | string | No | Filter by status (active, inactive, archived) |")
        lines.append(f"| filter[created_after] | ISO 8601 | No | Filter by creation date |")
        lines.append(f"| filter[tags] | string[] | No | Filter by tags (comma-separated) |")
        lines.append(f"| fields | string[] | No | Sparse fieldset selection |")
        lines.append(f"| include | string[] | No | Related resources to include |")
        lines.append("")

        if method in ("POST", "PUT", "PATCH"):
            lines.append(f"### Request Body\n")
            lines.append(f"```json")
            lines.append(f"{{")
            lines.append(f'  "data": {{')
            lines.append(f'    "type": "{resource}",')
            lines.append(f'    "attributes": {{')
            lines.append(f'      "name": "string (required, 1-255 chars)",')
            lines.append(f'      "description": "string (optional, max 10000 chars)",')
            lines.append(f'      "status": "string (active|inactive|archived)",')
            lines.append(f'      "priority": "integer (1-5, default: 3)",')
            lines.append(f'      "metadata": {{')
            lines.append(f'        "custom_field_1": "string",')
            lines.append(f'        "custom_field_2": "integer",')
            lines.append(f'        "nested_object": {{')
            lines.append(f'          "key": "value",')
            lines.append(f'          "array_field": ["item1", "item2"]')
            lines.append(f"        }}")
            lines.append(f"      }},")
            lines.append(f'      "tags": ["tag1", "tag2"],')
            lines.append(f'      "assigned_to": "uuid (user reference)",')
            lines.append(f'      "due_date": "ISO 8601 datetime",')
            lines.append(f'      "configuration": {{')
            lines.append(f'        "retry_policy": {{')
            lines.append(f'          "max_retries": 3,')
            lines.append(f'          "backoff_multiplier": 2.0,')
            lines.append(f'          "initial_delay_ms": 1000')
            lines.append(f"        }},")
            lines.append(f'        "timeout_seconds": 30,')
            lines.append(f'        "cache_ttl_seconds": 3600')
            lines.append(f"      }}")
            lines.append(f"    }},")
            lines.append(f'    "relationships": {{')
            lines.append(f'      "organization": {{ "data": {{ "type": "organizations", "id": "uuid" }} }},')
            lines.append(f'      "project": {{ "data": {{ "type": "projects", "id": "uuid" }} }}')
            lines.append(f"    }}")
            lines.append(f"  }}")
            lines.append(f"}}")
            lines.append(f"```\n")

        lines.append(f"### Response (200 OK)\n")
        lines.append(f"```json")
        lines.append(f"{{")
        lines.append(f'  "data": {{')
        lines.append(f'    "id": "550e8400-e29b-41d4-a716-44665544{endpoint_num:04d}",')
        lines.append(f'    "type": "{resource}",')
        lines.append(f'    "attributes": {{')
        lines.append(f'      "name": "Example {resource.replace("-", " ").title()} {endpoint_num}",')
        lines.append(f'      "status": "active",')
        lines.append(f'      "created_at": "2026-04-20T10:30:00Z",')
        lines.append(f'      "updated_at": "2026-04-20T10:30:00Z"')
        lines.append(f"    }}")
        lines.append(f"  }},")
        lines.append(f'  "meta": {{')
        lines.append(f'    "request_id": "req_abc123{endpoint_num:04d}",')
        lines.append(f'    "processing_time_ms": {10 + endpoint_num * 2}')
        lines.append(f"  }}")
        lines.append(f"}}")
        lines.append(f"```\n")

        lines.append(f"### Error Responses\n")
        lines.append(f"| Status | Code | Description |")
        lines.append(f"|--------|------|-------------|")
        lines.append(f"| 400 | INVALID_REQUEST | Request validation failed |")
        lines.append(f"| 401 | UNAUTHORIZED | Missing or invalid authentication |")
        lines.append(f"| 403 | FORBIDDEN | Insufficient permissions |")
        lines.append(f"| 404 | NOT_FOUND | Resource not found |")
        lines.append(f"| 409 | CONFLICT | Resource conflict (duplicate) |")
        lines.append(f"| 422 | UNPROCESSABLE | Semantic validation error |")
        lines.append(f"| 429 | RATE_LIMITED | Too many requests |")
        lines.append(f"| 500 | INTERNAL_ERROR | Server error |")
        lines.append("")

        lines.append(f"### Rate Limits\n")
        lines.append(f"- Standard tier: 100 requests/minute")
        lines.append(f"- Professional tier: 1,000 requests/minute")
        lines.append(f"- Enterprise tier: 10,000 requests/minute\n")

    return "\n".join(lines)
