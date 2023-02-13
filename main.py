import socket
import urllib
from urllib.parse import quote
from random import randint
import json

LOGIN_MESSAGE = "What is your name, Traveler?"

DIRECTIONS = ['north', 'south', 'east', 'west']

def match_command(txt):
    return lambda cmd: cmd['match'](txt)

def match_exactly(m):
    return lambda s: s == m

def match_by(key, val):
    return lambda x: x[key] == val

def match_one_of(list):
    return lambda s: s in list

def match_in(d, val):
    return lambda x: d[x] == val

def match_starting_with(str):
    return lambda s: s.startswith(str)
                      
def find_where(is_true, list):
    for item in list:
        if is_true(item):
            return item
    return None

def get_directions(room):
    dirs = []
    for d in DIRECTIONS:
        if room[d] != None:
            dirs.append(d)
    return dirs



world = {
    'users':[],
    'store':[],
    'rooms':[{'id':1, 'desc': 'Type load world', 'north':3, 'south':2, 'east':4, 'west':5}],
    'monsters':[],
    'items': []
    
}
  
def decode(start, end, str):
    start_index = str.find(start)
    if start_index > -1 and end == '':
        return str[start_index+len(start):].strip()
    if start_index > -1 and end != '':
        end_index = str.find(end, start_index)
        return str[start_index+len(start):end_index].strip()
    else:
        return ''

def http_response(headers, msg):
    return "HTTP/1.1 200 OK\r\n%s\r\n\r\n%s" %('\r\n'.join(headers), html_page(msg))

def html_page(msg):
    return """<!DOCTYPE html>
    <html>
        <head>
        </head>
            <body>
                <h1>%s</h1>
                <form method="POST">
                    <input name="txt" autofocus>
                </form>
                <h4> Type a command then press Enter </h4>
                <hr>
                <div style="display:inline-block; border:2px solid black;padding:5px;">
                    <u>Command List:</u><br>
                    <b>store</b>: purchase items<br>
                    <b>inv</b>: shows current inventory<br>
                    <b>look</b>: shows room description and available rooms<br>
                    <b>north</b>: moves you north...if available room exists<br>
                    <b>south</b>: moves you south...if available room exists<br>
                    <b>east</b>: moves you east...if available room exists<br>
                    <b>west</b>: moves you west...if available room exists<br>
                    <b>attack</b>: Type attack then the name of the monster in the room!<br>
                    <b>grab</b>: Type grab then the item's name in the room!<br>
                    <b>logout</b>: end game
                </div>
                    
            </body>
    </html> """ % (msg)
     
def store(txt, user):
    result = 'You are in the store and have %d shekels:<br>' % user['money']
    for item in world['store']:
        result += item['name']
        for a in item:
            if a != 'name':
                result += "  %s   %s " % (a, item[a])
        result += '<br>'
    choice = None
    while choice == None:
        
        name = yield result + 'What would you like to buy? (or q to quit)'
        if name == 'q':
            return
        choice = find_where(match_by('name', name), world['store'])
        if choice != None and choice['price'] > user['money']:
            result = "You cannot afford %s" % choice['name']
            choice = None
    user['money'] -= choice['price']
    user['inventory'].append(choice)
    world['store'].remove(choice)
    yield "You bought %s. You now have %d shekels" % (choice['name'], user['money'])


def new_user(username):
    user = {
        'name':username,
        'money':10,
        'inventory': [],
        'room_id': 1,
        'health':20,
        'message':'',
    }
    world['users'].append(user)
    txt = yield('Welcome %s!<br> Read the Command List below<br>' % username) 
    while txt != 'logout':
        match = find_where(match_command(txt), commands)
        if match is None:
            txt = yield "Hmm, I don't understand, %s" % txt
        else:
            gen = match['action'](txt,user)
            result = next(gen)
            while True:
                if 'logout' in user:
                    return
                txt = yield result
                try:
                    result = gen.send(txt)
                except StopIteration:
                    break
                
def inv(txt, user):
    result = 'Here is your inventory<br>'
    for item in user['inventory']:
        result += item['name'] + '<br>'
    yield result

def look(txt, user):
    room = find_where(match_by('id', user['room_id']),world['rooms'])
    result = 'You look around and see %s<br>' % room['desc']
    result += '<br> You can go %s ' % ', '.join(get_directions(room))
    for monster in filter(match_by('room_id', room['id']), world['monsters']):
        result += '<br>YOu see a %s<br>' % monster['name']
    for item in filter(match_by('room_id', room['id']), world['items']):
        result += '<br>You see a %s<br>' % item['name']
    yield result

def move(txt, user):
    if txt in DIRECTIONS:
        room = find_where(match_by('id', user['room_id']), world['rooms'])
        if txt in room and room[txt] != None:
            next_room = find_where(match_by('id', room[txt]), world['rooms'])
            if ('requires_key' in next_room and find_where(match_by('name', next_room['requires_key']),
user['inventory']) is None):
                yield "This door is locked. It requires a %s" % next_room['requires_key']
                return
            user['room_id'] = room[txt]
            if 'winner' in next_room:
                for u in world['users']:
                    if u['name'] != user['name']:
                        u['message'] = "Too Slow, %s has Won!!!<br><br>" % user['name']
                        u['logout'] = True
                yield "You Escaped!<br> %s is the WINNER!!!" % user['name']

            else:
                yield next(look(txt, user))
        else:
            yield "You cannot go %s!<br><br>" % txt

def attack(txt, user):
    name = txt[7:]
    result = ''
    monster = find_where(match_by('name', name), world['monsters'])
    if monster is None or monster['room_id'] != user['room_id']:
        yield "%s isn't here" % name
        return
    while monster['health'] > 0 and user['health'] > 0:
        result += 'Attacking the %s Health %d. Your health: %d<br><br>'%(monster['name'],
monster['health'], user['health'])
        result += "What weapon do you want to use?<br>"
        result += "fists<br>"
        for item in user['inventory']:
            result += item['name']
        weapon = None
        while weapon == None:
            name = yield result
            if find_where(match_by('name', monster['name']), world['monsters']) is None:
                user['message'] += "%s is already dead" % monster['name']
                return
            weapon = find_where(match_by('name', name), user['inventory'])
            if name == 'fists':
                weapon = {'name': 'fists', 'power': 1}
        dmg = randint(0, 4) + weapon['power']
        result += "<br>Your %s dealt %d damage to the %s<br>" % (weapon['name'], dmg, monster['name'])
        monster['health'] -= dmg
        if monster['health'] > 0:
            result += "The %s has %d health left.<br>" %(monster['name'], monster['health'])
            dmg = randint(0,4) + monster['attack']
            result += "The %s hit you for %d.<br>" %(monster['name'], dmg)
            user['health'] -= dmg
        if monster['health'] <= 0:
            result += "<br> The %s has fallen.<br><br>" % monster['name']
            reward = randint(1, monster['attack'] * 2)
            user['money'] += 5 + reward
            monster['health'] = monster['starting_health']
            result += 'You have %d shekels, and your health is now %s!<br>' % (user['money'],user['health'])
        if user['health'] <= 0:
            result += 'You have fallen'
        yield result

def grab(txt, user):
    name = txt[5:]
    item = find_where(match_by('name', name), world['items'])
    if item is None or item['room_id'] != user['room_id']:
        yield "%s isn't here" % name
        return
    user['inventory'].append(item)
    yield ("Picked up %s<br> Check your inventory!<br>" % name) + next(look(txt, user))

def opposite_direction(dir):
    if dir == 'north': return 'south'
    if dir == 'south': return 'north'
    if dir == 'east': return 'west'
    if dir == 'west': return 'east'

def create_room(txt, user):
    room = find_where(match_by('id', user['room_id']), world['rooms'])
    desc = ''
    while desc == '':
        desc = yield "Type a description"
    direction = ''
    while direction not in DIRECTIONS and direction != None:
        direction = yield "Type a direction (%s)" % ', '.join(filter(match_in(room, None), DIRECTIONS))
        if direction not in DIRECTIONS or room[direction] != None:
            direction = ''
    new_room = {
        'id': len(world['rooms']) + 1, 'desc': desc, 'north':None, 'south':None, 'east':None, 'west':None
    }
    world['rooms'].append(new_room)
    room[direction] = new_room['id']
    new_room[opposite_direction(direction)] = room['id']
    user['room_id'] = new_room['id']
    yield next(look(txt,user))

def save_world(txt, user):
    worldName = 'world.json'
    with open(worldName, 'w') as file:
        json.dump(world, file, indent=4)
    yield 'World saved!<br>You should now have a file named %s<br>' % worldName

def load_world(txt, user):
    worldName = 'world.json'
    global world
    with open(worldName, 'r') as file:
        world = json.load(file)
    user['room_id'] = 1
    user['inventory'] = []
    user['health'] = 20
    user['money'] = 10
    world['users'] = [user]
    yield "%s World loaded!<br><br>" % worldName + next(look(txt,user))
    
                                                             
commands = [
    {'match': match_exactly('store'), 'action': store},
    {'match': match_exactly('inv'), 'action': inv},
    {'match': match_exactly('look'), 'action':look},
    {'match': match_one_of(DIRECTIONS), 'action':move},
    {'match': match_starting_with('attack '), 'action':attack},
    {'match': match_starting_with('grab '), 'action':grab},
    {'match': match_exactly('create room'), 'action':create_room},
    {'match': match_exactly('save world'), 'action':save_world},
    {'match': match_exactly('load world'), 'action': load_world}
]

def start_server():
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    port = 12345
    print('Listening at http://localhost:%d' % port)
    s.bind(('', port))
    s.listen(5)

    clients = {}

    while True:
        c, addr = s.accept()
        print('Got connection from %s\n' % str(addr))
        request = c.recv(4096).decode()
        print(request)
        headers = []
        txt = urllib.parse.unquote_plus(decode('txt=', '', request))
        print(txt)

        username = decode('username=', '\r\n', request)

        if username == '' and txt =='':
            
            result = LOGIN_MESSAGE

        if username == '' and txt != '':
            
            username = txt

        if username != '':
            
            if username not in clients:
                clients[username] = new_user(username)
                headers = ['Set-Cookie: username=%s;' % username]
                result = next(clients[username])
            else:
                try:
                    result = clients[username].send(txt)
                except StopIteration:
                    del clients[username]
                    user = find_where(match_by('name', username), world['users'])
                    result = user['message'] + LOGIN_MESSAGE
                    headers = ['Set-Cookie: username=; expires=Thu, 01 Jan 1970 00:00:00 GMT;']
                
        output = http_response(headers, result)
        c.sendall(output.encode())
        c.close()

start_server()

