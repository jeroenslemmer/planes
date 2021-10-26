from Plain import Plain

level = { 'name': 'level 1', 
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
                [0,    0,    0,    0,    0,    0]],
      'player': {'img': 'sprite01.png', 'position': [1,1], 'orientation': 2}, 
      'goal': {'img':'treasure.png', 'position': [4,5]},
      'collision': {'img':'collision.png'}
    }

plain = Plain()
plain.loadMyLevel(level)

plain.wait()
