# Third-party
from celery import shared_task
from .models import Lecture, LectureQuality
from pathlib import Path

@shared_task
def detect_and_convert_lecture_qualities(lecture_id):
    try:
        lecture = Lecture.objects.get(id=lecture_id)
        if not lecture.video:
            return False

        original_quality = lecture.detect_original_video_quality()
        if not original_quality:
            return None

        supported_qualities = Lecture.get_supported_qualities(int(original_quality.quality))
        for quality in supported_qualities:
            quality = Lecture.scale_quality(quality)
            quality_attribute = getattr(LectureQuality.Qualities, f"_{quality}")
            if quality_attribute:
                video_name, converted = Lecture.convert_video_quality(video_path=lecture.video.path, quality=quality)
                if converted:
                    video_path = Path(lecture.video.name).parent.joinpath(video_name)
                    LectureQuality.objects.get_or_create(lecture=lecture, video=str(video_path), quality=quality_attribute)
    except:
        return None

@shared_task
def extract_and_set_lecture_audio(lecture_id):
    try:
        lecture = Lecture.objects.get(id=lecture_id)
        lecture.extract_and_set_audio()
    except:
       return None
