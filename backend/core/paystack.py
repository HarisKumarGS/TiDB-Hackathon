        timeout = 60  # Increase timeout to 60 seconds
            rsp = await self.client.get(
                url=f"transaction/verify/{payment_ref}",
                timeout=timeout
            )