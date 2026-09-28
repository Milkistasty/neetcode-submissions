# Definition for singly-linked list.
# class ListNode:
#     def __init__(self, val=0, next=None):
#         self.val = val
#         self.next = next

class Solution:
    def reverseList(self, head: Optional[ListNode]) -> Optional[ListNode]:
        if not head:
            return head

        # brute force solution 

        values = []

        while head:
            values.append(head.val)
            head = head.next
        
        values.reverse()

        head = ListNode()
        tail = ListNode()

        for idx in range(len(values)):
            new_node = ListNode(values[idx])

            if idx == 0:
                head = new_node

            tail.next = new_node
            tail = tail.next
        
        return head
            

        


        

        
            
        
