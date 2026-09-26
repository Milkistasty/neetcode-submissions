class Solution:
    def findMaxConsecutiveOnes(self, nums: List[int]) -> int:
        
        mx = 0
        best_max = 0

        for num in nums:
            if num == 1:
                mx += 1
            else:
                if mx > best_max:
                    best_max = mx

                mx = 0
            

        return max(best_max, mx)  
