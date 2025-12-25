# Tree Algorithms & Patterns

This section covers essential tree algorithms, focusing on different traversal methods, binary search tree operations, and common tree problem patterns.

## 📚 Contents

- **[Tree Traversals](./traversals.md)** - Complete guide to DFS traversals (recursive & iterative)
- **[Binary Search Trees](./binary-search-tree.md)** - BST validation, insertion, deletion
- **[Path Problems](./path-problems.md)** - Path sum, diameter, lowest common ancestor
- **[Tree Construction](./construction.md)** - Building trees from different inputs

## 🌳 Key Tree Concepts

### **Tree Traversal Orders**
- **Pre-order:** Root → Left → Right (good for copying/serialization)
- **In-order:** Left → Root → Right (gives sorted order for BST)
- **Post-order:** Left → Right → Root (good for deletion/cleanup)

### **Common Patterns**
- **Level Order (BFS):** Use queue, process level by level
- **Path Tracking:** DFS with running sum, backtrack when needed
- **Tree Validation:** In-order for BST, recursive bounds checking
- **Tree Modification:** Often easier with post-order traversal

### **Space-Time Complexities**
- **Recursive DFS:** `O(n) time, O(h) space` where h = height
- **Iterative DFS:** `O(n) time, O(h) space` for stack
- **Morris Traversal:** `O(n) time, O(1) space` using threading
- **Level Order:** `O(n) time, O(w) space` where w = max width

## 🎯 Problem Categories

### **Traversal Problems**
- Binary Tree Inorder/Preorder/Postorder Traversal
- Binary Tree Level Order Traversal
- Binary Tree Zigzag Level Order Traversal

### **Search & Validation**
- Validate Binary Search Tree
- Search in a Binary Search Tree
- Lowest Common Ancestor

### **Path & Sum Problems**
- Binary Tree Maximum Path Sum
- Path Sum II
- Binary Tree Diameter

### **Construction & Modification**
- Construct Binary Tree from Preorder and Inorder
- Flatten Binary Tree to Linked List
- Invert Binary Tree

---

*Start with [Tree Traversals](./traversals.md) for fundamental iterative DFS patterns!*