#!/usr/bin/env python3
"""
E-commerce Production Log Simulator

Generates realistic production logs in structured JSON format across multiple services.
Simulates normal operations and failure scenarios including SQL injection attacks.
"""

import json
import time
import random
import uuid
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from faker import Faker
import queue
import sys

fake = Faker()

class EcommerceData:
    """Generates realistic e-commerce data"""
    
    def __init__(self):
        # Generate users
        self.users = []
        for i in range(500):
            self.users.append({
                'user_id': f'user_{i:04d}',
                'name': fake.name(),
                'email': fake.email(),
                'created_at': fake.date_time_between(start_date='-2y', end_date='now')
            })
        
        # Generate products
        self.categories = ['Electronics', 'Clothing', 'Books', 'Home & Garden', 'Sports', 'Toys', 'Beauty', 'Food']
        self.products = []
        for i in range(1000):
            self.products.append({
                'product_id': f'prod_{i:04d}',
                'name': fake.catch_phrase(),
                'category': random.choice(self.categories),
                'price': round(random.uniform(9.99, 999.99), 2),
                'stock': random.randint(0, 100),
                'rating': round(random.uniform(1.0, 5.0), 1)
            })
        
        # Generate orders
        self.orders = []
        for i in range(2000):
            user = random.choice(self.users)
            products = random.sample(self.products, random.randint(1, 5))
            total = sum(p['price'] for p in products)
            
            self.orders.append({
                'order_id': f'ord_{i:04d}',
                'user_id': user['user_id'],
                'products': [p['product_id'] for p in products],
                'total': round(total, 2),
                'status': random.choice(['pending', 'processing', 'shipped', 'delivered', 'cancelled']),
                'created_at': fake.date_time_between(start_date='-1y', end_date='now')
            })
    
    def get_random_user(self):
        return random.choice(self.users)
    
    def get_random_product(self):
        return random.choice(self.products)
    
    def get_random_order(self):
        return random.choice(self.orders)

class LogGenerator:
    """Generates structured logs for different services"""
    
    def __init__(self, ecommerce_data: EcommerceData):
        self.data = ecommerce_data
        self.request_counter = 0
        self.failure_injected = False
        self.start_time = time.time()
        
    def generate_request_id(self):
        self.request_counter += 1
        return str(uuid.uuid4())
    
    def create_log_entry(self, level: str, service: str, message: str, 
                        user_id: Optional[str] = None, extra: Optional[Dict] = None) -> Dict[str, Any]:
        """Creates a structured log entry"""
        return {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'level': level,
            'service': service,
            'request_id': self.generate_request_id(),
            'user_id': user_id,
            'message': message,
            'extra': extra or {}
        }
    
    def generate_application_logs(self) -> Dict[str, Any]:
        """Generate frontend/backend application logs"""
        log_types = [
            'user_login', 'user_logout', 'product_view', 'add_to_cart', 
            'checkout_start', 'order_created', 'payment_success', 'review_posted'
        ]
        
        log_type = random.choice(log_types)
        user = self.data.get_random_user()
        
        if log_type == 'user_login':
            return self.create_log_entry(
                'INFO', 'frontend', f"User {user['name']} logged in successfully",
                user['user_id'], 
                {'ip_address': fake.ipv4(), 'user_agent': fake.user_agent()}
            )
        
        elif log_type == 'product_view':
            product = self.data.get_random_product()
            return self.create_log_entry(
                'INFO', 'backend', f"Product viewed: {product['name']}",
                user['user_id'],
                {'product_id': product['product_id'], 'category': product['category'], 'response_time_ms': random.randint(50, 300)}
            )
        
        elif log_type == 'add_to_cart':
            product = self.data.get_random_product()
            return self.create_log_entry(
                'INFO', 'cart-service', f"Item added to cart",
                user['user_id'],
                {'product_id': product['product_id'], 'quantity': random.randint(1, 3), 'cart_total': round(random.uniform(50, 500), 2)}
            )
        
        elif log_type == 'checkout_start':
            return self.create_log_entry(
                'INFO', 'checkout-service', f"Checkout process initiated",
                user['user_id'],
                {'cart_items': random.randint(1, 5), 'total_amount': round(random.uniform(25, 750), 2)}
            )
        
        elif log_type == 'order_created':
            order = self.data.get_random_order()
            return self.create_log_entry(
                'INFO', 'order-service', f"New order created: {order['order_id']}",
                user['user_id'],
                {'order_id': order['order_id'], 'total': order['total'], 'items_count': len(order['products'])}
            )
        
        elif log_type == 'payment_success':
            return self.create_log_entry(
                'INFO', 'payment-service', f"Payment processed successfully",
                user['user_id'],
                {'payment_method': random.choice(['credit_card', 'debit_card', 'paypal']), 
                 'amount': round(random.uniform(10, 500), 2), 
                 'transaction_id': f'txn_{uuid.uuid4().hex[:8]}'}
            )
        
        else:  # review_posted
            product = self.data.get_random_product()
            return self.create_log_entry(
                'INFO', 'review-service', f"Review posted for product",
                user['user_id'],
                {'product_id': product['product_id'], 'rating': random.randint(1, 5), 'review_length': random.randint(20, 500)}
            )
    
    def generate_database_logs(self) -> Dict[str, Any]:
        """Generate database-related logs"""
        log_types = ['slow_query', 'connection_pool', 'replication_lag', 'deadlock', 'index_scan']
        log_type = random.choice(log_types)
        
        if log_type == 'slow_query':
            queries = [
                "SELECT * FROM products WHERE category = 'Electronics' ORDER BY rating DESC",
                "UPDATE orders SET status = 'shipped' WHERE order_id = 'ord_1234'",
                "SELECT COUNT(*) FROM reviews JOIN products ON reviews.product_id = products.product_id WHERE products.category = 'Books'"
            ]
            return self.create_log_entry(
                'WARN', 'database', f"Slow query detected",
                None,
                {'query': random.choice(queries), 'execution_time_ms': random.randint(1000, 5000), 'table': 'products'}
            )
        
        elif log_type == 'connection_pool':
            return self.create_log_entry(
                'DEBUG', 'database', f"Connection pool status",
                None,
                {'active_connections': random.randint(15, 45), 'max_connections': 50, 'pool_utilization': f"{random.randint(30, 90)}%"}
            )
        
        elif log_type == 'replication_lag':
            return self.create_log_entry(
                'WARN', 'database', f"Replication lag detected",
                None,
                {'lag_seconds': random.randint(1, 10), 'master_host': 'db-master-1', 'slave_host': 'db-slave-2'}
            )
        
        elif log_type == 'deadlock':
            return self.create_log_entry(
                'ERROR', 'database', f"Deadlock detected and resolved",
                None,
                {'table1': 'orders', 'table2': 'inventory', 'resolution': 'transaction_rollback', 'duration_ms': random.randint(100, 500)}
            )
        
        else:  # index_scan
            return self.create_log_entry(
                'DEBUG', 'database', f"Full table scan avoided with index",
                None,
                {'table': random.choice(['products', 'orders', 'users', 'reviews']), 'index_used': 'idx_category_rating', 'rows_examined': random.randint(100, 10000)}
            )
    
    def generate_aws_logs(self) -> Dict[str, Any]:
        """Generate AWS service logs"""
        services = ['api-gateway', 's3', 'cloudfront', 'lambda', 'ecs', 'cloudwatch']
        service = random.choice(services)
        
        if service == 'api-gateway':
            return self.create_log_entry(
                random.choice(['INFO', 'WARN']), 'aws-apigateway', 
                f"API request processed",
                None,
                {'endpoint': '/api/products/search', 'method': 'GET', 'status_code': random.choice([200, 200, 200, 429, 503]), 
                 'latency_ms': random.randint(50, 2000), 'request_size': random.randint(200, 2000)}
            )
        
        elif service == 's3':
            return self.create_log_entry(
                'INFO', 'aws-s3', 
                f"Object uploaded successfully",
                None,
                {'bucket': 'ecommerce-product-images', 'object_key': f'products/img_{uuid.uuid4().hex[:8]}.jpg', 
                 'size_bytes': random.randint(50000, 500000), 'storage_class': 'STANDARD'}
            )
        
        elif service == 'cloudfront':
            return self.create_log_entry(
                'INFO', 'aws-cloudfront', 
                f"CDN cache hit",
                None,
                {'cache_status': random.choice(['Hit', 'Miss', 'RefreshHit']), 'edge_location': random.choice(['LAX', 'DFW', 'IAD', 'SFO']), 
                 'response_time_ms': random.randint(10, 100)}
            )
        
        elif service == 'lambda':
            return self.create_log_entry(
                random.choice(['INFO', 'WARN']), 'aws-lambda', 
                f"Function execution completed",
                None,
                {'function_name': 'product-recommendation-engine', 'duration_ms': random.randint(100, 5000), 
                 'memory_used_mb': random.randint(64, 256), 'cold_start': random.choice([True, False, False, False])}
            )
        
        elif service == 'ecs':
            return self.create_log_entry(
                'INFO', 'aws-ecs', 
                f"Container health check passed",
                None,
                {'cluster': 'ecommerce-prod', 'service': 'backend-api', 'task_arn': f'arn:aws:ecs:us-west-2:123456789012:task/{uuid.uuid4()}',
                 'cpu_utilization': f"{random.randint(20, 80)}%", 'memory_utilization': f"{random.randint(30, 90)}%"}
            )
        
        else:  # cloudwatch
            return self.create_log_entry(
                'INFO', 'aws-cloudwatch', 
                f"Metric data point recorded",
                None,
                {'metric_name': random.choice(['CPUUtilization', 'DatabaseConnections', 'RequestCount']), 
                 'value': random.randint(1, 100), 'unit': random.choice(['Percent', 'Count', 'Seconds'])}
            )
    
    def generate_infrastructure_logs(self) -> Dict[str, Any]:
        """Generate infrastructure and monitoring logs"""
        log_types = ['container_restart', 'load_balancer', 'auto_scaling', 'health_check']
        log_type = random.choice(log_types)
        
        if log_type == 'container_restart':
            return self.create_log_entry(
                'WARN', 'kubernetes', 
                f"Container restarted due to health check failure",
                None,
                {'pod_name': f'backend-api-{random.randint(1000, 9999)}', 'namespace': 'production', 
                 'restart_count': random.randint(1, 5), 'reason': random.choice(['OOMKilled', 'Error', 'Completed'])}
            )
        
        elif log_type == 'load_balancer':
            return self.create_log_entry(
                random.choice(['INFO', 'ERROR']), 'load-balancer', 
                f"Request routed to backend instance",
                None,
                {'target_instance': f'i-{uuid.uuid4().hex[:8]}', 'response_code': random.choice([200, 200, 200, 500, 502]), 
                 'response_time': random.randint(50, 1000), 'backend_processing_time': random.randint(20, 800)}
            )
        
        elif log_type == 'auto_scaling':
            return self.create_log_entry(
                'INFO', 'auto-scaling', 
                f"Scaling activity triggered",
                None,
                {'activity_type': random.choice(['scale_up', 'scale_down']), 'desired_capacity': random.randint(2, 10), 
                 'current_capacity': random.randint(1, 8), 'trigger_metric': 'CPUUtilization'}
            )
        
        else:  # health_check
            return self.create_log_entry(
                random.choice(['INFO', 'ERROR']), 'health-monitor', 
                f"Service health check completed",
                None,
                {'service': random.choice(['user-service', 'product-service', 'order-service']), 
                 'status': random.choice(['healthy', 'healthy', 'healthy', 'unhealthy']), 
                 'response_time_ms': random.randint(10, 500)}
            )
    
    def generate_security_logs(self) -> Dict[str, Any]:
        """Generate security-related logs"""
        log_types = ['failed_login', 'suspicious_activity', 'fraud_detection', 'rate_limiting']
        log_type = random.choice(log_types)
        
        if log_type == 'failed_login':
            return self.create_log_entry(
                'WARN', 'auth-service', 
                f"Failed login attempt",
                None,
                {'username': fake.email(), 'ip_address': fake.ipv4(), 'reason': random.choice(['invalid_password', 'account_locked', 'invalid_username']),
                 'user_agent': fake.user_agent(), 'attempt_count': random.randint(1, 5)}
            )
        
        elif log_type == 'suspicious_activity':
            return self.create_log_entry(
                'WARN', 'fraud-detection', 
                f"Suspicious activity detected",
                self.data.get_random_user()['user_id'],
                {'activity_type': random.choice(['multiple_rapid_orders', 'unusual_payment_pattern', 'high_value_transaction']),
                 'risk_score': random.randint(60, 95), 'location': fake.country()}
            )
        
        elif log_type == 'fraud_detection':
            return self.create_log_entry(
                'ERROR', 'fraud-detection', 
                f"Potential fraud detected - transaction blocked",
                self.data.get_random_user()['user_id'],
                {'transaction_amount': round(random.uniform(500, 5000), 2), 'payment_method': 'credit_card',
                 'fraud_indicators': ['velocity_check_failed', 'geolocation_mismatch'], 'blocked': True}
            )
        
        else:  # rate_limiting
            return self.create_log_entry(
                'WARN', 'rate-limiter', 
                f"Rate limit exceeded",
                None,
                {'ip_address': fake.ipv4(), 'endpoint': '/api/products/search', 'requests_per_minute': random.randint(100, 500),
                 'limit': 100, 'action': 'throttled'}
            )
    
    def generate_sql_injection_attack(self) -> List[Dict[str, Any]]:
        """Generate SQL injection attack sequence"""
        attacker_ip = "203.0.113.42"  # Example IP from RFC documentation
        malicious_payload = "admin' OR '1'='1' --"
        
        logs = []
        
        # 1. Frontend logs malicious login attempt
        logs.append(self.create_log_entry(
            'WARN', 'frontend', 
            f"Suspicious login attempt detected",
            None,
            {'username': malicious_payload, 'ip_address': attacker_ip, 'user_agent': 'curl/7.68.0',
             'payload_detected': True, 'security_scan': 'potential_sql_injection'}
        ))
        
        # 2. Backend processes the unsafe query
        logs.append(self.create_log_entry(
            'DEBUG', 'auth-service', 
            f"Executing user authentication query",
            None,
            {'query': f"SELECT * FROM users WHERE username = '{malicious_payload}' AND password = 'hashed_password'",
             'ip_address': attacker_ip}
        ))
        
        # 3. Database returns abnormal result
        logs.append(self.create_log_entry(
            'ERROR', 'database', 
            f"Query returned unexpected multiple rows",
            None,
            {'error': 'MultipleRowsReturnedError', 'rows_returned': 247, 'expected_rows': 1,
             'table': 'users', 'query_hash': 'abc123def456'}
        ))
        
        # 4. Backend hits unhandled exception
        logs.append(self.create_log_entry(
            'CRITICAL', 'auth-service', 
            f"Unhandled exception in authentication handler",
            None,
            {'exception': 'IndexError: list index out of range', 
             'stack_trace': 'File "/app/auth.py", line 45, in authenticate_user\\n  user = result[0]  # Expected single user',
             'ip_address': attacker_ip, 'request_id': self.generate_request_id()}
        ))
        
        # 5. System crash logged
        logs.append(self.create_log_entry(
            'CRITICAL', 'system', 
            f"Authentication service crashed - immediate restart required",
            None,
            {'service': 'auth-service', 'exit_code': 1, 'uptime_seconds': random.randint(3600, 86400),
             'last_error': 'IndexError', 'auto_restart': True}
        ))
        
        # 6. AWS ECS auto-restart
        logs.append(self.create_log_entry(
            'INFO', 'aws-ecs', 
            f"Container auto-restart initiated",
            None,
            {'cluster': 'ecommerce-prod', 'service': 'auth-service', 'reason': 'health_check_failed',
             'previous_task_stopped': True, 'new_task_starting': True, 'desired_count': 3}
        ))
        
        # 7. Load balancer notices unhealthy instance
        logs.append(self.create_log_entry(
            'ERROR', 'load-balancer', 
            f"Backend instance marked unhealthy",
            None,
            {'target_instance': f'i-{uuid.uuid4().hex[:8]}', 'health_check_failures': 3,
             'removed_from_rotation': True, 'remaining_healthy_instances': 2}
        ))
        
        return logs
    
    def should_inject_failure(self) -> bool:
        """Check if it's time to inject a failure scenario"""
        return (time.time() - self.start_time > 5.0) and not self.failure_injected
    
    def generate_log(self) -> Dict[str, Any]:
        """Generate a single log entry"""
        # Inject SQL injection attack after 5 seconds
        if self.should_inject_failure():
            self.failure_injected = True
            return self.generate_sql_injection_attack()
        
        # Normal log generation
        generators = [
            self.generate_application_logs,
            self.generate_database_logs,
            self.generate_aws_logs,
            self.generate_infrastructure_logs,
            self.generate_security_logs
        ]
        
        # Weight application logs more heavily
        weights = [0.4, 0.2, 0.2, 0.1, 0.1]
        generator = random.choices(generators, weights=weights)[0]
        
        return generator()

class LogSimulator:
    """Main log simulator class"""
    
    def __init__(self, logs_per_second: float = 10.0):
        self.ecommerce_data = EcommerceData()
        self.log_generator = LogGenerator(self.ecommerce_data)
        self.logs_per_second = logs_per_second
        self.running = True
        self.log_queue = queue.Queue()
        
    def generate_logs(self):
        """Background thread to generate logs"""
        while self.running:
            try:
                log = self.log_generator.generate_log()
                
                # Handle both single logs and lists of logs (for attack sequences)
                if isinstance(log, list):
                    for log_entry in log:
                        self.log_queue.put(log_entry)
                        time.sleep(0.1)  # Small delay between attack sequence logs
                else:
                    self.log_queue.put(log)
                
                time.sleep(1.0 / self.logs_per_second)
                
            except Exception as e:
                print(f"Error generating log: {e}", file=sys.stderr)
                time.sleep(0.1)
    
    def output_logs(self):
        """Main thread to output logs"""
        while self.running:
            try:
                log = self.log_queue.get(timeout=1.0)
                print(json.dumps(log, indent=2))
                sys.stdout.flush()
                self.log_queue.task_done()
            except queue.Empty:
                continue
            except KeyboardInterrupt:
                self.running = False
                break
            except Exception as e:
                print(f"Error outputting log: {e}", file=sys.stderr)
    
    def start(self):
        """Start the log simulator"""
        print("Starting E-commerce Production Log Simulator...", file=sys.stderr)
        print("Generating ~10 logs/second across multiple services", file=sys.stderr)
        print("SQL injection attack will be injected after 5 seconds", file=sys.stderr)
        print("Press Ctrl+C to stop\n", file=sys.stderr)
        
        # Start background log generation thread
        generator_thread = threading.Thread(target=self.generate_logs, daemon=True)
        generator_thread.start()
        
        try:
            self.output_logs()
        except KeyboardInterrupt:
            print("\nShutting down log simulator...", file=sys.stderr)
            self.running = False

def main():
    """Main entry point"""
    simulator = LogSimulator(logs_per_second=10.0)
    simulator.start()

if __name__ == "__main__":
    main()