
def error(error_key):
    return {
        'status': False,
        'message': 'error',
        'error_description': error_messages[error_key]
    }

def success(success_key):
    return {
        'status': True,
        'message': 'success',
        'success_description': success_messages[success_key]
    }

error_messages = {
    'internal_error': 'Internal Server Error.',
    'not_found': 'Not Found!',
    'access_denied': 'You don\'t have access to this resourse!, enroll this course to see its content.',
    'required_fields': 'Some fields are required.',
    'page_access_denied': 'You don\'t have access to preview this page.',
    'empty_quiz_answers': "Quiz answers cannot be empty.",
    'incorrect_left_off': 'Left off at value must be positive and numeric.',
    'incorrect_is_finished': 'is_finished value must be boolean.'
}

success_messages = {
    'quiz_answer_submitted': "Quiz answers has been recorded.",
    'enrolled': "Course Successfully Enrolled!"
}
