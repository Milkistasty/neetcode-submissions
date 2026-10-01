class Solution:
    def __init__(self):
        self.cache = {}

    def climbStairs(self, n: int) -> int:

        # Cached recursion
        # Time: O(n) -> each value from n-1 down to 4 is computed at most once and stored in self.cache
        # Space: O(n) -> for the cache

        if n <= 3:
            return n
        
        if n-1 not in self.cache:
            self.cache[n-1] = self.climbStairs(n-1)

        if n-2 not in self.cache:
            self.cache[n-2] = self.climbStairs(n-2)

        return self.cache[n-1] + self.cache[n-2]