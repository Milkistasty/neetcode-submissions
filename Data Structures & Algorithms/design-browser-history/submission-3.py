class ListNode:
    def __init__(self, val):
        self.val: str = val
        self.next = None
        self.prev = None

class BrowserHistory:

    def __init__(self, homepage: str):
        self.head = ListNode(homepage)
        self.current = self.head

    def visit(self, url: str) -> None:
        visit = ListNode(url)
        self.current.next = visit
        visit.prev = self.current
        self.current = self.current.next

    def back(self, steps: int) -> str:
        while steps > 0 and self.current.prev is not None:
            self.current = self.current.prev
            steps -= 1
        
        return self.current.val

    def forward(self, steps: int) -> str:
        while steps > 0 and self.current.next is not None:
            self.current = self.current.next
            steps -= 1
        
        return self.current.val


# Your BrowserHistory object will be instantiated and called as such:
# obj = BrowserHistory(homepage)
# obj.visit(url)
# param_2 = obj.back(steps)
# param_3 = obj.forward(steps)`