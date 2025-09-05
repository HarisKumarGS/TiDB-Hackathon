import argparse
import json
import random
import sys
import time
import os
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import boto3
from botocore.exceptions import ClientError, NoCredentialsError


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


def upload_logs_to_s3(scenario: str, logs: List[str]) -> tuple[str, str, str]:
    """Upload logs to S3 bucket and return S3 URL, S3 key, and crash ID (folder UUID)"""
    try:
        # Generate random UUIDs for the S3 path
        folder_uuid = str(uuid.uuid4())
        file_uuid = str(uuid.uuid4())
        
        # Create S3 path: random-uuid/error/random-uuid.log
        s3_key = f"{folder_uuid}/error/{file_uuid}.log"
        bucket_name = os.environ.get("S3_BUCKET_NAME", "tidb-hackathon-bucket")
        
        # Create S3 client
        s3_client = boto3.client('s3')
        
        # Prepare log content
        log_content = f"Error Log File - Scenario: {scenario}\n"
        log_content += f"Generated at: {datetime.now().isoformat()}\n"
        log_content += "=" * 50 + "\n\n"
        for log in logs:
            log_content += log + "\n"
        
        # Upload to S3
        s3_client.put_object(
            Bucket=bucket_name,
            Key=s3_key,
            Body=log_content.encode('utf-8'),
            ContentType='text/plain'
        )
        
        # Generate S3 URL
        s3_url = f"https://{bucket_name}.s3.amazonaws.com/{s3_key}"
        
        print(f"✅ Logs uploaded to S3: {s3_url}", file=sys.stderr)
        return s3_url, s3_key, folder_uuid
        
    except NoCredentialsError:
        print("❌ AWS credentials not found. Please configure AWS credentials.", file=sys.stderr)
        # Fallback to local file generation
        filepath, filename = generate_log_file_fallback(scenario, logs)
        return filepath, filename, str(uuid.uuid4())
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'NoSuchBucket':
            print(f"❌ S3 bucket '{bucket_name}' does not exist.", file=sys.stderr)
        elif error_code == 'AccessDenied':
            print(f"❌ Access denied to S3 bucket '{bucket_name}'. Check permissions.", file=sys.stderr)
        else:
            print(f"❌ S3 error: {e}", file=sys.stderr)
        # Fallback to local file generation
        filepath, filename = generate_log_file_fallback(scenario, logs)
        return filepath, filename, str(uuid.uuid4())
    except Exception as e:
        print(f"❌ Unexpected error uploading to S3: {e}", file=sys.stderr)
        # Fallback to local file generation
        filepath, filename = generate_log_file_fallback(scenario, logs)
        return filepath, filename, str(uuid.uuid4())


def create_dynamodb_entry(crash_id: str, scenario: str, s3_url: str, s3_key: str, error_details: Dict[str, Any], users_impacted: int) -> bool:
    """Create a DynamoDB entry for the crash with metadata"""
    try:
        # Get DynamoDB table name from environment variable
        table_name = os.environ.get("DYNAMODB_TABLE_NAME", "tidb-hackathon-crash")
        
        # Create DynamoDB client
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(table_name)
        
        # Prepare the item for DynamoDB
        item = {
            'crashId': crash_id,  # Partition key
            'scenario': scenario,
            'timestamp': datetime.now().isoformat(),
            's3Url': s3_url,
            's3Key': s3_key,
            'errorDetails': {
                'title': error_details.get('title', ''),
                'description': error_details.get('description', ''),
                'severity': error_details.get('severity', 'UNKNOWN'),
                'component': error_details.get('component', 'UNKNOWN'),
                'errorType': error_details.get('error_type', 'UNKNOWN')
            },
            'usersImpacted': users_impacted,
            'status': 'ACTIVE',
            'createdAt': datetime.now().isoformat(),
            'updatedAt': datetime.now().isoformat()
        }
        
        # Put item in DynamoDB
        table.put_item(Item=item)
        
        print(f"✅ DynamoDB entry created: {crash_id}", file=sys.stderr)
        return True
        
    except NoCredentialsError:
        print("❌ AWS credentials not found for DynamoDB. Skipping database entry.", file=sys.stderr)
        return False
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'ResourceNotFoundException':
            print(f"❌ DynamoDB table '{table_name}' does not exist.", file=sys.stderr)
        elif error_code == 'AccessDenied':
            print(f"❌ Access denied to DynamoDB table '{table_name}'. Check permissions.", file=sys.stderr)
        else:
            print(f"❌ DynamoDB error: {e}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"❌ Unexpected error creating DynamoDB entry: {e}", file=sys.stderr)
        return False


def generate_log_file_fallback(scenario: str, logs: List[str]) -> tuple[str, str]:
    """Fallback function to generate local log file when S3 upload fails"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"error_logs_{scenario}_{timestamp}.log"
    filepath = os.path.join(os.getcwd(), filename)
    
    with open(filepath, 'w') as f:
        f.write(f"Error Log File - Scenario: {scenario}\n")
        f.write(f"Generated at: {datetime.now().isoformat()}\n")
        f.write("=" * 50 + "\n\n")
        for log in logs:
            f.write(log + "\n")
    
    print(f"📄 Fallback: Log file generated locally: {filepath}", file=sys.stderr)
    return filepath, filename


def analyze_error_from_traceback(traceback: str, scenario: str) -> Dict[str, Any]:
    """Analyze the stack trace to extract error details"""
    error_details = {
        "title": "",
        "description": "",
        "severity": "HIGH",
        "component": "UNKNOWN",
        "error_type": "UNKNOWN"
    }
    
    # Extract error type from the last line of traceback
    lines = traceback.strip().split('\n')
    if lines:
        last_line = lines[-1].strip()
        if ':' in last_line:
            error_type = last_line.split(':')[0]
            error_details["error_type"] = error_type
    
    # Map scenarios to specific error details
    if scenario == "paystack_timeout":
        error_details.update({
            "title": "Payment Gateway Timeout - Checkout Process Failed",
            "description": "Paystack payment gateway connection timed out during checkout process. Users are unable to complete purchases, resulting in lost revenue and poor customer experience.",
            "severity": "CRITICAL",
            "component": "PAYMENT_SERVICE"
        })
    elif scenario == "migration_type_mismatch":
        error_details.update({
            "title": "Database Migration Type Mismatch Error",
            "description": "Database migration 160dd810dc36 introduced a type mismatch in the price field. Vendor dashboard calculations are failing due to NoneType values in price calculations.",
            "severity": "HIGH",
            "component": "DATABASE"
        })
    elif scenario == "taskq_oversell":
        error_details.update({
            "title": "Inventory Oversell Detection - Order Processing Failed",
            "description": "Task queue detected an oversell condition where requested quantity (2) exceeds available stock (1) for SKU-001. Order processing has been blocked to prevent inventory inconsistencies.",
            "severity": "HIGH",
            "component": "INVENTORY_SERVICE"
        })
    elif scenario == "verify_payment_timeout":
        error_details.update({
            "title": "Payment Verification Timeout",
            "description": "Payment verification with Paystack timed out while reading response. Order status remains uncertain, potentially causing duplicate charges or failed order confirmations.",
            "severity": "HIGH",
            "component": "PAYMENT_SERVICE"
        })
    elif scenario == "db_startup_failure":
        error_details.update({
            "title": "Database Connection Failure - Service Startup Failed",
            "description": "Application failed to start due to database connection issues after 3 retry attempts. All database-dependent services are unavailable.",
            "severity": "CRITICAL",
            "component": "DATABASE"
        })
    elif scenario == "stripe_signature_error":
        error_details.update({
            "title": "Stripe Signature Verification Failed",
            "description": "Stripe webhook signature verification failed, indicating potential security issue or configuration problem. Payment processing may be compromised.",
            "severity": "HIGH",
            "component": "PAYMENT_SERVICE"
        })
    
    return error_details


def generate_log_file(scenario: str, logs: List[str]) -> tuple[str, str, str]:
    """Generate a log file and upload to S3, return S3 URL, file identifier, and crash ID"""
    s3_url, s3_key, crash_id = upload_logs_to_s3(scenario, logs)
    return s3_url, s3_key, crash_id


def send_slack_notification(error_details: Dict[str, Any], s3_url: str, s3_key: str, users_impacted: int, sample_link: str) -> bool:
    """Send error notification to Slack"""
    try:
        # Get Bot User OAuth Token from environment variable
        slack_token = os.environ.get("SLACK_BOT_TOKEN")
        if not slack_token:
            print("❌ SLACK_BOT_TOKEN environment variable not set", file=sys.stderr)
            return False
        
        # Initialize Slack client
        client = WebClient(token=slack_token)
        
        # Get channel ID from environment variable or use default
        channel_id = os.environ.get("SLACK_CHANNEL_ID", "C09DTJ9K5PW")
        
        # Create the message payload
        message = {
            "channel": channel_id,
            "text": f"🚨 *{error_details['title']}*",
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": f"🚨 {error_details['title']}"
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"*Severity:*\n{error_details['severity']}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Component:*\n{error_details['component']}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Error Type:*\n{error_details['error_type']}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Users Impacted:*\n{users_impacted:,}"
                        }
                    ]
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Description:*\n{error_details['description']}"
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"*Log File:*\n<{s3_url}|{s3_key.split('/')[-1]}>"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Sample Link:*\n<{sample_link}|View Error Details>"
                        }
                    ]
                },
                {
                    "type": "divider"
                },
                {
                    "type": "context",
                    "elements": [
                        {
                            "type": "mrkdwn",
                            "text": f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')} | 🔧 Auto-generated from CrashLens Bot"
                        }
                    ]
                }
            ]
        }
        
        # Send the message
        response = client.chat_postMessage(**message)
        
        if response["ok"]:
            print(f"✅ Message sent: {response['ts']}", file=sys.stderr)
            print(f"✅ Slack notification sent successfully to channel {channel_id}", file=sys.stderr)
            return True
        else:
            print(f"❌ Failed to send Slack notification: {response['error']}", file=sys.stderr)
            return False
            
    except SlackApiError as e:
        print(f"❌ Error sending message: {e.response['error']}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"❌ Error sending Slack notification: {str(e)}", file=sys.stderr)
        return False


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


def scenario_paystack_timeout(fmt: str, jitter: bool, prelude_count: int) -> tuple[int, str, List[str]]:
    base = {"component": "BACKEND", "request_id": "req_001", "user_id": 42, "session_id": "sess_abc123", "request_id_prefix": "req_pyt_"}
    logs = []
    
    # Collect prelude logs
    prelude_logs = []
    session_id = base.get("session_id", "sess_abc123")
    user_id = base.get("user_id", 42)
    cart_id = base.get("cart_id", "cart_77")
    request_id_prefix = base.get("request_id_prefix", "req_pre_")
    pages = ["/", "/products", "/products/price", "/cart", "/checkout"]
    skus = ["SKU-001", "SKU-002", "SKU-003"]
    for i in range(prelude_count):
        jitter_sleep(enabled=jitter)
        page = pages[i % len(pages)]
        sku = skus[i % len(skus)]
        rid = f"{request_id_prefix}{i:03d}"
        choice = i % 12
        if choice == 0:
            log_line = f"FRONTEND INFO page_load path={page} build=prod session_id={session_id}"
        elif choice == 1:
            log_line = f"FRONTEND DEBUG api_request method=GET url=/products page={page} request_id={rid}"
        elif choice == 2:
            log_line = f"BACKEND INFO request_in method=GET path=/products request_id={rid}"
        elif choice == 3:
            log_line = f"DB DEBUG query=SELECT products ORDER BY price limit=20 request_id={rid}"
        elif choice == 4:
            log_line = f"BACKEND INFO response_out status=200 path=/products request_id={rid}"
        elif choice == 5:
            log_line = f"FRONTEND INFO click action=add_to_cart sku={sku} user_id={user_id}"
        elif choice == 6:
            log_line = f"BACKEND INFO request_in method=POST path=/cart/add user_id={user_id} request_id={rid}"
        elif choice == 7:
            log_line = f"DB DEBUG insert cart_id={cart_id} sku={sku} qty=1 request_id={rid}"
        elif choice == 8:
            log_line = f"TASKQ INFO enqueue job=add_order_items candidate_order_id=NA cart_id={cart_id}"
        elif choice == 9:
            log_line = f"ALB INFO forward_request target_group=ecom-backend listener=443 rule={page} request_id={rid}"
        elif choice == 10:
            log_line = f"CLOUDWATCH DEBUG metrics request_latency_ms={random.randint(20,180)} path={page}"
        else:
            log_line = f"SECURITY INFO cors_check origin=https://app.example.com result=allowed request_id={rid}"
        
        emit(log_line, fmt, base)
        prelude_logs.append(f"{now_iso()} {log_line}")
    
    # Main scenario logs
    jitter_sleep(enabled=jitter)
    log_line = "BACKEND INFO request_in method=POST path=/cart/checkout user_id=42 request_id=req_001"
    emit(log_line, fmt, base)
    logs.append(f"{now_iso()} {log_line}")
    
    base = {"component": "BACKEND", "request_id": "req_001"}
    log_line = "BACKEND INFO request_in method=POST path=/cart/checkout user_id=42 request_id=req_001"
    emit(log_line, fmt, base)
    logs.append(f"{now_iso()} {log_line}")
    
    jitter_sleep(enabled=jitter)
    log_line = "BACKEND DEBUG route handler=api.endpoints.cart.checkout deps=get_cart_service,get_current_verified_customer"
    emit(log_line, fmt, base)
    logs.append(f"{now_iso()} {log_line}")
    
    jitter_sleep(enabled=jitter)
    log_line = "BACKEND INFO service call services.cart_service.CartService.checkout customer_id=42"
    emit(log_line, fmt, base)
    logs.append(f"{now_iso()} {log_line}")
    
    jitter_sleep(enabled=jitter)
    log_line = "DB DEBUG get_cart_summary customer_id=42 items=2 total_amount=129900"
    emit(log_line, fmt, base)
    logs.append(f"{now_iso()} {log_line}")
    
    jitter_sleep(enabled=jitter)
    log_line = "PAYMENTS INFO initializing_paystack amount=129900 channel=CARD email=jane@example.com"
    emit(log_line, fmt, base)
    logs.append(f"{now_iso()} {log_line}")
    
    jitter_sleep(enabled=jitter)
    log_line = "PAYMENTS ERROR paystack_initialize_timeout timeout_ms=2000"
    emit(log_line, fmt, base)
    logs.append(f"{now_iso()} {log_line}")
    
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
    
    emit_block(traceback_text)
    logs.append(traceback_text)
    
    jitter_sleep(enabled=jitter)
    log_line = "DB DEBUG rollback_tx reason=payment_timeout request_id=req_001"
    emit(log_line, fmt, base)
    logs.append(f"{now_iso()} {log_line}")
    
    log_line = "BACKEND INFO response_out status=502 path=/cart/checkout request_id=req_001"
    emit(log_line, fmt, base)
    logs.append(f"{now_iso()} {log_line}")
    
    all_logs = prelude_logs + logs
    return 1, traceback_text, all_logs


def scenario_migration_type_mismatch(fmt: str, jitter: bool, prelude_count: int) -> tuple[int, str, List[str]]:
    base = {"component": "BACKEND", "request_id": "req_003", "user_id": 7, "session_id": "sess_vendor_7", "request_id_prefix": "req_mig_"}
    logs = []
    
    # Collect prelude logs (simplified for brevity)
    for i in range(prelude_count):
        jitter_sleep(enabled=jitter)
        log_line = f"BACKEND INFO prelude_log_{i} request_id=req_003"
        emit(log_line, fmt, base)
        logs.append(f"{now_iso()} {log_line}")
    
    log_line = "BACKEND INFO request_in method=GET path=/order/vendor/ vendor_id=7 request_id=req_003"
    emit(log_line, fmt, base)
    logs.append(f"{now_iso()} {log_line}")
    
    jitter_sleep(enabled=jitter)
    log_line = "BACKEND INFO service call services.order_service.OrderService.vendor_dashboard vendor_id=7"
    emit(log_line, fmt, base)
    logs.append(f"{now_iso()} {log_line}")
    
    jitter_sleep(enabled=jitter)
    log_line = "DB DEBUG fetch order_items by vendor_id=7 count=12"
    emit(log_line, fmt, base)
    logs.append(f"{now_iso()} {log_line}")
    
    log_line = "BACKEND ERROR vendor_dashboard_failed reason=type_mismatch_in_price_field migration=160dd810dc36"
    emit(log_line, fmt, base)
    logs.append(f"{now_iso()} {log_line}")
    
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
    
    emit_block(traceback_text)
    logs.append(traceback_text)
    
    log_line = "BACKEND INFO response_out status=500 path=/order/vendor/ request_id=req_003"
    emit(log_line, fmt, base)
    logs.append(f"{now_iso()} {log_line}")
    
    return 1, traceback_text, logs


def scenario_taskq_oversell(fmt: str, jitter: bool, prelude_count: int) -> tuple[int, str, List[str]]:
    base = {"component": "TASKQ", "job_id": "job_123", "session_id": "sess_abc123", "request_id_prefix": "req_tq_"}
    logs = []
    
    # Collect prelude logs
    for i in range(prelude_count):
        jitter_sleep(enabled=jitter)
        log_line = f"TASKQ INFO prelude_log_{i} job_id=job_123"
        emit(log_line, fmt, base)
        logs.append(f"{now_iso()} {log_line}")
    
    log_line = "TASKQ INFO enqueue job=add_order_items order_id=123"
    emit(log_line, fmt, base)
    logs.append(f"{now_iso()} {log_line}")
    
    jitter_sleep(enabled=jitter)
    log_line = "TASKQ INFO execute task_queue.tasks.cart_tasks.add_order_items order_id=123"
    emit(log_line, fmt, base)
    logs.append(f"{now_iso()} {log_line}")
    
    jitter_sleep(enabled=jitter)
    log_line = "DB DEBUG cart_summary customer_id=42 items=2"
    emit(log_line, fmt, base)
    logs.append(f"{now_iso()} {log_line}")
    
    jitter_sleep(enabled=jitter)
    log_line = "TASKQ ERROR add_order_items_failed reason=oversell_detected sku=SKU-001 stock=1 requested=2"
    emit(log_line, fmt, base)
    logs.append(f"{now_iso()} {log_line}")
    
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
    
    emit_block(traceback_text)
    logs.append(traceback_text)
    
    log_line = "TASKQ INFO execute task_queue.tasks.cart_tasks.update_stock_after_checkout order_id=123"
    emit(log_line, fmt, base)
    logs.append(f"{now_iso()} {log_line}")
    
    log_line = "DB DEBUG order_items fetched count=0"
    emit(log_line, fmt, base)
    logs.append(f"{now_iso()} {log_line}")
    
    log_line = "TASKQ WARN no_order_items_to_update order_id=123"
    emit(log_line, fmt, base)
    logs.append(f"{now_iso()} {log_line}")
    
    return 1, traceback_text, logs


def scenario_verify_payment_timeout(fmt: str, jitter: bool, prelude_count: int) -> tuple[int, str, List[str]]:
    base = {"component": "BACKEND", "request_id": "req_004", "user_id": 42, "session_id": "sess_abc123", "request_id_prefix": "req_vfy_"}
    logs = []
    
    # Collect prelude logs
    for i in range(prelude_count):
        jitter_sleep(enabled=jitter)
        log_line = f"BACKEND INFO prelude_log_{i} request_id=req_004"
        emit(log_line, fmt, base)
        logs.append(f"{now_iso()} {log_line}")
    
    log_line = "BACKEND INFO request_in method=GET path=/cart/verify-payment/REF_ABC request_id=req_004"
    emit(log_line, fmt, base)
    logs.append(f"{now_iso()} {log_line}")
    
    jitter_sleep(enabled=jitter)
    log_line = "BACKEND INFO service call services.cart_service.CartService.verify_order_payment"
    emit(log_line, fmt, base)
    logs.append(f"{now_iso()} {log_line}")
    
    jitter_sleep(enabled=jitter)
    log_line = "PAYMENTS INFO verify_paystack payment_ref=REF_ABC"
    emit(log_line, fmt, base)
    logs.append(f"{now_iso()} {log_line}")
    
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
    
    emit_block(traceback_text)
    logs.append(traceback_text)
    
    log_line = "BACKEND ERROR verify_payment_failed request_id=req_004 status=502"
    emit(log_line, fmt, base)
    logs.append(f"{now_iso()} {log_line}")
    
    return 1, traceback_text, logs


def scenario_db_startup_failure(fmt: str, jitter: bool, prelude_count: int) -> tuple[int, str, List[str]]:
    base = {"component": "BOOT", "session_id": "sess_boot", "request_id_prefix": "req_boot_"}
    logs = []
    
    # Collect prelude logs
    for i in range(prelude_count):
        jitter_sleep(enabled=jitter)
        log_line = f"BOOT INFO prelude_log_{i} session_id=sess_boot"
        emit(log_line, fmt, base)
        logs.append(f"{now_iso()} {log_line}")
    
    log_line = "BOOT INFO starting FastAPI app import=backend.main"
    emit(log_line, fmt, base)
    logs.append(f"{now_iso()} {log_line}")
    
    jitter_sleep(enabled=jitter)
    log_line = "DB INFO core.middleware.start_up_db attempting connection retries=0/3"
    emit(log_line, fmt, base)
    logs.append(f"{now_iso()} {log_line}")
    
    jitter_sleep(enabled=jitter)
    log_line = "DB ERROR Database connection failed (Attempts: 1/3)"
    emit(log_line, fmt, base)
    logs.append(f"{now_iso()} {log_line}")
    
    log_line = "DB ERROR Error: could not connect to server: Connection refused"
    emit(log_line, fmt, base)
    logs.append(f"{now_iso()} {log_line}")
    
    log_line = "DB ERROR Database connection failed (Attempts: 2/3)"
    emit(log_line, fmt, base)
    logs.append(f"{now_iso()} {log_line}")
    
    log_line = "DB ERROR Database connection failed (Attempts: 3/3)"
    emit(log_line, fmt, base)
    logs.append(f"{now_iso()} {log_line}")
    
    log_line = "DB ERROR Failed to establish database connection after 3 attempts"
    emit(log_line, fmt, base)
    logs.append(f"{now_iso()} {log_line}")
    
    traceback_text = """
Traceback (most recent call last):
  File "/Users/hariskumargs/Documents/Personal/TiDB-Hackathon/sample-ecommerce-app/backend/main.py", line 7, in <module>
    from core.middleware import start_up_db
  File "/Users/hariskumargs/Documents/Personal/TiDB-Hackathon/sample-ecommerce-app/backend/core/middleware.py", line 48, in start_up_db
    raise DatabaseConnectionError
core.errors.DatabaseConnectionError
        """.strip()
    
    emit_block(traceback_text)
    logs.append(traceback_text)
    
    return 1, traceback_text, logs


def scenario_stripe_signature_error(fmt: str, jitter: bool, prelude_count: int) -> tuple[int, str, List[str]]:
    base = {"component": "PAYMENTS", "session_id": "sess_pay", "request_id_prefix": "req_stp_"}
    logs = []
    
    # Collect prelude logs
    for i in range(prelude_count):
        jitter_sleep(enabled=jitter)
        log_line = f"PAYMENTS INFO prelude_log_{i} session_id=sess_pay"
        emit(log_line, fmt, base)
        logs.append(f"{now_iso()} {log_line}")
    
    log_line = "PAYMENTS INFO stripe_checkout_session quantity=2"
    emit(log_line, fmt, base)
    logs.append(f"{now_iso()} {log_line}")
    
    jitter_sleep(enabled=jitter)
    log_line = "PAYMENTS ERROR stripe_checkout_session_failed"
    emit(log_line, fmt, base)
    logs.append(f"{now_iso()} {log_line}")
    
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

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/Users/hariskumargs/Documents/Personal/TiDB-Hackathon/sample-ecommerce-app/backend/core/stripe_payment.py", line 29, in create_checkout_session
    raise ValueError()
ValueError
        """.strip()
    
    emit_block(traceback_text)
    logs.append(traceback_text)
    
    return 1, traceback_text, logs


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
    print(f"Running scenario: {args.scenario}", file=sys.stderr)
    
    rc, traceback_text, logs = func(fmt=args.format, jitter=not args.no_jitter, prelude_count=max(0, int(args.min_logs)))
    
    # Generate error analysis
    error_details = analyze_error_from_traceback(traceback_text, args.scenario)
    
    # Generate log file and upload to S3
    s3_url, s3_key, crash_id = generate_log_file(args.scenario, logs)
    print(f"📄 Log file uploaded to S3: {s3_url}", file=sys.stderr)
    
    # Generate random user impact and sample link
    users_impacted = random.randint(50, 5000)
    sample_link = f"https://monitoring.example.com/errors/{args.scenario}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # Create DynamoDB entry
    print(f"💾 Creating DynamoDB entry...", file=sys.stderr)
    dynamodb_success = create_dynamodb_entry(
        crash_id=crash_id,
        scenario=args.scenario,
        s3_url=s3_url,
        s3_key=s3_key,
        error_details=error_details,
        users_impacted=users_impacted
    )
    
    # Send Slack notification
    print(f"📤 Sending Slack notification...", file=sys.stderr)
    slack_success = send_slack_notification(
        error_details=error_details,
        s3_url=s3_url,
        s3_key=s3_key,
        users_impacted=users_impacted,
        sample_link=sample_link
    )
    
    if slack_success:
        print(f"✅ Error notification sent successfully!", file=sys.stderr)
    else:
        print(f"❌ Failed to send error notification", file=sys.stderr)
    
    if dynamodb_success:
        print(f"✅ DynamoDB entry created successfully!", file=sys.stderr)
    else:
        print(f"❌ Failed to create DynamoDB entry", file=sys.stderr)
    
    # Print summary
    print(f"\n📊 Error Summary:", file=sys.stderr)
    print(f"   Title: {error_details['title']}", file=sys.stderr)
    print(f"   Severity: {error_details['severity']}", file=sys.stderr)
    print(f"   Component: {error_details['component']}", file=sys.stderr)
    print(f"   Users Impacted: {users_impacted:,}", file=sys.stderr)
    print(f"   Crash ID: {crash_id}", file=sys.stderr)
    print(f"   Log File: {s3_key.split('/')[-1]}", file=sys.stderr)
    print(f"   S3 URL: {s3_url}", file=sys.stderr)
    
    # Ensure non-zero exit to represent crash
    return rc if rc else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))