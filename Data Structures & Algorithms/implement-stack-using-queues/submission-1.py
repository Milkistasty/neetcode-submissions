class MyStack:

    # Time: O(1) for init and pop, O(n) for push
    # Space: O(n)

    def __init__(self):
        self.queue = deque([])

    def push(self, x: int) -> None:
        self.queue.appendleft(x)

        # same as 
        # self.q.append(x)
        # for _ in range(len(self.q) - 1):
            # self.q.append(self.q.popleft())

    def pop(self) -> int:
        return self.queue.popleft()

    def top(self) -> int:
        return self.queue[0]

    def empty(self) -> bool:
        return True if not self.queue else False
        


# Your MyStack object will be instantiated and called as such:
# obj = MyStack()
# obj.push(x)
# param_2 = obj.pop()
# param_3 = obj.top()
# param_4 = obj.empty()