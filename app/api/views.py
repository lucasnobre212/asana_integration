from flask import jsonify, request

import asana
from . import api
from app.api.good_day_mock import get_good_day_project_id, receive_tasks
from .oauth import asana_client
from ..models import User


def get_tasks(project_id: str, client: asana.Client):

    return ''


@api.route('/asana/import/tasks/<int:user_id>', methods=['POST'])
def import_asana_task(user_id):
    data = request.json
    user = User.query.filter_by(user_id=user_id).first()
    token = ''
    client = asana_client(token=token)
    project_id = data['asanaProjectId']
    good_day_project_id = get_good_day_project_id()
    tasks = get_tasks(project_id, client)
    if tasks:
        return jsonify({
            'Status': 'OK',
            'goodday': receive_tasks(tasks, good_day_project_id)
        })
    else:
        return jsonify({'Status': 'error'})



@api.route('/import/projects/<int:user_id>', methods=['POST'])
def import_multiple_projects(user_id):
    data = request.json
    token = User.query.filter_by(user_id=user_id).first().token
    asana_projects_ids = data['asanaProjectIds']
    if not isinstance(asana_projects_ids, list):
        return jsonify({
            'status': 'error',
            'info': 'asanaProjectIds is not a list'
        })
    projects_dict = {}
    failed_imports = []
    for project in asana_projects_ids:
        tasks = get_tasks(project, token)
        if tasks:
            projects_dict[project] = tasks
        else:
            failed_imports.append(project)
    if projects_dict:
        return jsonify({
            'status': 'OK',
            'projects': projects_dict,
            'failed_imports': failed_imports,
        })
    else:
        return jsonify({
            'status': 'error',
        })
