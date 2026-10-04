# Definition for singly-linked list.
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

# class Solution:    
#     def mergeKLists(self, lists: List[Optional[ListNode]]) -> Optional[ListNode]:
#         if not lists:
#             return None
        
        # Brute Force 
        # convert all nodes to lists, sort, and convert them back to listnode
        # Time: O(nlogn)
        # Space: O(n)

        # nodes = []
        # for lst in lists:
        #     while lst:
        #         nodes.append(lst.val)
        #         lst = lst.next
        # nodes.sort()

        # res = ListNode(0)
        # cur = res
        # for node in nodes:
        #     cur.next = ListNode(node)
        #     cur = cur.next
        # return res.next


        # single linked list
        # Time: O(k * n), k lists, n total nodes
        # Space: O (n) for the output list

        # dummy = ListNode(0)
        # tail = dummy
        
        # while any(lists):
        #     smallest_val = None
        #     smallest_node = None

        #     for i in range(len(lists)):
        #         if lists[i] is not None:
        #             if smallest_val is None or lists[i].val < smallest_val:
        #                 smallest_val = lists[i].val
        #                 smallest_node = i

        #     node = lists[smallest_node]

        #     tail.next = node
        #     tail = tail.next

        #     lists[smallest_node] = node.next
        
        # return dummy.next


# Heap 
# Time: O(nlogk)
# Space: O(k)
# class NodeWrapper:
#     def __init__(self, node):
#         self.node = node

#     def __lt__(self, other):
#         return self.node.val < other.node.val

# class Solution:
#     def mergeKLists(self, lists: List[Optional[ListNode]]) -> Optional[ListNode]:
#         if len(lists) == 0:
#             return None

#         res = ListNode(0)
#         cur = res
#         minHeap = []

#         for lst in lists:
#             if lst is not None:
#                 heapq.heappush(minHeap, NodeWrapper(lst))

#         while minHeap:
#             node_wrapper = heapq.heappop(minHeap)
#             cur.next = node_wrapper.node
#             cur = cur.next

#             if node_wrapper.node.next:
#                 heapq.heappush(minHeap, NodeWrapper(node_wrapper.node.next))

#         return res.next


# Merge sort
# Time: O(nlogk)
# Space: O(k)
class Solution:

    def mergeKLists(self, lists: List[Optional[ListNode]]) -> Optional[ListNode]:
        if not lists or len(lists) == 0:
            return None

        while len(lists) > 1:
            mergedLists = []
            for i in range(0, len(lists), 2):
                l1 = lists[i]
                l2 = lists[i + 1] if (i + 1) < len(lists) else None
                mergedLists.append(self.mergeList(l1, l2))
            lists = mergedLists
        return lists[0]

    def mergeList(self, l1, l2):
        dummy = ListNode()
        tail = dummy

        while l1 and l2:
            if l1.val < l2.val:
                tail.next = l1
                l1 = l1.next
            else:
                tail.next = l2
                l2 = l2.next
            tail = tail.next

        if l1:
            tail.next = l1
        if l2:
            tail.next = l2

        return dummy.next
        