from Plain import Plain

plain = Plain('level 1')

plain.speed = 5 
plain.turnLeft()
plain.moveForward()
plain.moveForward()
plain.moveForward()
plain.operate()
# plain.turnRight()
# plain.moveForward()
# plain.turnRight()

# plain.moveForward()

# plain.turnRight()
# plain.moveForward()

for d in range(4):
  print(plain.canPass(d))


plain.wait()
