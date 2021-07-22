from flask import jsonify, request
from asana.error import AsanaError

from fields_mapping import get_asana_to_goodday_mapping
from . import api
from .oauth import asana_client
from ..models import Credential


@api.route('/import/asana/<user_id>/workspaces')
def import_workspaces(user_id):
    credential = Credential.query.filter_by(userId=user_id).first()
    token = credential.credentials
    client = asana_client(token=token)
    try:
        workspaces = [x for x in client.workspaces.get_workspaces()]
        if workspaces:
            return jsonify({
                'Status': 'OK',
                'workspaces': workspaces
            })
        else:
            return jsonify({'Status': 'error'})
    except AsanaError as e:
        print(e)
        return jsonify({
            'Status': 'error'
        })



@api.route('/import/asana/<user_id>/workspace/<workspace_id>/projects')
def import_projects(user_id, workspace_id):
    credential = Credential.query.filter_by(userId=user_id).first()
    token = credential.credentials
    client = asana_client(token=token)
    asana_projects = [x for x in client.projects.find_by_workspace(workspace_id)]
    try:
        if asana_projects:
            return jsonify({
                'status': 'OK',
                'projects': asana_projects,
            })
        else:
            return jsonify({
                'status': 'error',
            })
    except AsanaError as e:
        print(e)
        return jsonify({
            'Status': 'error'
        })


@api.route('/import/asana/<user_id>/project/<project_id>/tasks')
def import_tasks(user_id, project_id):
    credential = Credential.query.filter_by(userId=user_id).first()
    token = credential.credentials
    client = asana_client(token=token)
    try:
        tasks = get_project_tasks(client, project_id)
        goodday_tasks = tasks_to_goodday(tasks)
        if tasks:
            return jsonify({
                'Status': 'OK',
                'tasks': goodday_tasks
            })
        else:
            return jsonify({'Status': 'error'})
    except AsanaError as e:
        print(e)
        return jsonify({
            'Status': 'error'
        })


def tasks_to_goodday(tasks):
    goodday_tasks = []
    asana_to_goodday = get_asana_to_goodday_mapping()
    for task in tasks:
        gday_task = {asana_to_goodday.get(k, k): v for k, v in task.items()}
        goodday_tasks.append(gday_task)
    # Some information has to be retrieved from inside a dict
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
