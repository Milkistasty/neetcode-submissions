class Solution:
    def calPoints(self, operations: List[str]) -> int:
        
        # record: list[int] = []

        # if not operations:
        #     return 0

        # for i in range(len(operations)):
        #     if operations[i] not in ['+', 'D', 'C']:
        #         record.append(int(operations[i]))
        #     elif operations[i] == '+':
        #         record.append(int(record[-1]) + int(record[-2]))
        #     elif operations[i] == 'D':
        #         record.append(int(record[-1]) * 2)
        #     elif operations[i] == 'C':
        #         record.pop()

        # return sum(record)

        stack = []

        if not operations:
            return 0 

        for o in operations:
            if o == '+':
                stack.append(stack[-1] + stack[-2])
            elif o == 'D':
                stack.append(stack[-1] * 2)
            elif o == 'C':
                stack.pop()
            else:
                stack.append(int(o))
        
        return sum(stack)