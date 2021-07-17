def get_good_day_project_id():
    return {'goodDayProjectId': 1}


def receive_tasks(tasks, good_day_project_id):
    return {
        'goodDayProjectId': good_day_project_id,
        'tasks': tasks
    }
