from ingestion_system.raw_session import RawSession


class DataCorrector:
    """Corrects RawSession data by handling missing samples and clipping absolute outliers."""
    def __init__(self, max_transactions_amount: float):
        self.max_transactions_amount = max_transactions_amount

    def correct_missing_samples(self, session: RawSession) -> RawSession:
        """Handle missing samples by filling None values with the most frequent value.

        If no non-None values are present in a sequence, None values are left
        unchanged.
        """

        def _fill_with_mode(values, ips=False):
            non_null = [v for v in values if v is not None]
            if not non_null:
                # All values are None: assign a default value (0.0) or "0.0.0.0" for IPs
                return ["0.0.0.0" if ips else 0.0 for _ in values]

            # compute most frequent value (mode)
            freq = {}
            for v in non_null:
                freq[v] = freq.get(v, 0) + 1
            mode_value = max(freq.items(), key=lambda item: item[1])[0]

            return [mode_value if v is None else v for v in values]

        if session.timestamp:
            session.timestamp = _fill_with_mode(session.timestamp)
        if session.amount:
            session.amount = _fill_with_mode(session.amount)
        if session.longitude:
            session.longitude = _fill_with_mode(session.longitude)
        if session.latitude:
            session.latitude = _fill_with_mode(session.latitude)
        if session.source_ip:
            session.source_ip = _fill_with_mode(session.source_ip, ips=True)
        if session.dest_ip:
            session.dest_ip = _fill_with_mode(session.dest_ip, ips=True)

        return session

    def correct_absolute_outiers(self, session: RawSession) -> RawSession:
        """Clip absolute outliers such as very large transaction amounts."""
        if session.amount:
            session.amount = [
                min(a, self.max_transactions_amount) if a is not None else None
                for a in session.amount
            ]

        return session
