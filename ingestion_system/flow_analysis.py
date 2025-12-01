from ingestion_system.raw_session import RawSession


class FlowAnalysis:
    TARGET_SEQUENCE_LENGTH = 10

    @staticmethod
    def mark_missing_samples(session: RawSession, config: dict) -> bool:
        """
        Calculates the TOTAL missing samples across all columns.
        If the total is within the threshold, pads columns to the target length (10).
        Returns True if the session was valid and padded, False otherwise.
        """

        target_length = FlowAnalysis.TARGET_SEQUENCE_LENGTH

        # Group all session lists together by reference
        columns_data = [
            session.timestamp,
            session.amount,
            session.source_ip,
            session.dest_ip,
            session.longitude,
            session.latitude
        ]

        # 1. Calculate Total Missing Count (Accumulation Phase)
        total_missing_count = 0
        for col_list in columns_data:
            total_missing_count += max(0, target_length - len(col_list))

        missing_samples_threshold = config["missingSamplesThreshold"]

        # 2. Validation Check (Aggregate Phase)
        if total_missing_count > missing_samples_threshold * target_length * len(columns_data):
            print(
                f"[FlowAnalysis] INVALID: Found {total_missing_count} total missing samples across all columns "
                f"(Threshold: {missing_samples_threshold})"
            )
            return False

        for col_list in columns_data:
            missing_in_col = max(0, target_length - len(col_list))

            if missing_in_col > 0:
                padding = [None] * missing_in_col
                col_list.extend(padding)

        return True
