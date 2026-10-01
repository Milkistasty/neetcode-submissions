class ListNode:
    def __init__(self, val, prev, next):
        self.val = val
        self.prev = prev
        self.next = next

class Solution:
    def countStudents(self, students: List[int], sandwiches: List[int]) -> int:

        # brute force
        # Time: O (n * m), n -> number of students, m -> number of sandwiches
        # Space: O (n + m), n -> number of students, m -> number of sandwiches

        while sandwiches and sandwiches[0] in students:
            if sandwiches[0] == students[0]:
                students = students[1:]
                sandwiches = sandwiches[1:]
            else:
                students = students[1:] + [students[0]]

        return len(students)

