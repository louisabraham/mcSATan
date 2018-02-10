from heapq import heappush, heappop
from .. import logger


class PriorityQ():
    def __init__(self):
        self.heapq = []
        self.contents = set()

    def push(self, elem, priority):
        logger.debug('PQ.push\n'
                     '\telem: %s\n'
                     '\theapq: %s\n'
                     '\tcontents: %s\n', elem, self.heapq, self.contents)
        self.contents.add(elem)
        heappush(self.heapq, (priority, elem))

    def remove(self, elem):
        logger.debug('PQ.remove\n'
                     '\telem: %s\n'
                     '\theapq: %s\n'
                     '\tcontents: %s\n', elem, self.heapq, self.contents)

        if elem in self.contents:
            self.contents.remove(elem)

    def pop(self):
        _, ans = heappop(self.heapq)
        while not ans in self.contents:
            _, ans = heappop(self.heapq)
        self.contents.remove(ans)
        return ans

    def __len__(self):
        return len(self.contents)

    def __repr_(self):
        return '%s(%r)' % (self.__name__, self.heapq)


class MaxPriorityQ(PriorityQ):

    def push(self, elem, priority):
        super().push(elem, -priority)
