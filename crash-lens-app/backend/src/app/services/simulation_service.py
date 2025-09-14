import random
import uuid
import os
from datetime import datetime, timezone
from typing import Dict, Any, List, Tuple, Optional

from fastapi import BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import text

from src.app.core import error_analyzer_agent_executor
from ..schema.simulation import (
    SimulateCrashRequest,
    SimulateCrashResponse,
    ErrorDetails,
)
from .slack_service import SlackService
from .s3_service import S3Service
from .websocket_service import websocket_manager
from ..utils.datetime_utils import get_utc_now_naive


class SimulationService:
    """Service for crash simulation and log generation"""

    def __init__(self, db_session: Session):
        self.db = db_session
        self.slack_service = SlackService()
        self.s3_service = S3Service()

    def _trigger_agent(self, crash_content):
        error_analyzer_agent_executor.invoke({"messages": [{"role": "user", "content": crash_content}]})
        print("Agent completed the task")

    def simulate_crash(
            self, request: SimulateCrashRequest,
            background_tasks: BackgroundTasks,
    ) -> SimulateCrashResponse:
        """Simulate a crash scenario and create database entries"""

        # Generate crash ID
        crash_id = str(uuid.uuid4())

        # Run the simulation scenario
        logs, traceback_text = self._run_scenario(
            request.scenario.value,
            request.format.value,
            request.min_logs,
            not request.no_jitter,
        )

        # Analyze error details
        error_details = self._analyze_error_from_traceback(
            traceback_text, request.scenario.value
        )

        # Generate users impacted if not provided
        users_impacted = request.users_impacted or random.randint(50, 5000)

        # Create database entry
        database_success = self._create_crash_entry(
            crash_id=crash_id,
            request=request,
            error_details=error_details,
            users_impacted=users_impacted,
        )

        # Generate sample link
        sample_link = f"https://monitoring.example.com/errors/{request.scenario.value}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Upload logs to S3 and get URL
        s3_url, s3_key, s3_success = self.s3_service.upload_logs_to_s3(
            scenario=request.scenario.value,
            logs=logs,
            crash_id=crash_id
        )

        # Store S3 URL in database instead of log content
        error_log_updated = self._update_crash_error_log(crash_id, s3_url)

        background_tasks.add_task(self._trigger_agent, f"{traceback_text}\n crash id: {crash_id}\n repository id: {request.repository_id}\n repository url: {request.repository_url}")

        # Send Slack notification with real S3 URL
        slack_notification_sent = self.slack_service.send_crash_notification(
            error_details=error_details,
            s3_url=s3_url,
            s3_key=s3_key,
            users_impacted=users_impacted,
            sample_link=sample_link,
            crash_id=crash_id,
        )

        # Send WebSocket notification to connected clients
        background_tasks.add_task(
            self._send_websocket_notification,
            crash_id=crash_id,
            error_details=error_details,
            users_impacted=users_impacted,
            repository_id=request.repository_id
        )

        return SimulateCrashResponse(
            success=True,
            crash_id=crash_id,
            scenario=request.scenario.value,
            error_details=ErrorDetails(**error_details),
            users_impacted=users_impacted,
            logs_generated=len(logs),
            sample_link=sample_link,
            slack_notification_sent=slack_notification_sent,
            database_entry_created=database_success,
            message=f"Crash simulation '{request.scenario.value}' completed successfully. Error log uploaded to S3: {s3_success}, URL stored in database: {error_log_updated}",
        )

    def _run_scenario(
            self, scenario: str, fmt: str, prelude_count: int, jitter: bool
    ) -> Tuple[List[str], str]:
        """Run the specified crash scenario and return logs and traceback"""

        # Map scenario names to their functions
        scenarios = {
            "paystack_timeout": self._scenario_paystack_timeout,
            "migration_type_mismatch": self._scenario_migration_type_mismatch,
            "taskq_oversell": self._scenario_taskq_oversell,
            "verify_payment_timeout": self._scenario_verify_payment_timeout,
            "db_startup_failure": self._scenario_db_startup_failure,
            "stripe_signature_error": self._scenario_stripe_signature_error,
        }

        if scenario not in scenarios:
            raise ValueError(f"Unknown scenario: {scenario}")

        func = scenarios[scenario]
        return func(fmt, jitter, prelude_count)

    def _analyze_error_from_traceback(
            self, traceback: str, scenario: str
    ) -> Dict[str, Any]:
        """Analyze the stack trace to extract error details"""
        error_details = {
            "title": "",
            "description": "",
            "severity": "HIGH",
            "component": "UNKNOWN",
            "error_type": "UNKNOWN",
        }

        # Extract error type from the last line of traceback
        lines = traceback.strip().split("\n")
        if lines:
            last_line = lines[-1].strip()
            if ":" in last_line:
                error_type = last_line.split(":")[0]
                error_details["error_type"] = error_type

        # Map scenarios to specific error details
        scenario_mappings = {
            "paystack_timeout": {
                "title": "Payment Gateway Timeout - Checkout Process Failed",
                "description": "Paystack payment gateway connection timed out during checkout process. Users are unable to complete purchases, resulting in lost revenue and poor customer experience.",
                "severity": "critical",
                "component": "PAYMENT_SERVICE",
            },
            "migration_type_mismatch": {
                "title": "Database Migration Type Mismatch Error",
                "description": "Database migration 160dd810dc36 introduced a type mismatch in the price field. Vendor dashboard calculations are failing due to NoneType values in price calculations.",
                "severity": "high",
                "component": "DATABASE",
            },
            "taskq_oversell": {
                "title": "Inventory Oversell Detection - Order Processing Failed",
                "description": "Task queue detected an oversell condition where requested quantity (2) exceeds available stock (1) for SKU-001. Order processing has been blocked to prevent inventory inconsistencies.",
                "severity": "high",
                "component": "INVENTORY_SERVICE",
            },
            "verify_payment_timeout": {
                "title": "Payment Verification Timeout",
                "description": "Payment verification with Paystack timed out while reading response. Order status remains uncertain, potentially causing duplicate charges or failed order confirmations.",
                "severity": "high",
                "component": "PAYMENT_SERVICE",
            },
            "db_startup_failure": {
                "title": "Database Connection Failure - Service Startup Failed",
                "description": "Application failed to start due to database connection issues after 3 retry attempts. All database-dependent services are unavailable.",
                "severity": "critical",
                "component": "DATABASE",
            },
            "stripe_signature_error": {
                "title": "Stripe Signature Verification Failed",
                "description": "Stripe webhook signature verification failed, indicating potential security issue or configuration problem. Payment processing may be compromised.",
                "severity": "high",
                "component": "PAYMENT_SERVICE",
            },
        }

        if scenario in scenario_mappings:
            error_details.update(scenario_mappings[scenario])

        return error_details

    def _create_crash_entry(
            self,
            crash_id: str,
            request: SimulateCrashRequest,
            error_details: Dict[str, Any],
            users_impacted: int,
    ) -> bool:
        """Create crash entry in database"""
        try:
            # Insert crash record with timestamps
            now = get_utc_now_naive()
            query = text("""
                         INSERT INTO crash (id, component, error_type, severity, status, impacted_users, comment,
                                            repository_id, error_log, created_at, updated_at)
                         VALUES (:id, :component, :error_type, :severity, :status, :impacted_users, :comment,
                                 :repository_id, :error_log, :created_at, :updated_at)
                         """)

            self.db.execute(
                query,
                {
                    "id": crash_id,
                    "component": error_details["component"],
                    "error_type": error_details["error_type"],
                    "severity": error_details["severity"],
                    "status": "open",
                    "impacted_users": users_impacted,
                    "comment": request.comment,
                    "repository_id": request.repository_id,
                    "error_log": None,  # Will be updated with log content
                    "created_at": now,
                    "updated_at": now,
                },
            )

            self.db.commit()

            # Create RCA record for the crash
            rca_success = self._create_crash_rca(crash_id)
            if not rca_success:
                print(f"Warning: Failed to create RCA record for crash {crash_id}")

            return True

        except Exception as e:
            print(f"Error creating crash entry: {e}")
            self.db.rollback()
            return False

    def _create_crash_rca(self, crash_id: str) -> bool:
        """Create RCA record for a crash"""
        try:
            rca_id = str(uuid.uuid4())
            now = get_utc_now_naive()

            query = text("""
                         INSERT INTO crash_rca (id, crash_id, description, problem_identification,
                                                data_collection, root_cause_identification,
                                                solution, author, supporting_documents, git_diff, pull_request_url, created_at, updated_at)
                         VALUES (:id, :crash_id, :description, :problem_identification,
                                 :data_collection, :root_cause_identification,
                                 :solution, :author, :supporting_documents, :git_diff, :pull_request_url, :created_at, :updated_at)
                         """)

            self.db.execute(
                query,
                {
                    "id": rca_id,
                    "crash_id": crash_id,
                    "description": None,
                    "problem_identification": None,
                    "data_collection": None,
                    "root_cause_identification": None,
                    "solution": None,
                    "author": None,
                    "supporting_documents": None,
                    "git_diff": None,
                    "pull_request_url": None,
                    "created_at": now,
                    "updated_at": now,
                },
            )

            self.db.commit()
            print(f"✅ Created RCA record {rca_id} for crash {crash_id}")
            return True

        except Exception as e:
            print(f"Error creating RCA record: {e}")
            self.db.rollback()
            return False

    def _update_crash_error_log(self, crash_id: str, error_log_content: str) -> bool:
        """Update crash entry with error log content"""
        try:
            now = get_utc_now_naive()
            query = text("""
                         UPDATE crash
                         SET error_log  = :error_log,
                             updated_at = :updated_at
                         WHERE id = :id
                         """)

            self.db.execute(
                query, {"id": crash_id, "error_log": error_log_content, "updated_at": now}
            )

            self.db.commit()
            print(f"✅ Updated crash {crash_id} with error log content")
            return True

        except Exception as e:
            print(f"Error updating crash entry with error log content: {e}")
            self.db.rollback()
            return False

    async def _send_websocket_notification(
        self, crash_id: str, error_details: Dict[str, Any], users_impacted: int, repository_id: str
    ):
        """Send WebSocket notification for crash - simplified without DB dependency"""
        try:
            # Use a simple repository name without DB lookup
            repository_name = f"Repository-{repository_id}" if repository_id else "Unknown Repository"

            crash_data = {
                "crash_id": crash_id,
                "title": error_details.get("title", "Crash detected"),
                "severity": error_details.get("severity", "Medium"),
                "repository_name": repository_name,
                "component": error_details.get("component", "UNKNOWN"),
                "error_type": error_details.get("error_type", "UNKNOWN"),
                "users_impacted": users_impacted
            }

            # Send notification to all connected clients
            await websocket_manager.send_crash_notification(crash_data)
            print(f"✅ Sent WebSocket notification for crash {crash_id}")

        except Exception as e:
            print(f"❌ Error sending WebSocket notification: {e}")

    def _now_iso(self) -> str:
        """Get current time in ISO format"""
        return (
            datetime.now(timezone.utc)
            .isoformat(timespec="milliseconds")
            .replace("+00:00", "Z")
        )

    def _jitter_sleep(
            self, min_ms: int = 40, max_ms: int = 140, enabled: bool = True
    ) -> None:
        """Add jitter sleep for realistic timing"""
        if not enabled:
            return
        import time

        time.sleep(random.uniform(min_ms / 1000.0, max_ms / 1000.0))

    def _scenario_paystack_timeout(
            self, fmt: str, jitter: bool, prelude_count: int
    ) -> Tuple[List[str], str]:
        """Paystack timeout scenario"""
        logs = []

        # Skip prelude logs - only generate main scenario logs
        # Main scenario logs
        self._jitter_sleep(enabled=jitter)
        log_line = "BACKEND INFO request_in method=POST path=/cart/checkout user_id=42 request_id=req_001"
        logs.append(f"{self._now_iso()} {log_line}")

        self._jitter_sleep(enabled=jitter)
        log_line = "PAYMENTS INFO initializing_paystack amount=129900 channel=CARD email=jane@example.com"
        logs.append(f"{self._now_iso()} {log_line}")

        self._jitter_sleep(enabled=jitter)
        log_line = "PAYMENTS ERROR paystack_initialize_timeout timeout_ms=2000"
        logs.append(f"{self._now_iso()} {log_line}")

        traceback_text = """
Traceback (most recent call last):
  File "/Users/hariskumargs/Documents/Personal/TiDB-Hackathon/sample-ecommerce-app/backend/api/endpoints/cart.py", line 82, in checkout
    return await cart_service.checkout(data_obj, current_user)
  File "/Users/hariskumargs/Documents/Personal/TiDB-Hackathon/sample-ecommerce-app/backend/services/cart_service.py", line 130, in checkout
    return await self.paystack.initialize_payment(
  File "/Users/hariskumargs/Documents/Personal/TiDB-Hackathon/sample-ecommerce-app/backend/core/paystack.py", line 35, in initialize_payment
    rsp = await self.client.post(
  File "/usr/local/lib/python3.11/site-packages/httpx/_client.py", line 1778, in _send_single_request
    raise httpx.ConnectTimeout("Timed out while connecting to Paystack")
httpx.ConnectTimeout: Timed out while connecting to Paystack
        """.strip()

        logs.append(traceback_text)

        self._jitter_sleep(enabled=jitter)
        log_line = "BACKEND INFO response_out status=502 path=/cart/checkout request_id=req_001"
        logs.append(f"{self._now_iso()} {log_line}")

        return logs, traceback_text

    def _scenario_migration_type_mismatch(
            self, fmt: str, jitter: bool, prelude_count: int
    ) -> Tuple[List[str], str]:
        """Migration type mismatch scenario"""
        logs = []

        # Skip prelude logs - only generate main scenario logs
        log_line = "BACKEND INFO request_in method=GET path=/order/vendor/ vendor_id=7 request_id=req_003"
        logs.append(f"{self._now_iso()} {log_line}")

        self._jitter_sleep(enabled=jitter)
        log_line = "BACKEND ERROR vendor_dashboard_failed reason=type_mismatch_in_price_field migration=160dd810dc36"
        logs.append(f"{self._now_iso()} {log_line}")

        traceback_text = """
Traceback (most recent call last):
  File "/Users/hariskumargs/Documents/Personal/TiDB-Hackathon/sample-ecommerce-app/backend/api/endpoints/order.py", line 29, in vendor_dashboard
    return await order_service.vendor_dashboard(vendor_id=current_user.role_id)
  File "/Users/hariskumargs/Documents/Personal/TiDB-Hackathon/sample-ecommerce-app/backend/services/order_service.py", line 35, in vendor_dashboard
    total_sales = sum([item.price * item.quantity for item in order_items])
  File "/Users/hariskumargs/Documents/Personal/TiDB-Hackathon/sample-ecommerce-app/backend/services/order_service.py", line 35, in <listcomp>
    total_sales = sum([item.price * item.quantity for item in order_items])
TypeError: unsupported operand type(s) for *: 'NoneType' and 'int'
        """.strip()

        logs.append(traceback_text)

        log_line = "BACKEND INFO response_out status=500 path=/order/vendor/ request_id=req_003"
        logs.append(f"{self._now_iso()} {log_line}")

        return logs, traceback_text

    def _scenario_taskq_oversell(
            self, fmt: str, jitter: bool, prelude_count: int
    ) -> Tuple[List[str], str]:
        """Task queue oversell scenario"""
        logs = []

        # Skip prelude logs - only generate main scenario logs
        log_line = "TASKQ INFO enqueue job=add_order_items order_id=123"
        logs.append(f"{self._now_iso()} {log_line}")

        self._jitter_sleep(enabled=jitter)
        log_line = "TASKQ ERROR add_order_items_failed reason=oversell_detected sku=SKU-001 stock=1 requested=2"
        logs.append(f"{self._now_iso()} {log_line}")

        traceback_text = """
Traceback (most recent call last):
  File "/Users/hariskumargs/Documents/Personal/TiDB-Hackathon/sample-ecommerce-app/backend/task_queue/tasks/cart_tasks.py", line 47, in add_order_items
    order_item = OrderItemsCreate(
  File "pydantic/main.py", line 341, in pydantic.main.BaseModel.__init__
    raise ValidationError(model='OrderItemsCreate', errors=[{'loc': ('quantity',), 'msg': 'oversell', 'type': 'value_error'}])
pydantic.error_wrappers.ValidationError: 1 validation error for OrderItemsCreate
quantity
  oversell (type=value_error)
        """.strip()

        logs.append(traceback_text)

        return logs, traceback_text

    def _scenario_verify_payment_timeout(
            self, fmt: str, jitter: bool, prelude_count: int
    ) -> Tuple[List[str], str]:
        """Payment verification timeout scenario"""
        logs = []

        # Skip prelude logs - only generate main scenario logs
        log_line = "BACKEND INFO request_in method=GET path=/cart/verify-payment/REF_ABC request_id=req_004"
        logs.append(f"{self._now_iso()} {log_line}")

        self._jitter_sleep(enabled=jitter)
        log_line = "PAYMENTS INFO verify_paystack payment_ref=REF_ABC"
        logs.append(f"{self._now_iso()} {log_line}")

        traceback_text = """
Traceback (most recent call last):
  File "/Users/hariskumargs/Documents/Personal/TiDB-Hackathon/sample-ecommerce-app/backend/services/cart_service.py", line 157, in verify_order_payment
    payment_rsp = await self.paystack.verify_payment(payment_ref=payment_ref)
  File "/Users/hariskumargs/Documents/Personal/TiDB-Hackathon/sample-ecommerce-app/backend/core/paystack.py", line 53, in verify_payment
    rsp = await self.client.get(url=f"transaction/verify/{payment_ref}")
  File "/usr/local/lib/python3.11/site-packages/httpx/_client.py", line 1734, in _send_single_request
    raise httpx.ReadTimeout("Timed out while reading from Paystack")
httpx.ReadTimeout: Timed out while reading from Paystack
        """.strip()

        logs.append(traceback_text)

        log_line = "BACKEND ERROR verify_payment_failed request_id=req_004 status=502"
        logs.append(f"{self._now_iso()} {log_line}")

        return logs, traceback_text

    def _scenario_db_startup_failure(
            self, fmt: str, jitter: bool, prelude_count: int
    ) -> Tuple[List[str], str]:
        """Database startup failure scenario"""
        logs = []

        # Skip prelude logs - only generate main scenario logs
        log_line = "BOOT INFO starting FastAPI app import=backend.main"
        logs.append(f"{self._now_iso()} {log_line}")

        self._jitter_sleep(enabled=jitter)
        log_line = "DB ERROR Database connection failed (Attempts: 3/3)"
        logs.append(f"{self._now_iso()} {log_line}")

        traceback_text = """
Traceback (most recent call last):
  File "/Users/hariskumargs/Documents/Personal/TiDB-Hackathon/sample-ecommerce-app/backend/main.py", line 7, in <module>
    from core.middleware import start_up_db
  File "/Users/hariskumargs/Documents/Personal/TiDB-Hackathon/sample-ecommerce-app/backend/core/middleware.py", line 48, in start_up_db
    raise DatabaseConnectionError
core.errors.DatabaseConnectionError
        """.strip()

        logs.append(traceback_text)

        return logs, traceback_text

    def _scenario_stripe_signature_error(
            self, fmt: str, jitter: bool, prelude_count: int
    ) -> Tuple[List[str], str]:
        """Stripe signature error scenario"""
        logs = []

        # Skip prelude logs - only generate main scenario logs
        log_line = "PAYMENTS INFO stripe_checkout_session quantity=2"
        logs.append(f"{self._now_iso()} {log_line}")

        self._jitter_sleep(enabled=jitter)
        log_line = "PAYMENTS ERROR stripe_checkout_session_failed"
        logs.append(f"{self._now_iso()} {log_line}")

        traceback_text = """
Traceback (most recent call last):
  File "/Users/hariskumargs/Documents/Personal/TiDB-Hackathon/sample-ecommerce-app/backend/core/stripe_payment.py", line 11, in create_checkout_session
    session = stripe.checkout.Session.create(
  File "/usr/local/lib/python3.11/site-packages/stripe/api_resources/abstract/createable_api_resource.py", line 18, in create
    return super(CreateableAPIResource, cls).create(**params)
  File "/usr/local/lib/python3.11/site-packages/stripe/api_resources/abstract/api_resource.py", line 668, in create
    response, api_key = requestor.request("post", url, params, headers)
  File "/usr/local/lib/python3.11/site-packages/stripe/api_requestor.py", line 201, in request
    raise error.SignatureVerificationError("Invalid signature")
stripe.error.SignatureVerificationError: Invalid signature
        """.strip()

        logs.append(traceback_text)

        return logs, traceback_text


if __name__ == "__main__":
    SimulationService()._scenario_paystack_timeout()
