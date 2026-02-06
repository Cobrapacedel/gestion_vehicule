from tolls.models import TollDetection
from tolls.services.toll_processing_service import process_toll_detection

def register_toll_detection(plate_number, booth):
    detection = TollDetection.objects.create(
        plate_number=plate_number,
        booth=booth
    )

    try:
        process_toll_detection(detection)
    except Exception:
        # log / notification / traitement différé
        pass

    return detection