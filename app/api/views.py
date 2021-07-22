from flask import jsonify, request
import asana

from fields_mapping import get_asana_to_goodday_mapping
from . import api
from .oauth import asana_client
from ..models import Credential


@api.route('/import/asana/workspaces/<user_id>', methods=['POST'])
def import_workspaces(user_id):
    credential = Credential.query.filter_by(userId=user_id).first()
    token = credential.credentials
    client = asana_client(token=token)
    workspaces = client.session.get_project_workspaces()
    if workspaces:
        return jsonify({
            'Status': 'OK',
            'workspaces': workspaces
        })
    else:
        return jsonify({'Status': 'error'})


@api.route('/import/asana/projects/<user_id>', methods=['POST'])
def import_projects(user_id):
    data = request.json
    credential = Credential.query.filter_by(userId=user_id).first()
    token = credential.credentials
    client = asana_client(token=token)
    workspace_id = data['asanaWorkspaceId']
    asana_projects = [x for x in client.projects.find_by_workspace(workspace_id)]
    if asana_projects:
        return jsonify({
            'status': 'OK',
            'projects': asana_projects,
        })
    else:
        return jsonify({
            'status': 'error',
        })


@api.route('/import/asana/<user_id>/project/<project_id>/tasks')
def import_tasks(user_id, project_id):
    credential = Credential.query.filter_by(userId=user_id).first()
    token = credential.credentials
    client = asana_client(token=token)
    tasks = get_project_tasks(client, project_id)
    goodday_tasks = tasks_to_goodday(tasks)
    if tasks:
        return jsonify({
            'Status': 'OK',
            'tasks': goodday_tasks
        })
    else:
        return jsonify({'Status': 'error'})



def tasks_to_goodday(tasks):
    goodday_tasks = []
    asana_to_goodday = get_asana_to_goodday_mapping()
    for task in tasks:
        gday_task = {asana_to_goodday.get(k, k): v for k, v in task.items()}
        goodday_tasks.append(gday_task)
    for task in goodday_tasks:
        if task.get('createdForUserId'):
            task['createdForUserId'] = task['createdForUserId'].get('gid')
        if task.get('tags'):
            task['tags'] = [tag.get('gid') for tag in task['tags']]
        if task.get('projectId'):
            task['projectId'] = task['projectId'][0]['gid']
        if task.get('parentTaskId'):
            task['parentTaskId'] = task['parentTaskId'].get('gid')
    return goodday_tasks


def get_project_tasks(client, project_id):
    fields = ['notes', 'name', 'due_at', 'created_at', 'num_subtasks', 'start_at', 'assignee.gid',
              'custom_fields', 'permalink_url', 'tags.gid', 'projects.gid', 'parent', 'approval_status',
              ]
    tasks = [x for x in client.tasks.get_tasks(project=project_id, fields=fields)]
    subtasks = []
    for task in tasks:
        if task['num_subtasks'] > 0:
            subtasks.append(*[x for x in client.tasks.get_subtasks_for_task(task['gid'], fields=fields)])
    tasks = tasks + subtasks
    return tasks
