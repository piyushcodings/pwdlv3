from flask import Blueprint, request, jsonify
from beta.api.api_dl import download_pw_video
from beta.api.gen_utils import generate_random_word
from beta.api.mr_manager.boss_manager import Boss
from beta.api.gen_utils import generate_safe_folder_name


session_lodge = Blueprint('session_lodge', __name__)

client_manager = Boss.client_manager
task_manager = Boss.task_manager
OUT_DIR = Boss.OUT_DIR


@session_lodge.route('/api/client/<client_id>/<session_id>/create_session', methods=['POST'])
@session_lodge.route('/client/<client_id>/<session_id>/create_session', methods=['POST'])
def create_session(client_id, session_id):
    clients = client_manager.get_client_info(client_id)
    if not clients:
        client_manager.add_client(client_id)

    session = client_manager.get_client_info(client_id).get('sessions', {}).get(session_id)
    if not session:
        client_manager.add_session(client_id, session_id)
        sess_name = generate_random_word()
        print(f"Generated session name: {sess_name}")
        client_manager.set_session_name(client_id, session_id, sess_name)
    data = request.json
    ids = data.get('ids', [])
    names = data.get('names', [])


    if not ids or not names:
        return jsonify({'error': 'ids and names are required'}), 400

    if len(ids) != len(names):
        return jsonify({'error': 'ids and names must be of equal length'}), 400

    names_safe = [generate_safe_folder_name(name) for name in names]
    names = names_safe

    task_ids = []

    for i in range(len(ids)):
        id = ids[i]
        name = names[i]
        print(f"Creating task for {name} with id {id}")
        args = {
            'name': name,
            'id': id,
            'out_dir': OUT_DIR,
            'client_id': client_id,
            'session_id': session_id
        }
        task_id = task_manager.create_task(client_id, session_id, download_pw_video, args, inactive=True)
        task_ids.append(task_id)

    return jsonify({'task_ids': task_ids}), 202


@session_lodge.route('/api/start/<task_id>',methods=['GET','POST'])
@session_lodge.route('/start/<task_id>',methods=['GET','POST'])
def start_task(task_id):
    try:
        task_manager.start_task(task_id)
        return jsonify({'success': True}), 200
    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 500

@session_lodge.route('/api/client/<client_id>/delete_client')
@session_lodge.route('/client/<client_id>/delete_client')
def delete_client_route(client_id):
    client_manager.remove_client(client_id)
    return jsonify({'message': f'Client with ID {client_id} deleted successfully'}), 200

@session_lodge.route('/api/client/<client_id>/<session_id>/delete_session')
@session_lodge.route('/client/<client_id>/<session_id>/delete_session')
def delete_session_route(client_id, session_id):
    client_manager.remove_session(client_id, session_id)
    return jsonify({'message': f'Session with ID {session_id} for client {client_id} deleted successfully'}), 200

