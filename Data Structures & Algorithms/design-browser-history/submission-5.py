class ListNode:
    def __init__(self, val, prev=None, next=None):
        self.val = val
        self.next = next
        self.prev = prev

class BrowserHistory:

    # Doubly Linkedin List
    # Time: O(1) for init, visit
    # Time: O(min(n, steps)) for backward, forward
    # Space: O(m * n), n = number of visited urls, m = avg len of each url  

    def __init__(self, homepage: str):
        self.current = ListNode(homepage)

    def visit(self, url: str) -> None:
        self.current.next = ListNode(url, self.current)
        self.current = self.current.next

    def back(self, steps: int) -> str:
        while self.current.prev and steps > 0:
            self.current = self.current.prev
            steps -= 1
        
        return self.current.val

    def forward(self, steps: int) -> str:
        while self.current.next and steps > 0:
            self.current = self.current.next
            steps -= 1
        
        return self.current.val

    # Optimimal dynamic array method
    # Time: O(1) for init, visit, backward, forward
    # Space: O(m * n), n = number of visited urls, m = avg len of each url  

    # class BrowserHistory:

    # def __init__(self, homepage: str):
    #     self.history = [homepage]
    #     self.cur = 0
    #     self.n = 1

    # def visit(self, url: str) -> None:
    #     self.cur += 1
    #     if self.cur == len(self.history):
    #         self.history.append(url)
    #         self.n += 1
    #     else:
    #         self.history[self.cur] = url
    #         self.n = self.cur + 1

    # def back(self, steps: int) -> str:
    #     self.cur = max(0, self.cur - steps)
    #     return self.history[self.cur]

    # def forward(self, steps: int) -> str:
    #     self.cur = min(self.n - 1, self.cur + steps)
    #     return self.history[self.cur]

# Your BrowserHistory object will be instantiated and called as such:
# obj = BrowserHistory(homepage)
# obj.visit(url)
# param_2 = obj.back(steps)
# param_3 = obj.forward(steps)`