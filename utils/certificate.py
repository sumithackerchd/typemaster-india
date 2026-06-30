from datetime import datetime


def generate_certificate_id(result_id):

    today = datetime.now().strftime("%Y%m%d")

    return f"TMI-{today}-{result_id:06d}"