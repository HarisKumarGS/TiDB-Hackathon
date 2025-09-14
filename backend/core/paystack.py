from httpx import ReadTimeout
        try:
            rsp = await self.client.get(url=url, headers=headers, timeout=30)
            rsp.raise_for_status()
            return rsp.json()
        except ReadTimeout:
            # Retry the request with an increased timeout
            rsp = await self.client.get(url=url, headers=headers, timeout=60)
            rsp.raise_for_status()
            return rsp.json()