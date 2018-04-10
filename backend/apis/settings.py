from backend import app
from backend.model.resources import Setting

from flask import jsonify, request


@app.route('/admin/setting', methods=['POST'])
def setting():
    data = request.get_json()
    cpu = data['cpu']
    period = data['period']
    Setting.create_or_update('cpu', cpu)
    Setting.create_or_update('period', period)
    return 'success'


@app.route('/admin/setting', methods=['GET'])
def get_setting():
    cpu = Setting.query.filter_by(id='cpu').first()
    period = Setting.query.filter_by(id='period').first()
    return jsonify({'cpu': cpu.value, 'period': period.value})
