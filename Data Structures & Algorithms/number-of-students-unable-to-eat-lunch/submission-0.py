class ListNode:
    def __init__(self, val, prev, next):
        self.val = val
        self.prev = prev
        self.next = next

class Solution:
    def countStudents(self, students: List[int], sandwiches: List[int]) -> int:
        while sandwiches and sandwiches[0] in students:
            if sandwiches[0] == students[0]:
                students = students[1:]
                sandwiches = sandwiches[1:]
            else:
                students = students[1:] + [students[0]]

        return len(students) if students else 0 

