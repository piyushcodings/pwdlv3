import os.path

from flask import Blueprint, request, jsonify, send_file
from beta.api.mr_manager.boss_manager import Boss
from mainLogic.utils.os2 import SysFunc

client_manager = Boss.client_manager
task_manager = Boss.task_manager

admin = Blueprint('admin', __name__)

@admin.route('/api/webdl')
@admin.route('/webdl')
def webdl():
    return jsonify(SysFunc.list_files_and_folders(Boss.OUT_DIR)), 200

@admin.route('/api/webdl/webdl')
@admin.route('/webdl/webdl')
def webdl_copy():
    return webdl()

@admin.route('/api/webdl/<path:subpath>')
@admin.route('/webdl/<path:subpath>')
def webdl_subpath(subpath):
    return jsonify(SysFunc.list_files_and_folders(os.path.join(Boss.OUT_DIR, subpath))), 200

@admin.route('/api/delete/<path:subpath>')
@admin.route('/delete/<path:subpath>')
def delete_subpath(subpath):
    path_file_or_folder = os.path.join(Boss.OUT_DIR, subpath)

    if os.path.exists(path_file_or_folder):
        try:
            SysFunc.delete_file_or_folder(path_file_or_folder)
            return jsonify({'success': f'{subpath} deleted'}), 200
        except Exception as e:
            return jsonify({'error': f"Could not delete {e}"}), 404
    else:
        return jsonify({'error': 'file not found'}), 404

@admin.route('/api/get/<path:subpath>')
@admin.route('/get/<path:subpath>')
def get_subpath(subpath):
    path_to_file = os.path.join(Boss.OUT_DIR, subpath)
    if os.path.exists(path_to_file):
        return send_file(path_to_file, as_attachment=True, download_name=os.path.basename(path_to_file))
    else:
        return jsonify({'error': 'file not found'}), 404

@admin.route('/api/server/usages')
@admin.route('/server/usages')
def get_usages_for_all_client():
    usages = {}
    # will store usage in form of {client_id: size}

    for client_id in client_manager.clients:
        usages[client_id] = int(SysFunc.get_size_in_mB(os.path.join(Boss.OUT_DIR, client_id)))

    return jsonify(usages), 200

@admin.route('/api/server/update',methods=['GET','POST'])
@admin.route('/server/update',methods=['GET','POST'])
def update_server():
    from updater import check_for_updates, pull
    if request.method == 'POST':
        try:
            if check_for_updates():
                code, out = pull()
                if code == 0:
                    return jsonify({'message': 'Please restart the script.'}), 200
                else:
                    return jsonify({'error': 'Error occurred while pulling the latest changes. Exiting...'}), 500
            else:
                return jsonify({'message': 'No updates found.'}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    try:
        update = check_for_updates()
        return jsonify({'update': update}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

