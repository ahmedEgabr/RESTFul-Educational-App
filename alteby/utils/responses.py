
def error(error_key, **kwargs):
    return {
        'status': False,
        'message': 'error',
        'error_description': error_messages[error_key],
        **kwargs
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
    'incorrect_is_finished': 'is_finished value must be boolean.',
    'playlist_exists': 'Playlist with this name already exists.'
}

success_messages = {
    'quiz_answer_submitted': "Quiz answers has been recorded.",
    'enrolled': "Course Successfully Enrolled!",
    'account_deactivated': "Account Deactivated Successfully",
    'playlist_created': 'Playlist created successfully!',
    'added_to_playlist': "Successfully added.",
    'deleted': 'Successfully Deleted.'
}
