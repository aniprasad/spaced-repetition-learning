# Tree Traversals - Iterative DFS Solutions

This guide covers iterative implementations of depth-first search (DFS) tree traversals using stacks, providing both C++ and Python examples for each traversal type.

## 🎯 Why Iterative Over Recursive?

- **Memory Control:** Explicit stack management vs. call stack
- **Stack Overflow Prevention:** Better for deep trees
- **Debugging:** Easier to trace and modify execution
- **Interview Preference:** Often asked as follow-up to recursive solutions

## 📋 Tree Node Definition

### **C++**
```cpp
struct TreeNode {
    int val;
    TreeNode *left;
    TreeNode *right;
    TreeNode() : val(0), left(nullptr), right(nullptr) {}
    TreeNode(int x) : val(x), left(nullptr), right(nullptr) {}
    TreeNode(int x, TreeNode *left, TreeNode *right) : val(x), left(left), right(right) {}
};
```

### **Python**
```python
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right
```

---

## 🌟 Pre-order Traversal (Root → Left → Right)

**Use Cases:** Tree copying, prefix expressions, serialization

### **C++ Implementation**
```cpp
vector<int> preorderTraversal(TreeNode* root) {
    vector<int> result;
    if (!root) return result;
    
    stack<TreeNode*> stk;
    stk.push(root);
    
    while (!stk.empty()) {
        TreeNode* node = stk.top();
        stk.pop();
        
        result.push_back(node->val);
        
        // Push right first so left is processed first
        if (node->right) stk.push(node->right);
        if (node->left) stk.push(node->left);
    }
    
    return result;
}
```

### **Python Implementation**
```python
def preorder_traversal(root):
    if not root:
        return []
    
    result = []
    stack = [root]
    
    while stack:
        node = stack.pop()
        result.append(node.val)
        
        # Push right first so left is processed first
        if node.right:
            stack.append(node.right)
        if node.left:
            stack.append(node.left)
    
    return result
```

---

## 🌿 In-order Traversal (Left → Root → Right)

**Use Cases:** BST sorted output, expression evaluation

### **C++ Implementation**
```cpp
vector<int> inorderTraversal(TreeNode* root) {
    vector<int> result;
    stack<TreeNode*> stk;
    TreeNode* current = root;
    
    while (current || !stk.empty()) {
        // Go to leftmost node
        while (current) {
            stk.push(current);
            current = current->left;
        }
        
        // Process current node
        current = stk.top();
        stk.pop();
        result.push_back(current->val);
        
        // Move to right subtree
        current = current->right;
    }
    
    return result;
}
```

### **Python Implementation**
```python
def inorder_traversal(root):
    result = []
    stack = []
    current = root
    
    while stack or current:
        # Go to leftmost node
        while current:
            stack.append(current)
            current = current.left
        
        # Process current node
        current = stack.pop()
        result.append(current.val)
        
        # Move to right subtree
        current = current.right
    
    return result
```

---

## 🍂 Post-order Traversal (Left → Right → Root)

**Use Cases:** Tree deletion, postfix expressions, calculating directory sizes

### **C++ Implementation (Two Stacks)**
```cpp
vector<int> postorderTraversal(TreeNode* root) {
    vector<int> result;
    if (!root) return result;
    
    stack<TreeNode*> stk1, stk2;
    stk1.push(root);
    
    while (!stk1.empty()) {
        TreeNode* node = stk1.top();
        stk1.pop();
        stk2.push(node);
        
        if (node->left) stk1.push(node->left);
        if (node->right) stk1.push(node->right);
    }
    
    while (!stk2.empty()) {
        result.push_back(stk2.top()->val);
        stk2.pop();
    }
    
    return result;
}
```

### **Python Implementation (Two Stacks)**
```python
def postorder_traversal(root):
    if not root:
        return []
    
    result = []
    stack1, stack2 = [root], []
    
    while stack1:
        node = stack1.pop()
        stack2.append(node)
        
        if node.left:
            stack1.append(node.left)
        if node.right:
            stack1.append(node.right)
    
    while stack2:
        result.append(stack2.pop().val)
    
    return result
```

### **C++ Implementation (Single Stack with Last Visited)**
```cpp
vector<int> postorderTraversal(TreeNode* root) {
    vector<int> result;
    if (!root) return result;
    
    stack<TreeNode*> stk;
    TreeNode* current = root;
    TreeNode* lastVisited = nullptr;
    
    while (current || !stk.empty()) {
        if (current) {
            stk.push(current);
            current = current->left;
        } else {
            TreeNode* peekNode = stk.top();
            
            if (peekNode->right && lastVisited != peekNode->right) {
                current = peekNode->right;
            } else {
                result.push_back(peekNode->val);
                lastVisited = stk.top();
                stk.pop();
            }
        }
    }
    
    return result;
}
```

### **Python Implementation (Single Stack with Last Visited)**
```python
def postorder_traversal(root):
    if not root:
        return []
    
    result = []
    stack = []
    current = root
    last_visited = None
    
    while stack or current:
        if current:
            stack.append(current)
            current = current.left
        else:
            peek_node = stack[-1]
            
            if peek_node.right and last_visited != peek_node.right:
                current = peek_node.right
            else:
                result.append(peek_node.val)
                last_visited = stack.pop()
    
    return result
```

---

## 🚀 Advanced Patterns & Optimizations

### **Morris Traversal (O(1) Space)**
For in-order traversal without using a stack:

#### **C++ Implementation**
```cpp
vector<int> morrisInorder(TreeNode* root) {
    vector<int> result;
    TreeNode* current = root;
    
    while (current) {
        if (!current->left) {
            // No left subtree, visit current and go right
            result.push_back(current->val);
            current = current->right;
        } else {
            // Find inorder predecessor (rightmost node in left subtree)
            TreeNode* predecessor = current->left;
            while (predecessor->right && predecessor->right != current) {
                predecessor = predecessor->right;
            }
            
            if (!predecessor->right) {
                // Create thread: predecessor -> current
                predecessor->right = current;
                current = current->left;
            } else {
                // Thread exists, remove it and visit current
                predecessor->right = nullptr;
                result.push_back(current->val);
                current = current->right;
            }
        }
    }
    
    return result;
}
```

#### **Python Implementation**
```python
def morris_inorder(root):
    result = []
    current = root
    
    while current:
        if not current.left:
            result.append(current.val)
            current = current.right
        else:
            # Find inorder predecessor
            predecessor = current.left
            while predecessor.right and predecessor.right != current:
                predecessor = predecessor.right
            
            if not predecessor.right:
                # Create thread
                predecessor.right = current
                current = current.left
            else:
                # Remove thread and visit
                predecessor.right = None
                result.append(current.val)
                current = current.right
    
    return result
```

### **Unified Iterative Template**
A general pattern that works for all traversals:

```cpp
vector<int> traversal(TreeNode* root, string order) {
    vector<int> result;
    if (!root) return result;
    
    stack<pair<TreeNode*, bool>> stk;
    stk.push({root, false});
    
    while (!stk.empty()) {
        auto [node, visited] = stk.top();
        stk.pop();
        
        if (!node) continue;
        
        if (visited) {
            result.push_back(node->val);
        } else {
            if (order == "post") {
                stk.push({node, true});
                stk.push({node->right, false});
                stk.push({node->left, false});
            } else if (order == "in") {
                stk.push({node->right, false});
                stk.push({node, true});
                stk.push({node->left, false});
            } else { // preorder
                stk.push({node->right, false});
                stk.push({node->left, false});
                stk.push({node, true});
            }
        }
    }
    
    return result;
}
```

---

## 🎯 Key Takeaways

### **Pattern Recognition**
- **Pre-order:** Process root immediately, simple stack approach
- **In-order:** Need to track current position, go left first
- **Post-order:** Most complex, need to ensure children processed first

### **Common Mistakes**
- **Wrong push order:** Remember stack is LIFO
- **Missing null checks:** Always validate before dereferencing
- **Infinite loops:** Ensure proper traversal state management

### **Complexity Analysis**
- **Time:** `O(n)` for all traversals
- **Space:** `O(h)` where h is tree height (worst case O(n))

### **When to Use Each**
- **Pre-order:** Tree copying, prefix notation
- **In-order:** BST operations, sorted output
- **Post-order:** Tree deletion, postfix notation, size calculations

---

*Practice these patterns with different tree structures to build muscle memory for the stack manipulations!*