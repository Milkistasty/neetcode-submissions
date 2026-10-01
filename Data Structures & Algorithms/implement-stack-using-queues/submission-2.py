class MyStack:

    # using one queue
    # Time: O(1) for init and pop, O(n) for push
    # Space: O(n)

    # def __init__(self):
    #     self.queue = deque([])

    # def push(self, x: int) -> None:
    #     self.queue.appendleft(x)

    #     # same as 
    #     # self.q.append(x)
    #     # for _ in range(len(self.q) - 1):
    #         # self.q.append(self.q.popleft())

    # def pop(self) -> int:
    #     return self.queue.popleft()

    # def top(self) -> int:
    #     return self.queue[0]

    # def empty(self) -> bool:
    #     return True if not self.queue else False
    
    # queue of queues
    # Time: O(1) for init, pop, push
    # Space: O(n)

    def __init__(self):
        self.q = None

    def push(self, x: int) -> None:
        self.q = deque([x, self.q])

    def pop(self) -> int:
        top = self.q.popleft()
        self.q = self.q.popleft()
        return top

    def top(self) -> int:
        return self.q[0]

    def empty(self) -> bool:
        return not self.q    


# Your MyStack object will be instantiated and called as such:
# obj = MyStack()
# obj.push(x)
# param_2 = obj.pop()
# param_3 = obj.top()
# param_4 = obj.empty()