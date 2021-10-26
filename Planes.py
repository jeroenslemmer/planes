import pygame # install in terminal with: pip install pygame
import sys
from SpriteSheet import SpriteSheet

# Plane Class #############################################################
#
#   An object of this class...
#
#   lets you create a plane with an maze of tiles, a player and a treasure
#   the tiles of the plane, the player and the treasure depend on the level
#   lets you program the movement of the hero over tiles through the maze
#   lets you scan the directions in which the hero can pass to other tiles
#
#   uses four directions for movements:
#     0 = Directions.up
#     1 = Directions.right
#     2 = Directions.down
#     3 = Directions.left
#
# ######## methods for public use:
#   moveForward() 
#     moves the player forward if possible
#     returns True if succeeded
#
#   turnLeft()
#     turns the player to the left
#
#   turnRight()
#     turns the player to the right
#
#   canPass(direction)
#     returns True if the player can move one tile in the given direction
#
#   wait(operator)
#       waits for the the program window to be closed
#       operator is an optional function with a parameter: events {list of events}
#       the operator must/can handle each event in events
#
#   operate()
#       make the player move on keyboard-keys: UP, RIGHT, DOWN and LEFT
#
# ######## properties to inspect
#   playerPosition is the X and Y position on the plane: [X,Y]
#   playerOrientation is the direction in which the player is turned
#   goalReached is True if the player has reached the treasure
#   version is the version of the current software of planes.py. 
#
# ######## properties to set
#   speed is animation speed: 1 to 10 where 1 = slow, 10 = fast
#
# ######## creating and loading levels ########
#   
#   loadLevel(levelName)
#     loads a predefined level for levelName {string}
#     returns True if succeeded, returns False if failed
#     
#   loadMyLevel(plane) 
#     loads a self made plane 
#     where plane is a list of properties of the plane
#     returns True if succeeded, returns False if failed
#
#############################################################################

class Directions:
  up = 0
  right = 1
  down = 2
  left = 3

class Plane:
  version = '0.0.1'
  # directions in Plane: 0 = up, 1 = right, 2 = down, 3 = left
  _defaultLevels = [
    { 'name': 'level 1', 
      'tileTypes': [
        {}, # rock
        {'openIn': [0,1,2,3], 'openOut': [0,1,2,3] }, # plain
        {'openIn': [1,2,3],'openOut': [1,2,3]}, #
        {'openIn': [2,3],'openOut': [2,3]},
        {'openIn': [3],'openOut': [3]},
        {'openIn': [1,3],'openOut': [1,3]}
      ],
      'tileImages': 'tiles01.png',
      'tiles': [[0,    0,    0,    0,    0,    0], # tilenumber or [tilenumber, turned]
                [0,[4,2],    5,    5,    3,    0],
                [0,[3,3],    5,    5,[3,1],    0],
                [0,[3,2],    5,    5,    3,    0],
                [0,[3,3],    5,    5,[3,1],    0],
                [0,[3,2],    5,    5,    4,    0],
                [0,0,0,0,0,0]],
      'player': {'img': 'sprite01.png', 'position': [1,1], 'orientation': 2}, 
      'goal': {'img':'treasure.png', 'position': [4,5]},
      'collision': {'img':'collision.png'}
    }
  ]
  tileSize = 64
  level = None
  objects = []
  _speeds = [1,2,3,4,5,6,7,8,9,10]
  speed = 1
  _levelName = 'Unknown level'
  _collision = None
  _backgroundColor = (0,0,0)
  _eventSleepTime = 300
  _eventActiveCycles = 100
  _idleAnimationTime = 300

  def __init__(self, levelName = ''):
    pygame.init()
    self._clock = pygame.time.Clock()
    self.loadLevel(levelName)

  def _drawPlane(self):
    self._screen.fill(self._backgroundColor)
    rownr = 0
    for row in self.level['tiles']:
      y = rownr * self.tileSize
      colnr =  0
      for tile in row:
        tile = self._completeTile(tile)
        x = colnr * self.tileSize
        image = self.tileImages[tile[0]][0]
        image = pygame.transform.rotate(image, -90 * tile[1])
        self._screen.blit(image,(x,y))
        colnr += 1
        pass
      rownr += 1

  def _drawCollision(self):
    if not self._collision == None:
      self._screen.blit(self.collisionImages[self._collision['state']],(self._collision['position'][0],self._collision['position'][1]))

  def _drawPlayer(self, playerXY):
    self._screen.blit(self.playerStateImages[self.playerState[0]][self.playerState[1]],(playerXY[0],playerXY[1]))

  def _drawGoal(self):
    x = self.level['goal']['position'][0] * self.tileSize
    y = self.level['goal']['position'][1] * self.tileSize
    self._screen.blit(self.goalImages[0],(x,y))

  def _playerXY(self, position):
    x = position[0] * self.tileSize
    y = position[1] * self.tileSize
    return [x,y]

  def _drawState(self, playerXY):
    pygame.display.set_caption('Planes: ' + self._levelName)
    self._drawPlane()
    self._drawGoal()
    self._drawPlayer(playerXY)
    self._drawCollision()
    pygame.display.update()

  def _animateMove(self, *args):
    # should be non-blocking for input
    if int(self.speed) not in self._speeds:
      self.speed = 1
    playerXY = self._playerXY(self.playerPosition)
    if args[0] == 'left':
      activity = 4 + args[1]
      self.playerState = [activity, len(self.playerStateImages[activity]) - 1] 
    elif args[0] == 'right':
      activity = 4 + self.playerOrientation
      self.playerState = [activity, 0]
    elif (args[0] == 'forward'):
      activity = self.playerOrientation
      self.playerState = [activity, 0]
      targetXY = self._playerXY(args[1])
      arrived = False
    elif (args[0] == 'blocked'):
      activity =  self.playerOrientation
      self.playerState = [activity, 0]
      state = 0 
 
    ready = False
    while not ready:
      if (args[0] == 'idle'):
        ready = True
      elif (args[0] == 'left'):
        ready = self.playerState[1] == 0
      elif (args[0] == 'right'):
        ready = self.playerState[1] == len(self.playerStateImages[self.playerState[0]]) - 1
      elif (args[0] == 'forward'):
        arrived = (playerXY[0] == targetXY[0]) and (playerXY[1] == targetXY[1])
        ready = arrived  and (self.playerState[1] == 0)
      elif (args[0] == 'blocked'):
        if state == 0:
          state = 1
          steps = 0
        elif state == 1:
          if steps == 4:
            state = 2
            self._collision = {'position': [playerXY[0],playerXY[1]], 'state': 0}
            steps = 0
        elif state == 2:
          self._collision['state'] += 1
          if self._collision['state'] == 4:
            self._collision = None
          if steps == 4:
            state = 3
            steps = 0
        elif state == 3:
          if self.playerState[1] == 0:
            state == 3
            ready = True

      for event in pygame.event.get():
        self.checkCloseEvent(event)
      self._drawState(playerXY)
      pygame.display.update()
      if not ready:
        self._clock.tick(5 * self.speed)

      if (args[0] == 'left'):
        self.playerState[1] -= 1
      elif (args[0] == 'right'):
        self.playerState[1] += 1
      elif (args[0] == 'idle'):
        pygame.time.delay(self._idleAnimationTime)
      elif (args[0] == 'forward'):
        self.playerState[1] = (self.playerState[1] + 1) % 4
        if not arrived:
          if self.playerOrientation == 0:
            playerXY[1] -= 8
          elif self.playerOrientation == 1:
            playerXY[0] += 8
          elif self.playerOrientation == 2:
            playerXY[1] += 8
          elif self.playerOrientation == 3:
            playerXY[0] -= 8
      elif (args[0] == 'blocked'):
        self.playerState[1] = (self.playerState[1] + 1) % 4
        if state == 1:
          steps += 1
          if self.playerOrientation == 0:
            playerXY[1] -= 8
          elif self.playerOrientation == 1:
            playerXY[0] += 8
          elif self.playerOrientation == 2:
            playerXY[1] += 8
          elif self.playerOrientation == 3:
            playerXY[0] -= 8
        elif state == 2:
          steps += 1
          if self.playerOrientation == 0:
            playerXY[1] += 8
          elif self.playerOrientation == 1:
            playerXY[0] -= 8
          elif self.playerOrientation == 2:
            playerXY[1] -= 8
          elif self.playerOrientation == 3:
            playerXY[0] += 8

  def _initDisplay(self):
    tilesWidth = 0
    for row in self.level['tiles']:
      if len(row) > tilesWidth:
        tilesWidth = len(row)
    self.screenWidth = tilesWidth * self.tileSize
    self.screenHeight = len(self.level['tiles']) * self.tileSize
    self._screen = pygame.display.set_mode((self.screenWidth, self.screenHeight))
    self._screen.fill(self._backgroundColor)
    
    self.tileImages = []
    ss = SpriteSheet(self.level['tileImages'])
    for tile in range(len(self.level['tileTypes'])):
      y = tile * self.tileSize
      self.tileImages.append(ss.load_strip((0,y,64,64), 1, (0,0,0)))

    ss = SpriteSheet(self.level['player']['img'])
    self.playerStateImages = []
    for state in range(12):
      y = state * self.tileSize
      self.playerStateImages.append(ss.load_strip((0,y,64,64), 4, (0,0,0)))

    self.playerOrientation = self.level['player']['orientation']
    self.playerPosition = self.level['player']['position']
    self.playerState = [self.level['player']['orientation'],0] # walking, standing

    ss = SpriteSheet(self.level['goal']['img'])
    self.goalImages = ss.load_strip((0,0,64,64), 1, (0,0,0))
    self.goalReached = False

    ss = SpriteSheet(self.level['collision']['img'])
    self.collisionImages = ss.load_strip((0,0,64,64), 4, (0,0,0))

  def loadMyLevel(self, level):
    if self.level != None:
      return False
    self.level = level
    self._initDisplay()
    self._animateMove('idle')
    return True

  def loadLevel(self, levelName):
    success = False
    for level in self._defaultLevels:
      if levelName == level['name']:
        levelToLoad = level
        success = True
    if not success:
      levelToLoad = self._defaultLevels[0]
    self.loadMyLevel(levelToLoad)
    self._levelName = levelName
    return success

  def turnLeft(self):
    newOrientation = abs((self.playerOrientation - 1) % 4)
    self._animateMove('left', newOrientation)
    self.playerOrientation = newOrientation

  def turnRight(self):
    newOrientation = abs((self.playerOrientation + 1) % 4)
    self._animateMove('right', newOrientation)
    self.playerOrientation = newOrientation

  def _canGoIn(self, tile, side):
    tileType = self.level['tileTypes'][tile[0]]
    side = (4 + side - tile[1]) % 4 
    return 'openIn' in tileType and side in tileType['openIn']

  def _canGoOut(self, tile, side):
    tileType = self.level['tileTypes'][tile[0]]
    side = (4 + side - tile[1]) % 4 
    return 'openOut' in tileType and side in tileType['openOut']

  def _goalReached(self):
    return self.playerPosition[0] == self.level['goal']['position'][0] and self.playerPosition[1] == self.level['goal']['position'][1]

  def _completeTile(self, tile):
    if isinstance(tile, list):
      return tile
    else:
      return [tile, 0] # default values added

  def _getTile(self, position):
    tile = self.level['tiles'][position[1]][position[0]]
    return self._completeTile(tile)

  def _getNewPosition(self, direction):
    newPosition = None
    if direction == 0:
      if self.playerPosition[1] > 0:
        newPosition = [self.playerPosition[0],self.playerPosition[1] - 1]
    elif direction == 1:
      if self.playerPosition[0] < len(self.level['tiles'][self.playerPosition[1]]) - 1:
        newPosition = [self.playerPosition[0] + 1,self.playerPosition[1]]    
    elif direction == 2:
      if self.playerPosition[1] < len(self.level['tiles']) - 1:
        newPosition = [self.playerPosition[0],self.playerPosition[1] + 1]    
    elif direction == 3:
      if self.playerPosition[0] > 0:
        newPosition = [self.playerPosition[0] - 1,self.playerPosition[1]]
    return newPosition

  def moveForward(self):
    moved = False
    newPosition = self._getNewPosition(self.playerOrientation)
    currentTile = self._getTile(self.playerPosition)
    newTile = self._getTile(newPosition)
    sideGoIn = (self.playerOrientation + 2) % 4
    if self._canGoOut(currentTile, self.playerOrientation) and self._canGoIn(newTile, sideGoIn):
      self._animateMove('forward', newPosition)
      self.playerPosition = newPosition
      moved = True
      if self._goalReached():
        self.goalReached = True
    else:
      self._animateMove('blocked', newPosition)
    return moved

  def pickItem(self):
    pass

  def useItem(self, item):
    pass

  def canPass(self, direction = 0):
    newPosition = self._getNewPosition(direction)
    currentTile = self._getTile(self.playerPosition)
    if newPosition is None:
      return False
    newTile = self._getTile(newPosition)
    sideGoIn = (direction + 2) % 4
    return self._canGoOut(currentTile, direction) and self._canGoIn(newTile, sideGoIn)

  def checkCloseEvent(self,event):
    if event.type == pygame.QUIT:
      sys.exit()    

  def _defaultHandler(self, events):
    for event in events: 
      self.checkCloseEvent(event)

  def wait(self, handler = False):
    cycle = 0
    while True:
      events = pygame.event.get() # get latest events
      if callable(handler):
        handler(events)
      self._defaultHandler(events)
      if len(events) > 0:                       # events happened?
        cycle = 0                               # stay awake and alert
      cycle += 1                                # prepare for sleep
      if cycle > self._eventActiveCycles:       # after 30 cycles 
        pygame.time.delay(self._eventSleepTime) # go asleep for 300 milliseconds, give the processor some rest
        cycle = 0                               # wake up for events during sleep

  def _operator(self, instructions):
    for instruction in instructions:
      if instruction.type == pygame.KEYDOWN:
          if instruction.key == pygame.K_RIGHT:
            toRight = self.playerOrientation == Directions.up
            while self.playerOrientation != Directions.right:
              if toRight: self.turnRight() 
              else: self.turnLeft()
            self.moveForward()

          elif instruction.key == pygame.K_LEFT:
            toRight = self.playerOrientation == Directions.down
            while self.playerOrientation != Directions.left:
              if toRight: self.turnRight() 
              else: self.turnLeft()
            self.moveForward()            

          elif instruction.key == pygame.K_UP:
            toRight = self.playerOrientation == Directions.left
            while self.playerOrientation != Directions.up:
              if toRight: self.turnRight() 
              else: self.turnLeft()
            self.moveForward()            

          elif instruction.key == pygame.K_DOWN:
            toRight = self.playerOrientation == Directions.right
            while self.playerOrientation != Directions.down:
              if toRight: self.turnRight() 
              else: self.turnLeft()
            self.moveForward()            

  def operate(self):
    self.wait(self._operator)

plane = Plane('level 1')

plane.speed = 5 
plane.turnLeft()
plane.moveForward()
plane.moveForward()
plane.moveForward()
plane.operate()
# plane.turnRight()
# plane.moveForward()
# plane.turnRight()

# plane.moveForward()

# plane.turnRight()
# plane.moveForward()

for d in range(4):
  print(plane.canPass(d))


plane.wait()

