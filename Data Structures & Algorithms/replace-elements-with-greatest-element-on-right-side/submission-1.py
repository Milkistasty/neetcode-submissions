class Solution:
    def replaceElements(self, arr: List[int]) -> List[int]:
        right_max = 0
        temp = 0
        for i in range(1, len(arr)+1, 1):
            if arr[-i] >= right_max:
                if i == 1:
                    right_max = arr[-i]
                else:
                    temp = right_max
                    right_max = arr[-i]
                    arr[-i] = temp
            else:
                arr[-i] = right_max

        
        arr[-1] = -1

        return arr


