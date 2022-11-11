from datetime import datetime

def get_question_path(instance, filename):
    today = datetime.today().strftime("%d-%m-%Y")

    return 'questions/{0}/{1}'.format(
    today,
    filename
    )
