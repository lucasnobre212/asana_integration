from flask import jsonify, request

import asana
from . import api
from .oauth import asana_client, update_token
from ..models import User


def get_tasks_gid(project_id: str, client: asana.Client):
    return [x['gid'] for x in client.tasks.get_tasks(project=project_id)]


# TODO: Create asana import workspaces

@api.route('/asana/import/tasks/<int:user_id>', methods=['POST'])
def import_asana_task(user_id):
    data = request.json
    user = User.query.filter_by(user_id=user_id).first()
    token = user.get_token()
    client = asana_client(token=token)
    client = update_token(client, user)
    project_id = data['asanaProjectId']
    tasks = get_project_tasks(client, project_id)
    if tasks:
        return jsonify({
            'Status': 'OK',
            'tasks': tasks
        })
    else:
        return jsonify({'Status': 'error'})


def get_project_tasks(client, project_id):
    tasks_gid = get_tasks_gid(project_id, client)
    tasks = [client.tasks.get_task(gid) for gid in tasks_gid]
    return tasks


@api.route('/asana/import/projects/<int:user_id>', methods=['POST'])
def import_multiple_projects(user_id):
    data = request.json
    user = User.query.filter_by(user_id=user_id).first()
    token = user.get_token()
    client = asana_client(token=token)
    client = update_token(client, user)
    workspace_id = data['asanaWorkspaceId']
    asana_projects_ids = [x['gid'] for x in client.projects.find_by_workspace(workspace_id)]
    projects_dict = {}
    failed_imports = []
    for project_id in asana_projects_ids:
        tasks = get_project_tasks(client, project_id)
        if tasks:
            projects_dict[project_id] = tasks
        else:
            failed_imports.append(project_id)
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
