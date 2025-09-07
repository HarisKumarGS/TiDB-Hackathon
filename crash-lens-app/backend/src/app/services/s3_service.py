import os
import uuid
from datetime import datetime
from typing import List, Tuple, Optional
import boto3
from botocore.exceptions import ClientError, NoCredentialsError


class S3Service:
    """Service for S3 operations including log file uploads"""
    
    def __init__(self):
        self.bucket_name = os.environ.get("S3_BUCKET_NAME", "tidb-hackathon-bucket")
        self.region = os.environ.get("AWS_REGION", "us-east-1")
        self.s3_client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize S3 client with credentials"""
        try:
            # Use boto3's default credential chain
            self.s3_client = boto3.client('s3', region_name=self.region)
            
            # Test the connection
            self.s3_client.head_bucket(Bucket=self.bucket_name)
            print(f"✅ S3 client initialized for bucket: {self.bucket_name}")
            
        except (NoCredentialsError, ClientError) as e:
            print(f"⚠️  S3 not available: {e}")
            self.s3_client = None
        except Exception as e:
            print(f"⚠️  Failed to initialize S3: {e}")
            self.s3_client = None
    
    def upload_logs_to_s3(self, scenario: str, logs: List[str], crash_id: str) -> Tuple[Optional[str], Optional[str], bool]:
        """
        Upload logs to S3 bucket and return S3 URL, S3 key, and success status
        
        Args:
            scenario: The crash scenario name
            logs: List of log lines to upload
            crash_id: Unique crash identifier
            
        Returns:
            Tuple of (s3_url, s3_key, success)
        """
        if not self.s3_client:
            return self._generate_fallback_file(scenario, logs, crash_id)
        
        try:
            # Generate S3 path: crash_id/error/crash_id.log
            s3_key = f"{crash_id}/error/{crash_id}.log"
            
            # Prepare log content
            log_content = f"Error Log File - Scenario: {scenario}\n"
            log_content += f"Generated at: {datetime.now().isoformat()}\n"
            log_content += f"Crash ID: {crash_id}\n"
            log_content += "=" * 50 + "\n\n"
            for log in logs:
                log_content += log + "\n"
            
            # Upload to S3
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=log_content.encode('utf-8'),
                ContentType='text/plain'
            )
            
            # Generate S3 URL
            s3_url = f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{s3_key}"
            
            print(f"✅ Logs uploaded to S3: {s3_url}")
            return s3_url, s3_key, True
            
        except Exception as e:
            print(f"❌ S3 upload failed: {e}")
            return self._generate_fallback_file(scenario, logs, crash_id)
    
    def _generate_fallback_file(self, scenario: str, logs: List[str], crash_id: str) -> Tuple[str, str, bool]:
        """Generate fallback local file when S3 upload fails"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"error_logs_{scenario}_{timestamp}.log"
        filepath = os.path.join(os.getcwd(), "logs", filename)
        
        # Create logs directory if it doesn't exist
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'w') as f:
            f.write(f"Error Log File - Scenario: {scenario}\n")
            f.write(f"Generated at: {datetime.now().isoformat()}\n")
            f.write(f"Crash ID: {crash_id}\n")
            f.write("=" * 50 + "\n\n")
            for log in logs:
                f.write(log + "\n")
        
        print(f"📄 Log saved locally: {filepath}")
        return filepath, filename, False
    
    def is_available(self) -> bool:
        """Check if S3 service is available and configured"""
        return self.s3_client is not None
    
    def get_bucket_info(self) -> dict:
        """Get information about the configured S3 bucket"""
        if not self.s3_client:
            return {"available": False, "error": "S3 client not initialized"}
        
        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
            return {
                "available": True,
                "bucket_name": self.bucket_name,
                "region": self.region,
                "status": "accessible"
            }
        except ClientError as e:
            return {
                "available": False,
                "bucket_name": self.bucket_name,
                "region": self.region,
                "error": str(e)
            }