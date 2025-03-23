# app.py
from flask import Flask, render_template, request, redirect, url_for, jsonify, session
import os
import json

app = Flask(__name__)
app.secret_key = 'vampire_survivors_secret_key'

# Game data
CHARACTERS = {
    'antonio': {
        'name': 'Antonio',
        'description': 'The starting character.',
        'ability': 'Starts with a knife.',
        'stats': {'max_health': 100, 'recovery': 0, 'armor': 0, 'move_speed': 0, 'might': 0}
    },
    'imelda': {
        'name': 'Imelda',
        'description': 'The magic user.',
        'ability': 'Starts with a magic wand.',
        'stats': {'max_health': 90, 'recovery': 0, 'armor': 0, 'move_speed': 0, 'might': 0}
    },
    'pasqualina': {
        'name': 'Pasqualina Belpaese',
        'description': 'Projectiles get 10% faster every 5 levels (max +30%).',
        'ability': 'Projectiles get faster.',
        'stats': {'max_health': 95, 'recovery': 0, 'armor': 0, 'move_speed': 0, 'might': '+10% per 5 levels'}
    },
    'gennaro': {
        'name': 'Gennaro',
        'description': 'The tank character.',
        'ability': 'Extra armor.',
        'stats': {'max_health': 120, 'recovery': 0, 'armor': 1, 'move_speed': -1, 'might': 0}
    }
}

STAGES = {
    'mad_forest': {
        'name': 'Mad Forest',
        'description': 'Once a thriving haven, now a dumping ground for evil. A vampire is said to be the root of this evil, but we can find only mayhem and roast chicken.',
        'unlocked': True,
        'enemies': ['bat', 'skeleton', 'zombie'],
        'time_limit': '30:00'
    },
    'library': {
        'name': '???',
        'description': 'Not yet discovered.',
        'unlocked': False,
        'enemies': ['ghost', 'book', 'mummy'],
        'time_limit': '30:00'
    },
    'dairy_plant': {
        'name': '???',
        'description': 'Not yet discovered.',
        'unlocked': False,
        'enemies': ['slime', 'minotaur', 'butcher'],
        'time_limit': '30:00'
    },
    'gallo_tower': {
        'name': '???',
        'description': 'Not yet discovered.',
        'unlocked': False,
        'enemies': ['bat', 'ghost', 'reaper'],
        'time_limit': '30:00'
    },
    'flower_garden': {
        'name': '???',
        'description': 'Not yet discovered.',
        'unlocked': False,
        'enemies': ['plant', 'bee', 'butterfly'],
        'time_limit': '30:00'
    }
}

POWERUPS = {
    'might': {
        'name': 'Might',
        'description': 'Raises inflicted Damage by 5% per rank (max +25%).',
        'max_level': 5,
        'cost': 200
    },
    'armor': {
        'name': 'Armor',
        'description': 'Reduces damage taken by 3% per rank.',
        'max_level': 3,
        'cost': 300
    },
    'max_health': {
        'name': 'Max Health',
        'description': 'Increases max health by 10% per rank.',
        'max_level': 3,
        'cost': 300
    },
    'recovery': {
        'name': 'Recovery',
        'description': 'Increases health regeneration.',
        'max_level': 3,
        'cost': 300
    },
    'cooldown': {
        'name': 'Cooldown',
        'description': 'Reduces weapon cooldown.',
        'max_level': 2,
        'cost': 400
    },
    'area': {
        'name': 'Area',
        'description': 'Increases attack area by 10% per rank.',
        'max_level': 2,
        'cost': 400
    },
    'speed': {
        'name': 'Speed',
        'description': 'Increases projectile speed.',
        'max_level': 2,
        'cost': 400
    },
    'duration': {
        'name': 'Duration',
        'description': 'Increases weapon duration.',
        'max_level': 2,
        'cost': 400
    },
    'amount': {
        'name': 'Amount',
        'description': 'Increases projectile amount.',
        'max_level': 1,
        'cost': 500
    },
    'move_speed': {
        'name': 'Move Speed',
        'description': 'Increases character movement speed.',
        'max_level': 2,
        'cost': 400
    },
    'magnet': {
        'name': 'Magnet',
        'description': 'Increases pickup range.',
        'max_level': 2,
        'cost': 400
    },
    'luck': {
        'name': 'Luck',
        'description': 'Increases item drop chance.',
        'max_level': 3,
        'cost': 300
    },
    'growth': {
        'name': 'Growth',
        'description': 'Increases XP gain by 10% per rank.',
        'max_level': 5,
        'cost': 200
    },
    'greed': {
        'name': 'Greed',
        'description': 'Increases gold gain by 10% per rank.',
        'max_level': 5,
        'cost': 200
    },
    'curse': {
        'name': 'Curse',
        'description': 'Increases enemy quantity and speed.',
        'max_level': 5,
        'cost': 200
    },
    'revival': {
        'name': 'Revival',
        'description': 'Gives an extra life.',
        'max_level': 1,
        'cost': 1000
    }
}

WEAPONS = {
    'whip': {
        'name': 'Whip',
        'description': 'Attacks horizontally, passes through enemies.',
        'ignores': ['Speed', 'Duration'],
        'unlocked': True
    },
    'magic_wand': {
        'name': 'Magic Wand',
        'description': 'Shoots at the nearest enemy.',
        'ignores': ['Duration'],
        'unlocked': False
    },
    'knife': {
        'name': 'Knife',
        'description': 'Travels ahead quickly.',
        'ignores': ['Duration'],
        'unlocked': True
    },
    'axe': {
        'name': 'Axe',
        'description': 'Travels in an arc, passes through enemies.',
        'ignores': ['Duration'],
        'unlocked': True
    },
    'cross': {
        'name': 'Cross',
        'description': 'Returns after being thrown.',
        'ignores': ['Speed'],
        'unlocked': True
    },
    'holy_water': {
        'name': 'Holy Water',
        'description': 'Creates damaging puddles.',
        'ignores': ['Amount', 'Speed'],
        'unlocked': True
    },
    'diamond': {
        'name': 'Diamond',
        'description': 'Passes through enemies and bounces.',
        'ignores': ['Speed'],
        'unlocked': True
    },
    'garlic': {
        'name': 'Garlic',
        'description': 'Damages enemies that get too close.',
        'ignores': ['Amount', 'Speed', 'Duration'],
        'unlocked': False
    }
}

def init_user_data():
    """Initialize user data if not present in session"""
    if 'user_data' not in session:
        session['user_data'] = {
            'gems': 79,  # Starting gems from the screenshots
            'collected_weapons': ['whip', 'knife', 'diamond', 'cross', 'holy_water', 'axe'],
            'collected_count': 11,  # From the collection screen in the images
            'total_collectibles': 145,
            'unlocked_characters': ['antonio', 'imelda', 'pasqualina', 'gennaro'],
            'selected_character': 'pasqualina',
            'powerups': {name: 0 for name in POWERUPS},
            'unlocked_stages': ['mad_forest']
        }
    return session['user_data']

@app.route('/')
def home():
    """Main menu screen"""
    user_data = init_user_data()
    version = "v1.12.10"
    return render_template('index.html', user_data=user_data, version=version)

@app.route('/character_selection')
def character_selection():
    """Character selection screen"""
    user_data = init_user_data()
    return render_template('character_selection.html', 
                          user_data=user_data, 
                          characters=CHARACTERS)

@app.route('/select_character', methods=['POST'])
def select_character():
    """Handle character selection"""
    user_data = init_user_data()
    character_id = request.form.get('character_id')
    if character_id in CHARACTERS and character_id in user_data['unlocked_characters']:
        user_data['selected_character'] = character_id
        session['user_data'] = user_data
    return redirect(url_for('character_selection'))

@app.route('/powerup')
def powerup():
    """Powerup selection screen"""
    user_data = init_user_data()
    return render_template('powerup.html', 
                          user_data=user_data, 
                          powerups=POWERUPS)

@app.route('/buy_powerup', methods=['POST'])
def buy_powerup():
    """Handle purchasing powerups"""
    user_data = init_user_data()
    powerup_id = request.form.get('powerup_id')
    
    if powerup_id in POWERUPS:
        powerup = POWERUPS[powerup_id]
        current_level = user_data['powerups'][powerup_id]
        
        if current_level < powerup['max_level'] and user_data['gems'] >= powerup['cost']:
            user_data['gems'] -= powerup['cost']
            user_data['powerups'][powerup_id] += 1
            session['user_data'] = user_data
            return jsonify({'success': True})
    
    return jsonify({'success': False})

@app.route('/refund_powerups', methods=['POST'])
def refund_powerups():
    """Handle refunding all powerups"""
    user_data = init_user_data()
    refund_amount = 0
    
    for powerup_id, level in user_data['powerups'].items():
        if level > 0:
            refund_amount += POWERUPS[powerup_id]['cost'] * level
            user_data['powerups'][powerup_id] = 0
    
    user_data['gems'] += refund_amount
    session['user_data'] = user_data
    return redirect(url_for('powerup'))

@app.route('/collection')
def collection():
    """Collection screen showing unlocked weapons and items"""
    user_data = init_user_data()
    return render_template('collection.html', 
                          user_data=user_data, 
                          weapons=WEAPONS)

@app.route('/stage_selection')
def stage_selection():
    """Stage selection screen"""
    user_data = init_user_data()
    return render_template('stage_selection.html', 
                          user_data=user_data, 
                          stages=STAGES)

@app.route('/select_stage', methods=['POST'])
def select_stage():
    """Handle stage selection"""
    user_data = init_user_data()
    stage_id = request.form.get('stage_id')
    
    if stage_id in STAGES and stage_id in user_data['unlocked_stages']:
        # Start the game with the selected stage
        return redirect(url_for('game', stage_id=stage_id))
    
    return redirect(url_for('stage_selection'))

@app.route('/game/<stage_id>')
def game(stage_id):
    """Gameplay screen"""
    user_data = init_user_data()
    if stage_id not in STAGES or stage_id not in user_data['unlocked_stages']:
        return redirect(url_for('stage_selection'))
    
    character = CHARACTERS[user_data['selected_character']]
    stage = STAGES[stage_id]
    
    return render_template('game.html', 
                          user_data=user_data,
                          character=character,
                          stage=stage)

@app.route('/enter_coop')
def enter_coop():
    """Enter co-op mode"""
    # Placeholder for co-op functionality
    return redirect(url_for('home'))

@app.route('/credits')
def credits():
    """Credits screen"""
    return render_template('credits.html')

@app.route('/options')
def options():
    """Options screen"""
    return render_template('options.html')

if __name__ == '__main__':
    app.run(debug=True)

