from ingestion_system.raw_session import RawSession
from ingestion_system.ingestion_system_configuration import IngestionSystemConfiguration


class FlowAnalysis:
    TARGET_SEQUENCE_LENGTH = 10

    def mark_missing_samples(self, session: RawSession, config: IngestionSystemConfiguration) -> bool:
        """
        Pads columns to the target length (10) using None for missing samples
        and checks if the original missing sample count exceeded the allowed threshold.
        Returns True if the original session was valid, False otherwise.
        """

        target_length = FlowAnalysis.TARGET_SEQUENCE_LENGTH

        # Group all session lists together. The padding value is uniformly None.
        columns_data = [
            session.timestamp,
            session.amount,
            session.source_ip,
            session.dest_ip,
            session.longitude,
            session.latitude
        ]

        for col_list in columns_data:
            actual_length = len(col_list)
            missing_count = target_length - actual_length

            # 1. Validation Check
            if missing_count > config.missing_samples_threshold:
                # We don't need the field name for the printout here, but we set the flag.
                print(
                    f"[FlowAnalysis] INVALID: Found {missing_count} missing samples (Threshold: {config.missing_samples_threshold})")
                return False

            # 2. Marking/Padding
            if actual_length < target_length:
                padding = [None] * missing_count
                col_list.extend(padding)

        return True