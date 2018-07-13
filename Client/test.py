class M():
    def __init__(self):
        self.blocks = [1, 2, 3]
    
m = M()

blks = m.blocks

blks[0] = 0

print(m.blocks)