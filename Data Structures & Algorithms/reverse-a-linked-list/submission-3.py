# Definition for singly-linked list.
# class ListNode:
#     def __init__(self, val=0, next=None):
#         self.val = val
#         self.next = next

class Solution:
    def reverseList(self, head: Optional[ListNode]) -> Optional[ListNode]:
        if not head:
            return None

        # brute force solution 
        # Time: O(N)
        # Space: O(N)

        # values = []

        # while head:
        #     values.append(head.val)
        #     head = head.next
        
        # values.reverse()

        # head = ListNode()
        # tail = ListNode()

        # for idx in range(len(values)):
        #     new_node = ListNode(values[idx])

        #     if idx == 0:
        #         head = new_node

        #     tail.next = new_node
        #     tail = tail.next
        
        # return head


        # Optimized version 

        # Time: O(N)
        # Space: O(1)

        # prev = None
        # cur = head
        # next_node = ListNode()

        # while next_node:
        #     next_node = cur.next
        #     cur.next = prev
        #     prev = cur
        #     cur = next_node
            
        # return prev


        # recursion
        # Time: O(N)
        # Space: O(N)
        if not head or not head.next:
            return head


        new_head = self.reverseList(head.next)

        cur = new_head
        while cur.next:
            cur = cur.next
        cur.next = head
        head.next = None

        return new_head


        

        
            
        
