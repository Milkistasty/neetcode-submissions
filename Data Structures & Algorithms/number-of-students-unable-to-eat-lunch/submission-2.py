# from collections.Counter import Counter

class Solution:
    def countStudents(self, students: List[int], sandwiches: List[int]) -> int:

        # brute force
        # Time: O (n * m * m), n -> number of students, m -> number of sandwiches
        # Space: O (n + m), n -> number of students, m -> number of sandwiches

        # while sandwiches and sandwiches[0] in students:
        #     if sandwiches[0] == students[0]:
        #         students = students[1:]
        #         sandwiches = sandwiches[1:]
        #     else:
        #         students = students[1:] + [students[0]]

        # return len(students)

        # count preferences and check availability
        counts = Counter(students)  # 0: occurrences, 1: occurrences
        for s in sandwiches:
            if counts[s] > 0:
                counts[s] -= 1
            else:
                break

        return sum(counts.values())



