class Solution:
    def countStudents(self, students: List[int], sandwiches: List[int]) -> int:

        # brute force
        # Time: O (n ^ 3)
        # Space: O (n)

        # while sandwiches and sandwiches[0] in students:
        #     if sandwiches[0] == students[0]:
        #         students = students[1:]
        #         sandwiches = sandwiches[1:]
        #     else:
        #         students = students[1:] + [students[0]]

        # return len(students)


        # count preferences and check availability
        # Time: O (n)
        # Space: O (1)

        counts = Counter(students)  # 0: occurrences, 1: occurrences
        for s in sandwiches:
            if counts[s] > 0:
                counts[s] -= 1
            else:
                break

        return sum(counts.values())


        # queue simulation approach
        # Time: O (n ^ 2), rotate through up to n students before finding someone wants it
        # Space: O (n), store up to n students

        # queue = deque(students)
        # rotations = 0

        # # Stop if the whole queue has rotated without anyone taking the sandwich
        # while queue and rotations < len(queue):
        #     if queue[0] == sandwiches[0]:
        #         queue.popleft()
        #         sandwiches.pop(0)
        #         rotations = 0
        #     else:
        #         queue.rotate(-1)  # same as queue.append(queue.popleft())
        #         rotations += 1
        
        # return len(queue)
        

