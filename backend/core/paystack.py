class PaystackClient:
            async with self.client as client:
                client.timeout = 60  # Increase timeout to 60 seconds
                rsp = await client.post(