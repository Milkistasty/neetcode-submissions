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
        running_total = 0

        if not operations:
            return 0 

        for o in operations:
            if o == '+':
                stack.append(stack[-1] + stack[-2])
                running_total += stack[-1]
            elif o == 'D':
                stack.append(stack[-1] * 2)
                running_total += stack[-1]
            elif o == 'C':
                running_total -= stack[-1]
                stack.pop()
            else:
                stack.append(int(o))
                running_total += stack[-1]
        
        return running_total