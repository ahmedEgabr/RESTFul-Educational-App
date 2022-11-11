from datetime import datetime

def get_choice_path(instance, filename):
    today = datetime.today().strftime("%d-%m-%Y")

    return 'choices/{0}/{1}'.format(
    today,
    filename
    )
