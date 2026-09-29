# Definition for singly-linked list.
# class ListNode:
#     def __init__(self, val=0, next=None):
#         self.val = val
#         self.next = next

class Solution:
    def mergeTwoLists(self, list1: Optional[ListNode], list2: Optional[ListNode]) -> Optional[ListNode]:
        
        # brute force solution 
        # Time: O(N + M)
        # Space O(N)

        arr = []

        while list1:
            arr.append(list1.val)
            list1 = list1.next
        
        while list2:
            arr.append(list2.val)
            list2 = list2.next
        
        arr.sort()

        head = ListNode(0)
        cur = head

        for v in arr:
            cur.next = ListNode(v)
            cur = cur.next

        return head.next