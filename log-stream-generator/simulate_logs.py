import argparse
import json
import random
import sys
import time
from datetime import datetime, timezone
from typing import Dict, Any, List


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def jitter_sleep(min_ms: int = 40, max_ms: int = 140, enabled: bool = True) -> None:
    if not enabled:
        return
    time.sleep(random.uniform(min_ms / 1000.0, max_ms / 1000.0))


def emit(line: str, fmt: str, base: Dict[str, Any]) -> None:
    if fmt == "json":
        payload = {"ts": now_iso(), **base}
        # Merge parsed k=v tokens from line if present
        tokens = line.split()
        # First token is LEVEL or COMPONENT; we capture both explicitly below
        for token in tokens:
            if "=" in token:
                k, v = token.split("=", 1)
                payload[k] = v
        # Best-effort parse of level/component/message
        parts = line.split(" ", 2)
        if len(parts) >= 1:
            payload.setdefault("raw", line)
        sys.stdout.write(json.dumps(payload) + "\n")
    else:
        sys.stdout.write(f"{now_iso()} {line}\n")
    sys.stdout.flush()


def emit_block(block: str) -> None:
    sys.stderr.write(block.rstrip("\n") + "\n")
    sys.stderr.flush()


def emit_prelude(fmt: str, jitter: bool, count: int, base: Dict[str, Any]) -> None:
    session_id = base.get("session_id", "sess_abc123")
    user_id = base.get("user_id", 42)
    cart_id = base.get("cart_id", "cart_77")
    request_id_prefix = base.get("request_id_prefix", "req_pre_")
    pages = ["/", "/products", "/products/price", "/cart", "/checkout"]
    skus = ["SKU-001", "SKU-002", "SKU-003"]
    for i in range(count):
        jitter_sleep(enabled=jitter)
        page = pages[i % len(pages)]
        sku = skus[i % len(skus)]
        rid = f"{request_id_prefix}{i:03d}"
        choice = i % 12
        if choice == 0:
            emit(f"FRONTEND INFO page_load path={page} build=prod session_id={session_id}", fmt, base)
        elif choice == 1:
            emit(f"FRONTEND DEBUG api_request method=GET url=/products page={page} request_id={rid}", fmt, base)
        elif choice == 2:
            emit(f"BACKEND INFO request_in method=GET path=/products request_id={rid}", fmt, base)
        elif choice == 3:
            emit(f"DB DEBUG query=SELECT products ORDER BY price limit=20 request_id={rid}", fmt, base)
        elif choice == 4:
            emit(f"BACKEND INFO response_out status=200 path=/products request_id={rid}", fmt, base)
        elif choice == 5:
            emit(f"FRONTEND INFO click action=add_to_cart sku={sku} user_id={user_id}", fmt, base)
        elif choice == 6:
            emit(f"BACKEND INFO request_in method=POST path=/cart/add user_id={user_id} request_id={rid}", fmt, base)
        elif choice == 7:
            emit(f"DB DEBUG insert cart_id={cart_id} sku={sku} qty=1 request_id={rid}", fmt, base)
        elif choice == 8:
            emit(f"TASKQ INFO enqueue job=add_order_items candidate_order_id=NA cart_id={cart_id}", fmt, base)
        elif choice == 9:
            emit(f"ALB INFO forward_request target_group=ecom-backend listener=443 rule={page} request_id={rid}", fmt, base)
        elif choice == 10:
            emit(f"CLOUDWATCH DEBUG metrics request_latency_ms={random.randint(20,180)} path={page}", fmt, base)
        else:
            emit(f"SECURITY INFO cors_check origin=https://app.example.com result=allowed request_id={rid}", fmt, base)


def scenario_paystack_timeout(fmt: str, jitter: bool, prelude_count: int) -> int:
    base = {"component": "BACKEND", "request_id": "req_001", "user_id": 42, "session_id": "sess_abc123", "request_id_prefix": "req_pyt_"}
    emit_prelude(fmt=fmt, jitter=jitter, count=prelude_count, base=base)
    jitter_sleep(enabled=jitter)
    emit("BACKEND INFO request_in method=POST path=/cart/checkout user_id=42 request_id=req_001", fmt, base)
    base = {"component": "BACKEND", "request_id": "req_001"}
    emit("BACKEND INFO request_in method=POST path=/cart/checkout user_id=42 request_id=req_001", fmt, base)
    jitter_sleep(enabled=jitter)
    emit("BACKEND DEBUG route handler=api.endpoints.cart.checkout deps=get_cart_service,get_current_verified_customer", fmt, base)
    jitter_sleep(enabled=jitter)
    emit("BACKEND INFO service call services.cart_service.CartService.checkout customer_id=42", fmt, base)
    jitter_sleep(enabled=jitter)
    emit("DB DEBUG get_cart_summary customer_id=42 items=2 total_amount=129900", fmt, base)
    jitter_sleep(enabled=jitter)
    emit("PAYMENTS INFO initializing_paystack amount=129900 channel=CARD email=jane@example.com", fmt, base)
    jitter_sleep(enabled=jitter)
    emit("PAYMENTS ERROR paystack_initialize_timeout timeout_ms=2000", fmt, base)
    emit_block(
        """
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
    )
    jitter_sleep(enabled=jitter)
    emit("DB DEBUG rollback_tx reason=payment_timeout request_id=req_001", fmt, base)
    emit("BACKEND INFO response_out status=502 path=/cart/checkout request_id=req_001", fmt, base)
    return 1


def scenario_migration_type_mismatch(fmt: str, jitter: bool, prelude_count: int) -> int:
    base = {"component": "BACKEND", "request_id": "req_003", "user_id": 7, "session_id": "sess_vendor_7", "request_id_prefix": "req_mig_"}
    emit_prelude(fmt=fmt, jitter=jitter, count=prelude_count, base=base)
    emit("BACKEND INFO request_in method=GET path=/order/vendor/ vendor_id=7 request_id=req_003", fmt, base)
    jitter_sleep(enabled=jitter)
    emit("BACKEND INFO service call services.order_service.OrderService.vendor_dashboard vendor_id=7", fmt, base)
    jitter_sleep(enabled=jitter)
    emit("DB DEBUG fetch order_items by vendor_id=7 count=12", fmt, base)
    emit("BACKEND ERROR vendor_dashboard_failed reason=type_mismatch_in_price_field migration=160dd810dc36", fmt, base)
    emit_block(
        """
Traceback (most recent call last):
  File "/Users/hariskumargs/Documents/Personal/TiDB-Hackathon/sample-ecommerce-app/backend/api/endpoints/order.py", line 29, in vendor_dashboard
    return await order_service.vendor_dashboard(vendor_id=current_user.role_id)
  File "/Users/hariskumargs/Documents/Personal/TiDB-Hackathon/sample-ecommerce-app/backend/services/order_service.py", line 35, in vendor_dashboard
    total_sales = sum([item.price * item.quantity for item in order_items])
  File "/Users/hariskumargs/Documents/Personal/TiDB-Hackathon/sample-ecommerce-app/backend/services/order_service.py", line 35, in <listcomp>
    total_sales = sum([item.price * item.quantity for item in order_items])
TypeError: unsupported operand type(s) for *: 'NoneType' and 'int'
        """.strip()
    )
    emit("BACKEND INFO response_out status=500 path=/order/vendor/ request_id=req_003", fmt, base)
    return 1


def scenario_taskq_oversell(fmt: str, jitter: bool, prelude_count: int) -> int:
    base = {"component": "TASKQ", "job_id": "job_123", "session_id": "sess_abc123", "request_id_prefix": "req_tq_"}
    emit_prelude(fmt=fmt, jitter=jitter, count=prelude_count, base=base)
    emit("TASKQ INFO enqueue job=add_order_items order_id=123", fmt, base)
    jitter_sleep(enabled=jitter)
    emit("TASKQ INFO execute task_queue.tasks.cart_tasks.add_order_items order_id=123", fmt, base)
    jitter_sleep(enabled=jitter)
    emit("DB DEBUG cart_summary customer_id=42 items=2", fmt, base)
    jitter_sleep(enabled=jitter)
    emit("TASKQ ERROR add_order_items_failed reason=oversell_detected sku=SKU-001 stock=1 requested=2", fmt, base)
    emit_block(
        """
Traceback (most recent call last):
  File "/Users/hariskumargs/Documents/Personal/TiDB-Hackathon/sample-ecommerce-app/backend/task_queue/tasks/cart_tasks.py", line 47, in add_order_items
    order_item = OrderItemsCreate(
  File "pydantic/main.py", line 341, in pydantic.main.BaseModel.__init__
    raise ValidationError(model='OrderItemsCreate', errors=[{'loc': ('quantity',), 'msg': 'oversell', 'type': 'value_error'}])
pydantic.error_wrappers.ValidationError: 1 validation error for OrderItemsCreate
quantity
  oversell (type=value_error)
        """.strip()
    )
    emit("TASKQ INFO execute task_queue.tasks.cart_tasks.update_stock_after_checkout order_id=123", fmt, base)
    emit("DB DEBUG order_items fetched count=0", fmt, base)
    emit("TASKQ WARN no_order_items_to_update order_id=123", fmt, base)
    return 1


def scenario_verify_payment_timeout(fmt: str, jitter: bool, prelude_count: int) -> int:
    base = {"component": "BACKEND", "request_id": "req_004", "user_id": 42, "session_id": "sess_abc123", "request_id_prefix": "req_vfy_"}
    emit_prelude(fmt=fmt, jitter=jitter, count=prelude_count, base=base)
    emit("BACKEND INFO request_in method=GET path=/cart/verify-payment/REF_ABC request_id=req_004", fmt, base)
    jitter_sleep(enabled=jitter)
    emit("BACKEND INFO service call services.cart_service.CartService.verify_order_payment", fmt, base)
    jitter_sleep(enabled=jitter)
    emit("PAYMENTS INFO verify_paystack payment_ref=REF_ABC", fmt, base)
    emit_block(
        """
Traceback (most recent call last):
  File "/Users/hariskumargs/Documents/Personal/TiDB-Hackathon/sample-ecommerce-app/backend/services/cart_service.py", line 157, in verify_order_payment
    payment_rsp = await self.paystack.verify_payment(payment_ref=payment_ref)
  File "/Users/hariskumargs/Documents/Personal/TiDB-Hackathon/sample-ecommerce-app/backend/core/paystack.py", line 53, in verify_payment
    rsp = await self.client.get(url=f"transaction/verify/{payment_ref}")
  File "/usr/local/lib/python3.11/site-packages/httpx/_client.py", line 1734, in _send_single_request
    raise httpx.ReadTimeout("Timed out while reading from Paystack")
httpx.ReadTimeout: Timed out while reading from Paystack
        """.strip()
    )
    emit("BACKEND ERROR verify_payment_failed request_id=req_004 status=502", fmt, base)
    return 1


def scenario_db_startup_failure(fmt: str, jitter: bool, prelude_count: int) -> int:
    base = {"component": "BOOT", "session_id": "sess_boot", "request_id_prefix": "req_boot_"}
    emit_prelude(fmt=fmt, jitter=jitter, count=prelude_count, base=base)
    emit("BOOT INFO starting FastAPI app import=backend.main", fmt, base)
    jitter_sleep(enabled=jitter)
    emit("DB INFO core.middleware.start_up_db attempting connection retries=0/3", fmt, base)
    jitter_sleep(enabled=jitter)
    emit("DB ERROR Database connection failed (Attempts: 1/3)", fmt, base)
    emit("DB ERROR Error: could not connect to server: Connection refused", fmt, base)
    emit("DB ERROR Database connection failed (Attempts: 2/3)", fmt, base)
    emit("DB ERROR Database connection failed (Attempts: 3/3)", fmt, base)
    emit("DB ERROR Failed to establish database connection after 3 attempts", fmt, base)
    emit_block(
        """
Traceback (most recent call last):
  File "/Users/hariskumargs/Documents/Personal/TiDB-Hackathon/sample-ecommerce-app/backend/main.py", line 7, in <module>
    from core.middleware import start_up_db
  File "/Users/hariskumargs/Documents/Personal/TiDB-Hackathon/sample-ecommerce-app/backend/core/middleware.py", line 48, in start_up_db
    raise DatabaseConnectionError
core.errors.DatabaseConnectionError
        """.strip()
    )
    return 1


def scenario_stripe_signature_error(fmt: str, jitter: bool, prelude_count: int) -> int:
    base = {"component": "PAYMENTS", "session_id": "sess_pay", "request_id_prefix": "req_stp_"}
    emit_prelude(fmt=fmt, jitter=jitter, count=prelude_count, base=base)
    emit("PAYMENTS INFO stripe_checkout_session quantity=2", fmt, base)
    jitter_sleep(enabled=jitter)
    emit("PAYMENTS ERROR stripe_checkout_session_failed", fmt, base)
    emit_block(
        """
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

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/Users/hariskumargs/Documents/Personal/TiDB-Hackathon/sample-ecommerce-app/backend/core/stripe_payment.py", line 29, in create_checkout_session
    raise ValueError()
ValueError
        """.strip()
    )
    return 1


SCENARIOS = {
    "paystack_timeout": scenario_paystack_timeout,
    "migration_type_mismatch": scenario_migration_type_mismatch,
    "taskq_oversell": scenario_taskq_oversell,
    "verify_payment_timeout": scenario_verify_payment_timeout,
    "db_startup_failure": scenario_db_startup_failure,
    "stripe_signature_error": scenario_stripe_signature_error,
}


def main(argv: List[str]) -> int:
    parser = argparse.ArgumentParser(description="Simulate realistic logs and crashes for known P1 scenarios.")
    parser.add_argument("scenario", choices=sorted(SCENARIOS.keys()), help="Scenario to simulate")
    parser.add_argument("--format", choices=["plain", "json"], default="json", help="Log output format")
    parser.add_argument("--min-logs", type=int, default=120, help="Minimum number of prelude log lines before the crash")
    parser.add_argument("--no-jitter", action="store_true", help="Disable network/processing jitter between logs")
    args = parser.parse_args(argv)

    random.seed(42)

    func = SCENARIOS[args.scenario]
    print(f"Running scenario: {args.scenario}")
    
    rc = func(fmt=args.format, jitter=not args.no_jitter, prelude_count=max(0, int(args.min_logs)))
    
    # Ensure non-zero exit to represent crash
    return rc if rc else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))