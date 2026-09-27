class Solution:
    def isValid(self, s: str) -> bool:
        if len(s) % 2 != 0  :
            return False
        
        p_map = {
            "]": "[", 
            "}": "{", 
            ")": "("
        }
        
        stack = []

        for ch in s:

            print("stack: ", stack)
            # print("p_map[ch]: ", p_map[ch])
            
            # if stack: 
            if stack and (ch in p_map) and stack[-1] == p_map[ch]:
                stack.pop()
            else:
                stack.append(ch)
        
        return False if stack else True

