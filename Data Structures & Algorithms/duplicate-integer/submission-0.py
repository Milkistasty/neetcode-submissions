from collections import Counter

class Solution:
    def hasDuplicate(self, nums: List[int]) -> bool:
        if len(nums) == 0: return False

        cnt = Counter(nums)

        for occ in cnt.values():
            if occ > 1:
                return True
        return False