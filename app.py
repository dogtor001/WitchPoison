from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import eventlet

app = Flask(__name__)
app.config['SECRET_KEY'] = 'witch_secret'
socketio = SocketIO(app, async_mode='eventlet')

TOTAL_SNACKS = 20

game_state = {
    'snack_count': TOTAL_SNACKS,
    'eaten': [],
    'players': [],
    'player_roles': {},
    'poison_choices': {},
    'current_turn': 1,
    'game_over': False,
    'winner': None,
    'players_count': 0,
    'spectators': [],
    'spectators_count': 0
}

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    sid = request.sid

    # 清理断线重连旧 SID
    if sid in game_state['players']:
        game_state['players'].remove(sid)
    if sid in game_state['spectators']:
        game_state['spectators'].remove(sid)

    # 加入玩家或观战者
    if len(game_state['players']) < 2:
        game_state['players'].append(sid)
        game_state['players_count'] = len(game_state['players'])
        role = game_state['players_count']
        game_state['player_roles'][sid] = role
        emit('assign_role', {'role': role, 'message': f'你是P{role}，请设定毒药'}, room=sid)
        emit('prompt_set_poison', {}, room=sid)
    else:
        game_state['spectators'].append(sid)
        game_state['spectators_count'] = len(game_state['spectators'])
        emit('assign_role', {'role': 0, 'message': '你是观战者'}, room=sid)

    emit('update_state', game_state, broadcast=True)

@socketio.on('set_poison')
def handle_set_poison(data):
    sid = request.sid
    poison = data.get('poison')
    if not (1 <= poison <= TOTAL_SNACKS):
        emit('invalid_action', {'message': '毒药编号无效'}, room=sid)
        return

    game_state['poison_choices'][sid] = poison
    emit('info', {'message': f'你已设定毒药'}, room=sid)

    # 广播设毒状态给所有人
    role = game_state['player_roles'].get(sid, '?')
    emit('info', {'message': f'P{role} 已设定毒药'}, broadcast=True)

    # 若两人都设好了毒药，开始游戏
    if len(game_state['poison_choices']) == 2:
        emit('info', {'message': '双方毒药已设定，游戏即将开始...'}, broadcast=True)
        socketio.sleep(2)
        emit('game_start', {'message': '游戏开始！P1先手'}, broadcast=True)
        emit('update_state', game_state, broadcast=True)

@socketio.on('eat_snack')
def handle_eat_snack(data):
    sid = request.sid
    snack_id = data.get('snack')
    if game_state['game_over']:
        return
    if not (1 <= snack_id <= TOTAL_SNACKS):
        return
    if snack_id in game_state['eaten']:
        return

    player_num = game_state['player_roles'].get(sid)
    if player_num != game_state['current_turn']:
        emit('invalid_action', {'message': '还没轮到你'}, room=sid)
        return

    game_state['eaten'].append(snack_id)

    # 判断是否中毒
    for other_sid in game_state['players']:
        if other_sid != sid:
            if snack_id == game_state['poison_choices'].get(other_sid):
                game_state['game_over'] = True
                game_state['winner'] = game_state['player_roles'][other_sid]
                loser = player_num
                sid1, sid2 = game_state['players']
                poison1 = game_state['poison_choices'].get(sid1, '?')
                poison2 = game_state['poison_choices'].get(sid2, '?')
                # Add log entry for eating poison
                emit('log_entry', {
                    'text': f'P{loser} 吃到毒药 #{snack_id}！游戏结束。'
                }, broadcast=True)
                emit('game_over', {
                    'winner': game_state['winner'],
                    'loser': loser,
                    'poison1': poison1,
                    'poison2': poison2,
                    'eaten_poison_snack_id': snack_id # Pass the ID of the eaten poison
                }, broadcast=True)
                emit('update_state', game_state, broadcast=True)
                return

    # 平局判定
    if len(game_state['eaten']) >= TOTAL_SNACKS:
        game_state['game_over'] = True
        emit('game_over', {'winner': 0}, broadcast=True)
        return

    # 正常切换回合
    game_state['current_turn'] = 3 - game_state['current_turn']
    emit('snack_eaten', {
        'snack': snack_id,
        'by_player': player_num,
        'next_turn': game_state['current_turn']
    }, broadcast=True)
    emit('log_entry', {
        'text': f'P{player_num} 吃了 #{snack_id}'
    }, broadcast=True)
    emit('update_state', game_state, broadcast=True)

@socketio.on('reset_game')
def handle_reset():
    reset_game()
    emit('update_state', game_state, broadcast=True)
    emit('info', {'message': '游戏已重置，请重新设定毒药'}, broadcast=True)

    for sid in game_state['players']:
        role = game_state['player_roles'][sid]
        emit('assign_role', {'role': role, 'message': f'你是P{role}，请重新设定毒药'}, room=sid)
        emit('prompt_set_poison', {}, room=sid)
        emit('force_reset_poison', {}, room=sid)  # ✅ 通知前端清空毒药状态

@socketio.on('disconnect')
def handle_disconnect():
    sid = request.sid

    if sid in game_state['players']:
        game_state['players'].remove(sid)
        game_state['player_roles'].pop(sid, None)
        game_state['poison_choices'].pop(sid, None)
        game_state['players_count'] = len(game_state['players'])
        reset_game()
        emit('info', {'message': '有玩家退出，游戏重置'}, broadcast=True)
    elif sid in game_state['spectators']:
        game_state['spectators'].remove(sid)
        game_state['spectators_count'] = len(game_state['spectators'])

    emit('update_state', game_state, broadcast=True)

def reset_game():
    game_state['eaten'] = []
    game_state['poison_choices'] = {}
    game_state['current_turn'] = 1
    game_state['game_over'] = False
    game_state['winner'] = None

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)


